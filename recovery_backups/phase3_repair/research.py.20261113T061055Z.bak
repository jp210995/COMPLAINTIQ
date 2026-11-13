from .state import CIQState


# Index objects are supplied explicitly after loading existing Phase 3
# artifacts. This module never creates embeddings or loads AWS clients.
_REG_INDEX = None
_CASE_INDEX = None


def configure_indexes(reg_index=None, case_index=None):
    global _REG_INDEX, _CASE_INDEX

    if reg_index is not None:
        _REG_INDEX = reg_index

    if case_index is not None:
        _CASE_INDEX = case_index


def configure_reg_index(reg_index):
    configure_indexes(reg_index=reg_index)


def configure_case_index(case_index):
    configure_indexes(case_index=case_index)


def cases_node(state: CIQState) -> dict:
    if _CASE_INDEX is None:
        raise RuntimeError(
            "CASE_INDEX is not configured. Load the existing Phase 3 "
            "case vectors/chunks and call configure_case_index()."
        )

    t = state["triage"]

    hits = _CASE_INDEX.search(
        f"{t['product']} {t['issue']} {t['summary']}",
        k=5,
    )

    keep = [
        "complaint_id",
        "issue",
        "company_response",
        "timely",
        "rrf",
    ]

    similar_cases = [
        {key: hit.get(key) for key in keep}
        for hit in hits
    ]

    return {
        "similar_cases": similar_cases,
        "trace": [{"node": "cases", "n": len(hits)}],
    }


def research_node(state: CIQState) -> dict:
    if _REG_INDEX is None:
        raise RuntimeError(
            "REG_INDEX is not configured. Load the existing Phase 3 "
            "regulatory vectors/chunks and call configure_reg_index()."
        )

    query = state["clean_request"]

    if state.get("triage"):
        t = state["triage"]
        query = (
            f"{t['issue']} "
            f"{' '.join(t.get('regulation_hints', []))} "
            f"{t['summary']}"
        )

    hits = _REG_INDEX.search(query, k=8)

    evidence = []

    for hit in hits:
        evidence.append({
            "chunk_id": hit.get("chunk_id"),
            "source": hit.get("source"),
            "page": hit.get("page"),
            "text": hit.get("text", ""),
            "rrf": hit.get("rrf"),
        })

    return {
        "evidence": evidence,
        "trace": [{
            "node": "research",
            "ids": [e["chunk_id"] for e in evidence],
        }],
    }
