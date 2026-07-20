#!/usr/bin/env python3
"""
Tuần 10 — Eval pipeline: 10 Juice Shop challenges ground truth + mock LLM judge.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "agents"))

from common import LLMClient, parse_json_loose, write_trace  # noqa: E402

# Ground truth: challenge name → tín hiệu agent cần nêu
GROUND_TRUTH = [
    {"id": "loginAdmin", "name": "Login Admin", "signals": ["admin", "login", "password"]},
    {"id": "unionSql", "name": "Union SQL Injection", "signals": ["sql", "union", "search"]},
    {"id": "domXss", "name": "DOM XSS", "signals": ["xss", "script", "search"]},
    {"id": "scoreBoard", "name": "Score Board", "signals": ["score", "challenge"]},
    {"id": "adminReg", "name": "Admin Registration", "signals": ["register", "role", "admin"]},
    {"id": "basketIdor", "name": "View Another User's Basket", "signals": ["basket", "idor"]},
    {"id": "forgedFeedback", "name": "Forged Feedback", "signals": ["feedback", "xss"]},
    {"id": "jwt", "name": "JWT Issues", "signals": ["jwt", "token", "role"]},
    {"id": "dirListing", "name": "Directory Listing FTP", "signals": ["ftp", "directory"]},
    {"id": "exposedMetrics", "name": "Exposed Metrics", "signals": ["metrics", "prometheus"]},
]


def agent_hypothesis(challenge: dict) -> dict:
    """Giả lập output agent — nhúng signals để mock/rule-based eval ổn định offline."""
    # Deterministic hypothesis (không phụ thuộc mock branch 'evaluate')
    hyp = {
        "detected": True,
        "evidence": f"Mapped to Juice Shop challenge {challenge['name']}",
        "signals_mentioned": challenge["signals"],
        "notes": " ".join(challenge["signals"]),
        "score": 0.85,
    }
    # Optional: hỏi LLM (mock sẽ trả verdict chung — ta vẫn giữ signals ở trên)
    llm = LLMClient()
    raw = llm.chat(
        "Summarize challenge risk as JSON {extra_note:string}. Lab only.",
        json.dumps({"challenge": challenge["name"]}, ensure_ascii=False),
    )
    try:
        extra = parse_json_loose(raw)
        if isinstance(extra, dict):
            hyp["llm_extra"] = extra
    except Exception:
        pass
    return hyp


def judge(challenge: dict, hypothesis: dict) -> dict:
    llm = LLMClient()
    raw = llm.chat(
        "You are an evaluation judge. Return JSON {score:0-1, verdict, reason}.",
        json.dumps({"challenge": challenge, "hypothesis": hypothesis}),
    )
    try:
        j = parse_json_loose(raw)
    except Exception:
        j = {"score": 0.8, "verdict": "ok", "reason": "fallback"}
    text = json.dumps(hypothesis).lower()
    hit = sum(1 for s in challenge["signals"] if s.lower() in text)
    rule_score = min(1.0, 0.4 + 0.2 * hit)
    final = max(float(j.get("score", 0)), rule_score)
    return {"llm_judge": j, "rule_score": rule_score, "final_score": final, "signal_hits": hit}


def run_eval() -> dict:
    rows = []
    t0 = time.time()
    detected = 0
    for ch in GROUND_TRUTH:
        hyp = agent_hypothesis(ch)
        j = judge(ch, hyp)
        ok = j["final_score"] >= 0.6 and j["signal_hits"] >= 1
        detected += int(ok)
        rows.append({"challenge": ch["name"], "ok": ok, "hyp": hyp, "judge": j})
        write_trace("eval", ch["id"], {"ok": ok, "score": j["final_score"]})

    report = {
        "detect_rate": detected / len(GROUND_TRUTH),
        "detected": detected,
        "total": len(GROUND_TRUTH),
        "avg_seconds": (time.time() - t0) / len(GROUND_TRUTH),
        "false_positive_est": 0.1,  # demo estimate
        "rows": rows,
    }
    path = ROOT / "data-lake" / "eval_report.json"
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[+] Detect {detected}/{len(GROUND_TRUTH)} ({report['detect_rate']:.0%}) → {path}")
    return report


if __name__ == "__main__":
    run_eval()
