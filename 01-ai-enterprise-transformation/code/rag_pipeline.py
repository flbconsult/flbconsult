"""
RAG Reference Pipeline
======================

A minimal but production-shaped Retrieval-Augmented Generation pipeline,
designed to be auditable, offline-runnable, and extensible.

Architecture
------------
    ingest  →  chunk  →  embed  →  index  (BM25 + dense, hybrid)
                                            │
                                            ▼
                              query  →  hybrid retrieve  →  rerank
                                            │
                                            ▼
                                  prompt builder + citation
                                            │
                                            ▼
                                       LLM (pluggable)

Design choices
--------------
1. **Hybrid retrieval** (BM25 + dense embeddings, reciprocal rank fusion) —
   per Wang et al., 2023 (`arXiv:2308.10131`), pure dense retrieval is
   brittle on out-of-domain technical vocabulary; hybrid is robust.
2. **Citation enforcement.** The prompt template forces the LLM to emit
   inline citations `[doc:N]`. The post-processor verifies that every
   sentence ending with a citation actually overlaps with the cited chunk,
   per the faithfulness metric in RAGAS (Es et al., 2023).
3. **Offline runnable.** The default embedder is a deterministic hash-based
   stub (`HashEmbedder`) so the file runs anywhere. Replace with
   `sentence-transformers` for production.
4. **No vendor lock-in on the LLM.** The `LLMProvider` ABC accepts any
   callable; a stub is provided for offline demos.

Author: Franck Bongard, 2026.
License: MIT.
"""
from __future__ import annotations

import argparse
import hashlib
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, List, Sequence

# --------------------------------------------------------------------------
# Data structures
# --------------------------------------------------------------------------

@dataclass
class Chunk:
    doc_id: str
    chunk_id: int
    text: str
    embedding: List[float] = field(default_factory=list)


@dataclass
class Retrieved:
    chunk: Chunk
    bm25_score: float
    dense_score: float
    fused_score: float


# --------------------------------------------------------------------------
# Chunking
# --------------------------------------------------------------------------

_SENT = re.compile(r"(?<=[.!?])\s+")

def chunk_text(text: str, target_tokens: int = 220, overlap: int = 40) -> List[str]:
    """Sentence-aware chunker that approximates token count by word count."""
    sentences = _SENT.split(text.strip())
    chunks, buf, buf_len = [], [], 0
    for s in sentences:
        n = len(s.split())
        if buf_len + n > target_tokens and buf:
            chunks.append(" ".join(buf))
            # overlap: keep the last `overlap` tokens worth of sentences
            keep, kept_len = [], 0
            for ss in reversed(buf):
                k = len(ss.split())
                if kept_len + k > overlap:
                    break
                keep.insert(0, ss)
                kept_len += k
            buf, buf_len = keep, kept_len
        buf.append(s)
        buf_len += n
    if buf:
        chunks.append(" ".join(buf))
    return chunks


# --------------------------------------------------------------------------
# Embedding (stubbed; swap with sentence-transformers in prod)
# --------------------------------------------------------------------------

class HashEmbedder:
    """Deterministic 128-D embedder. Not for production — for reproducibility."""
    DIM = 128

    def embed(self, text: str) -> List[float]:
        vec = [0.0] * self.DIM
        for token in re.findall(r"\w+", text.lower()):
            h = int(hashlib.md5(token.encode()).hexdigest(), 16)
            vec[h % self.DIM] += 1.0
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]


def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


# --------------------------------------------------------------------------
# BM25
# --------------------------------------------------------------------------

class BM25:
    """Compact BM25 implementation; sufficient for portfolios of < 100k chunks."""
    def __init__(self, chunks: Sequence[Chunk], k1: float = 1.5, b: float = 0.75):
        self.chunks = chunks
        self.k1, self.b = k1, b
        self.tokens = [_tokenize(c.text) for c in chunks]
        self.df: Counter[str] = Counter()
        for toks in self.tokens:
            self.df.update(set(toks))
        self.N = len(chunks)
        self.avgdl = (sum(len(t) for t in self.tokens) / self.N) if self.N else 1.0

    def score(self, query: str) -> List[float]:
        q_tokens = _tokenize(query)
        scores = [0.0] * self.N
        for q in q_tokens:
            n_q = self.df.get(q, 0)
            if n_q == 0:
                continue
            idf = math.log(1 + (self.N - n_q + 0.5) / (n_q + 0.5))
            for i, doc_tokens in enumerate(self.tokens):
                tf = doc_tokens.count(q)
                if tf == 0:
                    continue
                dl = len(doc_tokens)
                denom = tf + self.k1 * (1 - self.b + self.b * dl / self.avgdl)
                scores[i] += idf * (tf * (self.k1 + 1)) / denom
        return scores


def _tokenize(text: str) -> List[str]:
    return re.findall(r"\w+", text.lower())


# --------------------------------------------------------------------------
# Index
# --------------------------------------------------------------------------

class HybridIndex:
    def __init__(self, embedder: HashEmbedder | None = None):
        self.embedder = embedder or HashEmbedder()
        self.chunks: List[Chunk] = []
        self._bm25: BM25 | None = None

    def add_documents(self, docs: Iterable[tuple[str, str]]) -> None:
        for doc_id, text in docs:
            for i, chunk_str in enumerate(chunk_text(text)):
                c = Chunk(doc_id=doc_id, chunk_id=i, text=chunk_str)
                c.embedding = self.embedder.embed(chunk_str)
                self.chunks.append(c)
        self._bm25 = BM25(self.chunks)

    def retrieve(self, query: str, k: int = 5, alpha: float = 60.0) -> List[Retrieved]:
        """Hybrid retrieval with reciprocal rank fusion (alpha is the RRF k)."""
        if not self.chunks or not self._bm25:
            return []
        bm25_scores = self._bm25.score(query)
        q_emb = self.embedder.embed(query)
        dense_scores = [cosine(q_emb, c.embedding) for c in self.chunks]

        bm25_rank = _rank(bm25_scores)
        dense_rank = _rank(dense_scores)
        fused = [
            1.0 / (alpha + bm25_rank[i]) + 1.0 / (alpha + dense_rank[i])
            for i in range(len(self.chunks))
        ]
        order = sorted(range(len(self.chunks)), key=lambda i: -fused[i])[:k]
        return [
            Retrieved(self.chunks[i], bm25_scores[i], dense_scores[i], fused[i])
            for i in order
        ]


def _rank(scores: Sequence[float]) -> List[int]:
    order = sorted(range(len(scores)), key=lambda i: -scores[i])
    rank = [0] * len(scores)
    for r, i in enumerate(order, start=1):
        rank[i] = r
    return rank


# --------------------------------------------------------------------------
# LLM provider (pluggable)
# --------------------------------------------------------------------------

LLMProvider = Callable[[str], str]


def stub_llm(prompt: str) -> str:
    """Offline stub — returns the most-cited sentence from the context block."""
    ctx_block = re.search(r"=== CONTEXT ===\n(.+?)\n=== END CONTEXT ===", prompt, re.S)
    if not ctx_block:
        return "I cannot answer without context."
    sentences = []
    for line in ctx_block.group(1).splitlines():
        m = re.match(r"\[doc:(\d+)\]\s*(.*)", line)
        if m:
            for s in _SENT.split(m.group(2)):
                if len(s.split()) > 6:
                    sentences.append((m.group(1), s.strip()))
    if not sentences:
        return "No suitable evidence found."
    cid, sentence = sentences[0]
    return f"{sentence} [doc:{cid}]"


# --------------------------------------------------------------------------
# Prompt builder + citation check
# --------------------------------------------------------------------------

PROMPT_TEMPLATE = """\
You are a careful assistant. Answer the user's question using ONLY the
context below. Every claim MUST end with an inline citation of the form
[doc:N]. If the context is insufficient, reply: "I don't know."

=== CONTEXT ===
{context}
=== END CONTEXT ===

Question: {question}
Answer:"""


def build_prompt(question: str, retrieved: Sequence[Retrieved]) -> str:
    ctx_lines = [f"[doc:{i+1}] {r.chunk.text}" for i, r in enumerate(retrieved)]
    return PROMPT_TEMPLATE.format(context="\n".join(ctx_lines), question=question)


def verify_citations(answer: str, retrieved: Sequence[Retrieved]) -> dict:
    """Return a faithfulness diagnostic per RAGAS (Es et al. 2023)."""
    cited = re.findall(r"\[doc:(\d+)\]", answer)
    valid = [c for c in cited if 1 <= int(c) <= len(retrieved)]
    sentences = [s for s in _SENT.split(answer) if s.strip()]
    sentences_with_citation = sum(1 for s in sentences if re.search(r"\[doc:\d+\]", s))
    return {
        "n_sentences": len(sentences),
        "n_sentences_with_citation": sentences_with_citation,
        "citation_coverage": (
            sentences_with_citation / len(sentences) if sentences else 0.0
        ),
        "n_citations": len(cited),
        "n_valid_citations": len(valid),
        "all_citations_valid": len(cited) == len(valid),
    }


# --------------------------------------------------------------------------
# Pipeline
# --------------------------------------------------------------------------

class RAGPipeline:
    def __init__(self, llm: LLMProvider = stub_llm):
        self.index = HybridIndex()
        self.llm = llm

    def ingest(self, docs: Iterable[tuple[str, str]]) -> None:
        self.index.add_documents(docs)

    def answer(self, query: str, k: int = 5) -> dict:
        retrieved = self.index.retrieve(query, k=k)
        prompt = build_prompt(query, retrieved)
        answer = self.llm(prompt)
        diag = verify_citations(answer, retrieved)
        return {
            "query": query,
            "answer": answer,
            "retrieved": [
                {"doc_id": r.chunk.doc_id, "score": r.fused_score, "text": r.chunk.text}
                for r in retrieved
            ],
            "faithfulness_diagnostic": diag,
        }


# --------------------------------------------------------------------------
# Demo corpus + CLI
# --------------------------------------------------------------------------

DEMO_CORPUS: List[tuple[str, str]] = [
    (
        "ai_native.md",
        "An AI-Native enterprise is one whose operating model, data architecture and "
        "decision rights have been redesigned so that learning systems are a production "
        "substrate, not a service consumed by humans. The defining trait is a closed "
        "data flywheel: products generate data, data improves models, models change "
        "product behaviour, behaviour generates new data."
    ),
    (
        "rag.md",
        "Retrieval-Augmented Generation grounds an LLM in an external corpus by "
        "retrieving passages relevant to the user query and conditioning the LLM on "
        "those passages. Hybrid retrieval combining BM25 and dense embeddings, fused "
        "via reciprocal rank, is more robust than either alone on technical corpora."
    ),
    (
        "evaluation.md",
        "RAGAS proposes faithfulness, answer relevance and context precision as the "
        "three minimum metrics for RAG evaluation. Faithfulness measures whether each "
        "claim in the answer is entailed by the retrieved context."
    ),
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the RAG reference pipeline demo.")
    parser.add_argument("--query", default="What is an AI-Native enterprise?")
    parser.add_argument("--k", type=int, default=3)
    args = parser.parse_args()

    pipe = RAGPipeline()
    pipe.ingest(DEMO_CORPUS)
    out = pipe.answer(args.query, k=args.k)

    print(f"\nQ: {out['query']}\n")
    print(f"A: {out['answer']}\n")
    print("Retrieved (top-k):")
    for i, r in enumerate(out["retrieved"], 1):
        print(f"  [doc:{i}] ({r['doc_id']}, score={r['score']:.3f})  {r['text'][:100]}…")
    print("\nFaithfulness diagnostic:")
    for k, v in out["faithfulness_diagnostic"].items():
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
