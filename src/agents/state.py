from typing import Annotated, Literal, TypedDict
import operator

Intent = Literal[
    "TRIAGE",
    "ANALYTICS",
    "REG_QA",
    "BRIEF",
    "OUT_OF_SCOPE",
]

class CIQState(TypedDict, total=False):
    # Incoming request and routing
    request: str
    clean_request: str
    flags: list[str]
    intent: Intent

    # Complaint triage
    triage: dict

    # SQL analyst
    sql: str
    sql_rows: list[dict]

    # Retrieval
    similar_cases: list[dict]
    regulatory_sources: list[dict]
    evidence: list[dict]

    # Draft generation and review
    draft: str
    critique: dict
    revisions: int
    human_decision: dict

    # Publishing and execution trace
    report_uri: str
    thread_id: str
    trace: Annotated[list[dict], operator.add]
