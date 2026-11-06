
import json
import hashlib
import sqlite3
import time
import threading
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from pydantic import BaseModel, ValidationError

from config import REGION, STATE


# ============================================================
# 1. BEDROCK CLIENT
# ============================================================

brt = boto3.client(
    "bedrock-runtime",
    region_name=REGION,
    config=Config(
        retries={
            "max_attempts": 12,
            "mode": "adaptive"
        },
        read_timeout=180,
        connect_timeout=15
    )
)


# ============================================================
# 2. MODEL PRICING
# ============================================================
# Prices are USD per 1,000 tokens.
#
# Keep these as None until you enter the applicable prices
# for your actual model/inference profile and pricing tier.
#
# Do not use guessed prices for the final cost report.

PRICE_PER_1K = {
    "sonnet-4-6": (0.0033, 0.0165),
    "opus-4-8": (0.0055, 0.0275),
    "haiku": (None, None),
}


def configure_price(model_family, input_price, output_price):
    """
    Configure USD price per 1,000 input/output tokens.
    """
    if input_price < 0 or output_price < 0:
        raise ValueError("Prices cannot be negative")

    PRICE_PER_1K[model_family] = (
        float(input_price),
        float(output_price)
    )


def _price_for_model(model_id):
    model_id = model_id.lower()

    for family, prices in PRICE_PER_1K.items():
        if family in model_id:
            return prices

    return None, None


# ============================================================
# 3. USAGE AND COST LEDGER
# ============================================================

class Ledger:

    def __init__(self):
        self.rows = []
        self.lock = threading.Lock()

    def add(self, model, tin, tout, ms):
        with self.lock:
            self.rows.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "model": model,
                "input_tokens": int(tin),
                "output_tokens": int(tout),
                "latency_ms": int(ms)
            })

    def total_tokens(self):
        with self.lock:
            return sum(r["input_tokens"] + r["output_tokens"]
                       for r in self.rows)

    def total_input_tokens(self):
        with self.lock:
            return sum(r["input_tokens"] for r in self.rows)

    def total_output_tokens(self):
        with self.lock:
            return sum(r["output_tokens"] for r in self.rows)

    def usd(self):
        total = 0.0
        unknown_models = set()

        with self.lock:
            rows = list(self.rows)

        for row in rows:
            pi, po = _price_for_model(row["model"])

            if pi is None or po is None:
                unknown_models.add(row["model"])
                continue

            total += (
                row["input_tokens"] / 1000 * pi
                + row["output_tokens"] / 1000 * po
            )

        return round(total, 6)

    def latency_summary(self):
        with self.lock:
            values = [r["latency_ms"] for r in self.rows]

        if not values:
            return {
                "calls": 0,
                "average_ms": 0,
                "p50_ms": 0,
                "p95_ms": 0
            }

        ordered = sorted(values)

        return {
            "calls": len(values),
            "average_ms": round(statistics.mean(values), 2),
            "p50_ms": round(
                ordered[int((len(ordered) - 1) * 0.50)], 2
            ),
            "p95_ms": round(
                ordered[int((len(ordered) - 1) * 0.95)], 2
            )
        }

    def summary(self):
        with self.lock:
            rows = list(self.rows)

        return {
            "calls": len(rows),
            "input_tokens": sum(r["input_tokens"] for r in rows),
            "output_tokens": sum(r["output_tokens"] for r in rows),
            "total_tokens": sum(
                r["input_tokens"] + r["output_tokens"]
                for r in rows
            ),
            "estimated_cost_usd": self.usd(),
            "latency": self.latency_summary(),
            "models_used": sorted(set(r["model"] for r in rows))
        }

    def to_list(self):
        with self.lock:
            return list(self.rows)


LEDGER = Ledger()


# ============================================================
# 4. SQLITE RESPONSE CACHE
# ============================================================

CACHE_PATH = Path(STATE) / "llm_cache.sqlite"
CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)

_cache_lock = threading.Lock()

_cache = sqlite3.connect(
    str(CACHE_PATH),
    check_same_thread=False
)

_cache.execute("""
    CREATE TABLE IF NOT EXISTS c (
        k TEXT PRIMARY KEY,
        v TEXT NOT NULL,
        created_at TEXT
    )
""")

_cache.commit()


def _cache_get(key):

    with _cache_lock:
        row = _cache.execute(
            "SELECT v FROM c WHERE k = ?",
            (key,)
        ).fetchone()

    return row[0] if row else None


def _cache_set(key, value):

    with _cache_lock:
        _cache.execute(
            """
            INSERT OR REPLACE INTO c (k, v, created_at)
            VALUES (?, ?, ?)
            """,
            (
                key,
                value,
                datetime.now(timezone.utc).isoformat()
            )
        )

        _cache.commit()


def cache_stats():

    with _cache_lock:
        count = _cache.execute(
            "SELECT COUNT(*) FROM c"
        ).fetchone()[0]

    return {
        "cache_path": str(CACHE_PATH),
        "cached_responses": count
    }


# ============================================================
# 5. TEMPERATURE COMPATIBILITY
# ============================================================

_no_temperature = set()


# ============================================================
# 6. BEDROCK CHAT
# ============================================================

def chat(
    model_id,
    system,
    user,
    max_tokens=1500,
    temperature=0.0,
    use_cache=True
):
    """
    Central Bedrock Converse wrapper.

    Features:
      - Explicit region
      - Adaptive SDK retries
      - SQLite response cache
      - Token accounting
      - Latency accounting
      - Temperature compatibility retry
    """

    cache_payload = json.dumps(
        [
            model_id,
            system,
            user,
            max_tokens,
            temperature
        ],
        sort_keys=True
    )

    key = hashlib.sha256(
        cache_payload.encode("utf-8")
    ).hexdigest()

    # --------------------------------------------------------
    # CACHE LOOKUP
    # --------------------------------------------------------

    if use_cache:
        cached = _cache_get(key)

        if cached is not None:
            return cached

    # --------------------------------------------------------
    # REQUEST CONFIGURATION
    # --------------------------------------------------------

    inference_config = {
        "maxTokens": max_tokens
    }

    if model_id not in _no_temperature:
        inference_config["temperature"] = temperature

    # --------------------------------------------------------
    # BEDROCK CALL
    # --------------------------------------------------------

    start = time.perf_counter()

    try:

        response = brt.converse(
            modelId=model_id,
            system=[
                {"text": system}
            ],
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"text": user}
                    ]
                }
            ],
            inferenceConfig=inference_config
        )

    except ClientError as exc:

        message = str(exc).lower()

        # Some models reject the temperature parameter.
        # Remember this for future calls and retry once
        # without temperature.

        if (
            "temperature" in message
            and model_id not in _no_temperature
        ):

            _no_temperature.add(model_id)

            return chat(
                model_id=model_id,
                system=system,
                user=user,
                max_tokens=max_tokens,
                temperature=temperature,
                use_cache=use_cache
            )

        raise

    latency_ms = int(
        (time.perf_counter() - start) * 1000
    )

    # --------------------------------------------------------
    # RESPONSE EXTRACTION
    # --------------------------------------------------------

    response_text = response["output"]["message"]["content"][0]["text"]

    usage = response.get("usage", {})

    input_tokens = usage.get("inputTokens", 0)
    output_tokens = usage.get("outputTokens", 0)

    # --------------------------------------------------------
    # LEDGER UPDATE
    # --------------------------------------------------------

    LEDGER.add(
        model=model_id,
        tin=input_tokens,
        tout=output_tokens,
        ms=latency_ms
    )

    # --------------------------------------------------------
    # CACHE SAVE
    # --------------------------------------------------------

    if use_cache:
        _cache_set(key, response_text)

    return response_text


# ============================================================
# 7. STRUCTURED JSON OUTPUT WITH PYDANTIC VALIDATION
# ============================================================

def chat_json(
    model_id,
    system,
    user,
    schema: type[BaseModel],
    **kwargs
):
    """
    Requests JSON from the model and validates it using
    Pydantic.

    The model gets one repair attempt if its first response
    is invalid.
    """

    json_system = (
        system
        + "\n\nReturn ONLY one valid JSON object. "
          "Do not include markdown fences or prose."
    )

    raw = chat(
        model_id=model_id,
        system=json_system,
        user=user,
        **kwargs
    )

    for attempt in range(2):

        try:

            start = raw.find("{")
            end = raw.rfind("}")

            if start == -1 or end == -1 or end < start:
                raise ValueError("No JSON object found")

            blob = raw[start:end + 1]

            return schema.model_validate_json(blob)

        except (ValueError, ValidationError) as exc:

            if attempt == 1:
                raise

            repair_user = (
                user
                + "\n\nYour previous response was invalid."
                + f"\nValidation error: {str(exc)}"
                + "\nReturn valid JSON matching this schema:"
                + json.dumps(schema.model_json_schema(), indent=2)
            )

            raw = chat(
                model_id=model_id,
                system=json_system,
                user=repair_user,
                use_cache=False,
                **kwargs
            )


# ============================================================
# 8. REPORTING HELPERS
# ============================================================

def get_usage_report():

    return {
        "ledger": LEDGER.summary(),
        "cache": cache_stats(),
        "models_without_temperature": sorted(_no_temperature)
    }


def reset_ledger():
    """
    Clears in-memory metrics only.
    Does NOT delete the SQLite response cache.
    """
    with LEDGER.lock:
        LEDGER.rows.clear()
