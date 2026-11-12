import re

from .agents.state import CIQState

PII = [
    (re.compile(r"\\b\\d{3}-\\d{2}-\\d{4}\\b"), "[SSN]"),
    (re.compile(r"\\b(?:\\d[ -]?){13,19}\\b"), "[CARD_OR_ACCOUNT]"),
    (re.compile(r"[\\w.+-]+@[\\w-]+\\.[\\w.]+"), "[EMAIL]"),
    (re.compile(r"\\(?\\b\\d{3}\\)?[ .-]?\\d{3}[ .-]?\\d{4}\\b"), "[PHONE]"),
]

INJECTION = re.compile(
    r"ignore\\s+(all|any|previous|your)\\s+(instructions|rules)"
    r"|system prompt|you are now|developer mode",
    re.IGNORECASE,
)

def guard_node(state: CIQState) -> dict:
    raw = state.get("request", "")
    text = raw[:8000]

    for pattern, replacement in PII:
        text = pattern.sub(replacement, text)

    flags = []
    if len(raw) > 8000:
        flags.append("request_truncated")
    if INJECTION.search(text):
        flags.append("possible_prompt_injection")

    return {
        "clean_request": text,
        "flags": flags,
        "revisions": 0,
        "trace": [{"node": "guard", "flags": flags}],
    }
