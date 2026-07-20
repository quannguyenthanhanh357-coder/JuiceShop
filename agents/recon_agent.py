#!/usr/bin/env python3
"""
Tuần 4 — Recon Agent: đọc SAST/DAST (+ RAG gợi ý) → Attack Surface Map JSON.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "agents"))
sys.path.insert(0, str(ROOT / "rag"))

from common import LLMClient, parse_json_loose, write_trace  # noqa: E402


def load_vulns(db_path: Path, limit: int = 20) -> list[dict]:
    if not db_path.exists():
        return []
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT tool, severity, name, description, path_or_url FROM vulnerabilities ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def rag_snippets(query: str, k: int = 2) -> list[str]:
    try:
        from query import search

        return [h["text"][:400] for h in search(query, k=k)]
    except Exception as e:
        return [f"(RAG unavailable: {e})"]


SYSTEM = """Bạn là Recon Agent cho Project Sentinel.
Chỉ phân tích OWASP Juice Shop trên localhost/Compose.
Output BẮT BUỘC JSON: {endpoints:[{path,method,risk,issue,cve_related}], summary:string}.
Không đưa lời khuyên tấn công hệ thống thật."""


def run_recon(db: Path | None = None) -> dict:
    db = db or (ROOT / "data-lake" / "vuln_data.db")
    vulns = load_vulns(db)
    snippets = rag_snippets("Juice Shop SQL Injection XSS access control")
    user = json.dumps({"vulnerabilities": vulns, "rag_context": snippets}, ensure_ascii=False)
    # Token budget: cắt ngắn
    if len(user) > 6000:
        user = user[:6000] + "...(truncated)"

    llm = LLMClient()
    raw = llm.chat(SYSTEM, user)
    data = parse_json_loose(raw)
    out_path = ROOT / "data-lake" / "attack_surface_map.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    write_trace("recon", "attack_surface_map", data)
    print(f"[+] Attack Surface Map → {out_path}")
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=ROOT / "data-lake" / "vuln_data.db")
    args = parser.parse_args()
    result = run_recon(args.db)
    print(json.dumps(result, indent=2, ensure_ascii=False)[:1500])


if __name__ == "__main__":
    main()
