#!/usr/bin/env python3
"""
Đo retrieval accuracy trên 10 câu hỏi gold (doc id kỳ vọng nằm trong top-k).
"""
from __future__ import annotations

import json
from pathlib import Path

from hybrid_search import hybrid_search
from query import search

ROOT = Path(__file__).resolve().parent

# Câu hỏi → tập id tài liệu "đúng ngữ cảnh" (ít nhất 1 hit trong top-3)
GOLD = [
    ("SQL Injection là gì và cách phòng?", {"owasp_sqli_cheatsheet", "pentest_juice_sqli", "cve_sqli_rce"}),
    ("Juice Shop search endpoint SQLi", {"pentest_juice_sqli", "owasp_sqli_cheatsheet"}),
    ("XSS prevention cheat sheet", {"owasp_xss_cheatsheet", "pentest_juice_xss"}),
    ("Log4Shell CVE-2021-44228", {"cve_log4shell"}),
    ("Apache Struts RCE Content-Type", {"cve_struts"}),
    ("Broken access control admin Juice Shop", {"pentest_juice_access", "owasp_auth_cheatsheet"}),
    ("JWT authentication best practices", {"owasp_auth_cheatsheet", "pentest_juice_access"}),
    ("Stored XSS trong feedback", {"pentest_juice_xss", "owasp_xss_cheatsheet"}),
    ("Union SQL injection Users table", {"pentest_juice_sqli", "cve_sqli_rce"}),
    ("Vulnerable outdated components Log4j", {"cve_log4shell"}),
]


def eval_one(use_hybrid: bool, k: int = 3) -> dict:
    hits = 0
    details = []
    for q, expected in GOLD:
        results = hybrid_search(q, top_k=k) if use_hybrid else search(q, k=k)
        ids = {r["id"] for r in results}
        ok = bool(ids & expected)
        hits += int(ok)
        details.append({"q": q, "got": sorted(ids), "expected": sorted(expected), "ok": ok})
    return {
        "mode": "hybrid" if use_hybrid else "vector_or_bow",
        "correct": hits,
        "total": len(GOLD),
        "accuracy": hits / len(GOLD),
        "details": details,
    }


def main() -> None:
    # Đảm bảo đã ingest
    if not (ROOT / "store" / "bow_index.pkl").exists():
        from ingest import main as ingest_main

        ingest_main()

    bow = eval_one(False)
    hyb = eval_one(True)
    report = {"bow_or_chroma": bow, "hybrid": hyb}
    out = ROOT / "store" / "retrieval_eval.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"BOW/Chroma: {bow['correct']}/{bow['total']} = {bow['accuracy']:.0%}")
    print(f"Hybrid:     {hyb['correct']}/{hyb['total']} = {hyb['accuracy']:.0%}")
    print(f"[+] Wrote {out}")


if __name__ == "__main__":
    main()
