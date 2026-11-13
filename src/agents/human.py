from langgraph.types import interrupt

from .state import CIQState


def human_node(state: CIQState) -> dict:
    decision = interrupt({
        "draft": state.get("draft", ""),
        "critique": state.get("critique", {}),
        "triage": state.get("triage", {}),
        "ask": (
            "Return a decision with action approve, edit, or reject. "
            "For edit, include the edited text."
        ),
    })

    action = decision.get("action")

    if action not in {"approve", "edit", "reject"}:
        raise ValueError("Invalid human-review action")

    update = {
        "human_decision": decision,
        "trace": [{"node": "human", "action": action}],
    }

    if action == "edit":
        edited_text = decision.get("text", "")

        if not edited_text.strip():
            raise ValueError("Edited draft cannot be empty")

        update["draft"] = edited_text

    return update


def refuse_node(state: CIQState) -> dict:
    return {
        "draft": (
            "I can help with supported consumer complaint triage, "
            "complaint analytics, regulatory research, or complaint trend briefs. "
            "This request is outside the supported scope."
        ),
        "trace": [{"node": "refuse", "reason": "OUT_OF_SCOPE"}],
    }


def after_human(state: CIQState) -> str:
    action = state.get("human_decision", {}).get("action")
    return "publish" if action in {"approve", "edit"} else "END"
