#!/usr/bin/env python3
"""Query RAG store (Chroma hoặc BOW)."""
from __future__ import annotations

import argparse
import math
import pickle
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INDEX_PATH = ROOT / "store" / "bow_index.pkl"
_TOKEN = re.compile(r"[a-z0-9_]+", re.I)


def tokenize(text: str) -> list[str]:
    return _TOKEN.findall(text.lower())


def cosine(a: dict[str, float], b: dict[str, float]) -> float:
    keys = set(a) | set(b)
    dot = sum(a.get(k, 0.0) * b.get(k, 0.0) for k in keys)
    na = math.sqrt(sum(v * v for v in a.values()) or 1e-9)
    nb = math.sqrt(sum(v * v for v in b.values()) or 1e-9)
    return dot / (na * nb)


def load_index() -> dict:
    if not INDEX_PATH.exists():
        raise SystemExit("Chưa ingest. Chạy: python rag/ingest.py")
    with open(INDEX_PATH, "rb") as f:
        return pickle.load(f)


def query_bow(index: dict, question: str, k: int = 3) -> list[dict]:
    idf = index["idf"]
    q_tf: dict[str, float] = {}
    tokens = tokenize(question)
    for t in tokens:
        q_tf[t] = q_tf.get(t, 0.0) + 1.0
    n = float(len(tokens) or 1)
    q_vec = {t: (c / n) * idf.get(t, 0.0) for t, c in q_tf.items()}

    scored = []
    for i, doc_tf in enumerate(index["doc_tfs"]):
        d_vec = {t: w * idf.get(t, 0.0) for t, w in doc_tf.items()}
        score = cosine(q_vec, d_vec)
        scored.append((score, index["docs"][i]))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [{"score": s, **d} for s, d in scored[:k]]


def query_chroma(question: str, k: int = 3) -> list[dict] | None:
    import os

    if os.environ.get("SENTINEL_USE_CHROMA", "").strip() not in ("1", "true", "yes"):
        return None
    try:
        import chromadb  # type: ignore
    except ImportError:
        return None
    path = ROOT / "store" / "chroma"
    if not path.exists():
        return None
    client = chromadb.PersistentClient(path=str(path))
    coll = client.get_or_create_collection("sentinel_threats")
    if coll.count() == 0:
        return None
    res = coll.query(query_texts=[question], n_results=k)
    out = []
    for i, doc_id in enumerate(res["ids"][0]):
        out.append(
            {
                "id": doc_id,
                "text": res["documents"][0][i],
                "score": 1.0 - (res["distances"][0][i] if res.get("distances") else 0.0),
                "path": (res["metadatas"][0][i] or {}).get("path", ""),
            }
        )
    return out


def search(question: str, k: int = 3) -> list[dict]:
    chroma = query_chroma(question, k=k)
    if chroma:
        return chroma
    return query_bow(load_index(), question, k=k)


def main() -> None:
    parser = argparse.ArgumentParser(description="Query Sentinel RAG")
    parser.add_argument("question", nargs="?", default="SQL Injection là gì?")
    parser.add_argument("-k", type=int, default=3)
    args = parser.parse_args()
    hits = search(args.question, k=args.k)
    print(f"Q: {args.question}\n")
    for i, h in enumerate(hits, 1):
        snippet = h["text"][:200].replace("\n", " ")
        print(f"{i}. [{h.get('id', '?')}] score={h['score']:.3f}")
        print(f"   {snippet}...\n")


if __name__ == "__main__":
    main()
