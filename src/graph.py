import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from langgraph.graph import StateGraph, START, END

from .agents.state import CIQState
from .guards import guard_node
from .agents.router import router_node, route_intent
from .agents.triage import triage_node
from .agents.analyst import analyst_node
from .agents.research import cases_node, research_node
from .agents.drafter import drafter_node
from .agents.critic import critic_node
from .agents.human import human_node, refuse_node


def after_analyst(state: CIQState) -> str:
    intent = state.get("intent")

    if intent == "BRIEF":
        return "research"

    if intent == "ANALYTICS":
        return "drafter"

    raise ValueError(f"Unexpected intent after analyst: {intent}")


def after_critic(state: CIQState) -> str:
    critique = state.get("critique", {})
    passed = critique.get("pass", False)
    revisions = state.get("revisions", 0)
    intent = state.get("intent")

    if not passed:
        if revisions < 2:
            return "drafter"
        return "human"

    if intent in {"TRIAGE", "BRIEF"}:
        return "human"

    return "publish"


def after_human(state: CIQState):
    action = state.get("human_decision", {}).get("action")

    if action in {"approve", "edit"}:
        return "publish"

    return END


def _publish_runtime():
    import boto3
    from botocore.exceptions import ClientError

    root = Path(__file__).resolve().parent
    models = json.loads(
        (root / "models.json").read_text(encoding="utf-8")
    )

    region = "us-east-1"
    sts = boto3.client("sts", region_name=region)
    account = sts.get_caller_identity()["Account"]

    bucket = f"sagemaker-complaintiq-{account}"
    s3 = boto3.client("s3", region_name=region)

    return models, bucket, s3, ClientError


def get_usage_snapshot():
    try:
        import llm
        return llm.get_usage_report()
    except Exception as exc:
        return {"usage_report_error": str(exc)}


def append_audit_record(record, bucket, s3, ClientError):
    audit_key = "complaintiq/reports/audit.jsonl"

    try:
        existing = s3.get_object(
            Bucket=bucket,
            Key=audit_key,
        )["Body"].read().decode("utf-8")
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code")

        if code not in {"NoSuchKey", "404", "NotFound"}:
            raise

        existing = ""

    line = json.dumps(record, default=str) + "\n"

    s3.put_object(
        Bucket=bucket,
        Key=audit_key,
        Body=(existing + line).encode("utf-8"),
        ContentType="application/x-ndjson",
    )


def publish_node(state, config=None):
    decision = state.get("human_decision", {})
    action = decision.get("action")

    if action not in {"approve", "edit"}:
        raise ValueError(
            "Publishing requires a human approve or edit decision."
        )

    draft = state.get("draft", "").strip()

    if not draft:
        raise ValueError("Cannot publish an empty draft.")

    configurable = (config or {}).get("configurable", {})

    thread_id = (
        configurable.get("thread_id")
        or state.get("thread_id")
        or f"complaintiq-{uuid.uuid4().hex[:12]}"
    )

    # AWS identity lookup and S3 client initialization occur only
    # when this publish function is actually invoked.
    models, bucket, s3, ClientError = _publish_runtime()

    publishing_event = {
        "node": "publish",
        "status": "publishing",
        "thread_id": thread_id,
    }

    report_trace = list(state.get("trace", [])) + [publishing_event]

    report = (
        "# ComplaintIQ — Approved Report\n\n"
        f"**Thread ID:** `{thread_id}`\n\n"
        f"**Intent:** `{state.get('intent', 'UNKNOWN')}`\n\n"
        f"**Human action:** `{action}`\n\n"
        "---\n\n"
        "## Report\n\n"
        f"{draft}\n\n"
        "---\n\n"
        "## Execution Trace\n\n"
        "```json\n"
        f"{json.dumps(report_trace, indent=2, default=str)}\n"
        "```\n"
    )

    report_key = f"complaintiq/reports/{thread_id}.md"

    s3.put_object(
        Bucket=bucket,
        Key=report_key,
        Body=report.encode("utf-8"),
        ContentType="text/markdown",
    )

    report_uri = f"s3://{bucket}/{report_key}"
    usage = get_usage_snapshot()

    audit_record = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "thread_id": thread_id,
        "intent": state.get("intent"),
        "models_used": [
            models.get("worker"),
            models.get("judge"),
        ],
        "usage": usage,
        "critic_verdict": state.get("critique", {}).get("verdict"),
        "critic_pass": state.get("critique", {}).get("pass"),
        "human_action": action,
        "report_s3_uri": report_uri,
    }

    append_audit_record(audit_record, bucket, s3, ClientError)

    return {
        "report_uri": report_uri,
        "trace": [
            publishing_event,
            {
                "node": "publish",
                "status": "published",
                "report_uri": report_uri,
            },
        ],
    }


def build_graph(checkpointer=None):
    """Build the graph without opening or creating any checkpoint database."""

    g = StateGraph(CIQState)

    nodes = {
        "guard": guard_node,
        "router": router_node,
        "triage": triage_node,
        "cases": cases_node,
        "analyst": analyst_node,
        "research": research_node,
        "drafter": drafter_node,
        "critic": critic_node,
        "human": human_node,
        "publish": publish_node,
        "refuse": refuse_node,
    }

    for name, fn in nodes.items():
        g.add_node(name, fn)

    g.add_edge(START, "guard")
    g.add_edge("guard", "router")

    g.add_conditional_edges(
        "router",
        route_intent,
        {
            "TRIAGE": "triage",
            "ANALYTICS": "analyst",
            "BRIEF": "analyst",
            "REG_QA": "research",
            "OUT_OF_SCOPE": "refuse",
        },
    )

    g.add_edge("triage", "cases")
    g.add_edge("cases", "research")

    g.add_conditional_edges(
        "analyst",
        after_analyst,
        {
            "research": "research",
            "drafter": "drafter",
        },
    )

    g.add_edge("research", "drafter")
    g.add_edge("drafter", "critic")

    g.add_conditional_edges(
        "critic",
        after_critic,
        {
            "drafter": "drafter",
            "human": "human",
            "publish": "publish",
        },
    )

    g.add_conditional_edges(
        "human",
        after_human,
        {
            "publish": "publish",
            END: END,
        },
    )

    g.add_edge("publish", END)
    g.add_edge("refuse", END)

    return g


def compile_graph(checkpointer=None):
    """Compile only when explicitly requested by the caller."""
    return build_graph(checkpointer=checkpointer).compile(
        checkpointer=checkpointer
    )
