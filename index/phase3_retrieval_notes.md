# ComplaintIQ — Phase 3 Retrieval Layer

## Objective
Retrieve relevant banking regulations/reference passages
and similar historical consumer complaints.

## Implementation
- Embeddings: Amazon Bedrock Titan Text Embeddings V2
- Dimensions: 1,024
- Dense retrieval: FAISS IndexFlatIP
- Keyword retrieval: BM25Okapi
- Fusion: Reciprocal Rank Fusion, k=60
- Cache: SHA1-keyed NumPy files
- Embedding concurrency: 3 workers

## Indexed corpus
- Regulatory/document chunks: 1784
- Deduplicated Jan-May complaint pool: 31813
- Stratified complaint sample: 3000
- June holdout: 6110 (excluded)
- Sample seed: 42

## Validation
- Five regulatory smoke tests saved.
- Exact 12 CFR 1005.11 test: True
- Similar complaint results saved.
- June holdout overlap: 0

## Why hybrid retrieval?
Dense retrieval identifies semantically similar passages.
BM25 matches exact terminology, decimal CFR section numbers,
and other lexical details. RRF combines both ranked lists.

## Limitations
Smoke tests are functional checks, not a comprehensive benchmark.
Phase 7 must evaluate recall@5 and compare dense-only,
BM25-only, and hybrid retrieval against a labeled golden set.
