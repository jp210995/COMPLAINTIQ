import re
from collections import defaultdict
from typing import Callable, Optional

import faiss
import numpy as np
from rank_bm25 import BM25Okapi


def tok(s):
    """
    Original Phase 3 tokenizer.

    Preserves decimal regulatory references such as 1005.11.
    """
    return re.findall(
        r"[a-z0-9]+(?:\.[0-9]+)?",
        str(s).lower()
    )


class HybridIndex:
    """
    Dense FAISS + sparse BM25 retrieval with Reciprocal Rank Fusion.

    embed_fn:
        Callable accepting a list of strings and returning a
        float32-compatible matrix of shape (n_queries, dimension).

    Pass the existing Phase 3 cache-only Titan embedding function.
    This class does not create AWS clients or generate embeddings.
    """

    def __init__(
        self,
        chunks,
        vectors,
        embed_fn: Optional[Callable] = None
    ):
        self.chunks = list(chunks)

        self.vectors = np.asarray(
            vectors,
            dtype="float32"
        )

        self.embed_fn = embed_fn

        if len(self.vectors) != len(self.chunks):
            raise ValueError(
                "Vector/metadata count mismatch"
            )

        if self.vectors.ndim != 2:
            raise ValueError(
                "Vectors must be a 2D matrix"
            )

        if len(self.vectors) == 0:
            raise ValueError(
                "Cannot construct an empty HybridIndex"
            )

        if not np.isfinite(self.vectors).all():
            raise ValueError(
                "Invalid vectors: NaN or Inf detected"
            )

        self.faiss = faiss.IndexFlatIP(
            self.vectors.shape[1]
        )

        self.faiss.add(self.vectors)

        self.bm25 = BM25Okapi([
            tok(chunk.get("text", ""))
            for chunk in self.chunks
        ])

    def search(
        self,
        query,
        k=8,
        pool=40,
        rrf_k=60
    ):
        if not query or not str(query).strip():
            raise ValueError(
                "Query cannot be blank"
            )

        if self.embed_fn is None:
            raise RuntimeError(
                "HybridIndex has no embedding function. "
                "Pass the existing Phase 3 cache-only "
                "embedding function as embed_fn."
            )

        if k < 1 or pool < 1 or rrf_k < 1:
            raise ValueError(
                "k, pool and rrf_k must be positive"
            )

        pool = min(pool, len(self.chunks))

        qv = np.asarray(
            self.embed_fn([query]),
            dtype="float32"
        )

        if qv.ndim != 2 or qv.shape[0] != 1:
            raise ValueError(
                "Embedding function must return "
                "a 2D matrix with one query vector"
            )

        if qv.shape[1] != self.vectors.shape[1]:
            raise ValueError(
                "Query/index embedding dimension mismatch"
            )

        if not np.isfinite(qv).all():
            raise ValueError(
                "Query embedding contains NaN or Inf"
            )

        _, dense_ids = self.faiss.search(
            qv,
            pool
        )

        sparse_scores = self.bm25.get_scores(
            tok(query)
        )

        sparse_ids = np.argsort(
            sparse_scores
        )[::-1][:pool]

        scores = defaultdict(float)

        for ranking in (dense_ids[0], sparse_ids):
            for rank, idx in enumerate(ranking):
                if int(idx) >= 0:
                    scores[int(idx)] += (
                        1.0 / (rrf_k + rank + 1)
                    )

        # Original Phase 3 CFR citation prioritisation.
        citation = re.search(
            r"\b(\d{1,2})\s*CFR\s*(\d{3,4}\.\d+)\b",
            query,
            re.I
        )

        if citation:
            target = (
                f"{citation.group(1)} CFR "
                f"{citation.group(2)}"
            ).lower()

            compact = (
                f"{citation.group(1)}cfr"
                f"{citation.group(2)}"
            ).lower()

            for idx, rec in enumerate(self.chunks):
                haystack = " ".join([
                    str(rec.get("chunk_id", "")),
                    str(rec.get("section", "")),
                    str(rec.get("text", ""))
                ]).lower()

                normalized = re.sub(
                    r"\s+",
                    " ",
                    haystack
                )

                compact_haystack = re.sub(
                    r"[^a-z0-9.]",
                    "",
                    haystack
                )

                if (
                    target in normalized
                    or compact in compact_haystack
                ):
                    scores[idx] += 1.0

        top = sorted(
            scores,
            key=scores.get,
            reverse=True
        )[:k]

        return [
            {
                **self.chunks[i],
                "rrf": round(
                    float(scores[i]),
                    6
                )
            }
            for i in top
        ]
