import re
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
    """Retrieve regulatory evidence while preserving source provenance."""

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

        source_type = hit.get("source_type")
        source_file = hit.get("source_file")
        source_id = hit.get("source_id")
        citation = hit.get("citation")

        # PDF page numbers are derived only from existing provenance.
        page_number = None

        if source_type == "pdf":

            page_match = re.search(
                r"_page_(\d+)(?:_|$)",
                str(source_id or "")
            )

            if not page_match:
                page_match = re.search(
                    r"\bpage\s+(\d+)\b",
                    str(citation or ""),
                    re.IGNORECASE
                )

            if page_match:
                page_number = int(page_match.group(1))

        evidence.append({
            # Original chunk identity
            "chunk_id": hit.get("chunk_id"),
            "chunk_number": hit.get("chunk_number"),

            # Full original provenance
            "source_type": source_type,
            "source_id": source_id,
            "source_file": source_file,
            "citation": citation,
            "title": hit.get("title"),

            # Backward-compatible aliases
            "source": source_file,
            "page": page_number,

            # Retrieved content and score
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
