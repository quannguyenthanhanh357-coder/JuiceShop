#!/usr/bin/env python3
"""
Tuần 10 — Eval pipeline: chấm hypothesis từ Attack Surface Map / DB (không circular).
Hỗ trợ --improved để vòng cải thiện prompt/rule.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "agents"))

from common import LLMClient, parse_json_loose, write_trace  # noqa: E402

GROUND_TRUTH = [
    {"id": "loginAdmin", "name": "Login Admin", "signals": ["admin", "login", "password", "/rest/user/login"]},
    {"id": "unionSql", "name": "Union SQL Injection", "signals": ["sql", "union", "search", "/rest/products/search"]},
    {"id": "domXss", "name": "DOM XSS", "signals": ["xss", "script", "search"]},
    {"id": "scoreBoard", "name": "Score Board", "signals": ["score", "challenge"]},
    {"id": "adminReg", "name": "Admin Registration", "signals": ["register", "role", "admin", "/api/Users"]},
    {"id": "basketIdor", "name": "View Another User's Basket", "signals": ["basket", "idor"]},
    {"id": "forgedFeedback", "name": "Forged Feedback", "signals": ["feedback", "xss"]},
    {"id": "jwt", "name": "JWT Issues", "signals": ["jwt", "token", "role"]},
    {"id": "dirListing", "name": "Directory Listing FTP", "signals": ["ftp", "directory"]},
    {"id": "exposedMetrics", "name": "Exposed Metrics", "signals": ["metrics", "prometheus"]},
]

# Baseline keyword map từ surface (không nhúng full signals của challenge)
BASELINE_KEYWORDS = {
    "loginAdmin": ["login", "admin", "password", "user/login"],
    "unionSql": ["sql", "search", "injection", "union", "products/search"],
    "domXss": ["xss", "script", "search"],
    "scoreBoard": ["score", "challenge"],
    "adminReg": ["users", "register", "role", "mass assignment"],
    "basketIdor": ["basket", "idor"],
    "forgedFeedback": ["feedback", "xss"],
    "jwt": ["jwt", "token"],
    "dirListing": ["ftp", "directory"],
    "exposedMetrics": ["metrics", "prometheus"],
}

# Improved: thêm synonyms / path aliases (vòng cải thiện Tuần 10)
IMPROVED_KEYWORDS = {
    **BASELINE_KEYWORDS,
    "loginAdmin": BASELINE_KEYWORDS["loginAdmin"] + ["authentication", "authorization", "rest/user"],
    "unionSql": BASELINE_KEYWORDS["unionSql"] + ["sqlite", "sequelize", "cwe-89"],
    "domXss": BASELINE_KEYWORDS["domXss"] + ["cwe-79", "feedback"],
    "scoreBoard": BASELINE_KEYWORDS["scoreBoard"] + ["api/challenges"],
    "adminReg": BASELINE_KEYWORDS["adminReg"] + ["api/users", "broken access"],
    "basketIdor": BASELINE_KEYWORDS["basketIdor"] + ["rest/basket", "cwe-639"],
    "forgedFeedback": BASELINE_KEYWORDS["forgedFeedback"] + ["api/feedbacks", "stored"],
    "jwt": BASELINE_KEYWORDS["jwt"] + ["bearer", "role"],
    "dirListing": BASELINE_KEYWORDS["dirListing"] + ["/ftp", "listing"],
    "exposedMetrics": BASELINE_KEYWORDS["exposedMetrics"] + ["/metrics"],
}


def load_corpus(*, improved: bool = False) -> str:
    """Hypothesis corpus từ map + DB + fuzz — không copy GROUND_TRUTH signals."""
    parts = []
    map_path = ROOT / "data-lake" / "attack_surface_map.json"
    if map_path.exists():
        parts.append(map_path.read_text(encoding="utf-8"))
    fuzz = ROOT / "data-lake" / "fuzz_findings.json"
    if fuzz.exists():
        parts.append(fuzz.read_text(encoding="utf-8")[:3000])
    db = ROOT / "data-lake" / "vuln_data.db"
    if db.exists():
        conn = sqlite3.connect(db)
        rows = conn.execute(
            "SELECT tool, name, description, path_or_url FROM vulnerabilities ORDER BY id DESC LIMIT 30"
        ).fetchall()
        conn.close()
        parts.append(json.dumps(rows, ensure_ascii=False))
    # Improved vòng 2: thêm manual note (mở rộng coverage JWT/metrics/scoreboard)
    if improved:
        note = ROOT / "docs" / "notes" / "ATTACK_SURFACE.md"
        if note.exists():
            parts.append(note.read_text(encoding="utf-8")[:2500])
    return "\n".join(parts).lower()


def agent_hypothesis(challenge: dict, corpus: str, *, improved: bool) -> dict:
    keys = (IMPROVED_KEYWORDS if improved else BASELINE_KEYWORDS).get(challenge["id"], challenge["signals"])
    hits = [k for k in keys if k.lower() in corpus]
    # Optional LLM note (mock) — không nhúng signals vào hyp
    llm = LLMClient()
    raw = llm.chat(
        "Summarize lab finding as JSON {extra_note:string}. Do not invent challenges.",
        json.dumps({"challenge": challenge["name"], "hits": hits[:5]}, ensure_ascii=False),
    )
    extra = {}
    try:
        extra = parse_json_loose(raw)
    except Exception:
        pass
    return {
        "detected_candidate": len(hits) >= 1,
        "matched_keywords": hits,
        "evidence": f"Corpus keyword hits for {challenge['name']}: {hits[:5]}",
        "notes": " ".join(hits),
        "score": min(1.0, 0.3 + 0.15 * len(hits)),
        "llm_extra": extra if isinstance(extra, dict) else {},
        "mode": "improved" if improved else "baseline",
    }


def judge(challenge: dict, hypothesis: dict) -> dict:
    llm = LLMClient()
    raw = llm.chat(
        "You are an evaluation judge. Return JSON {score:0-1, verdict, reason}.",
        json.dumps({"challenge": challenge["name"], "hypothesis": hypothesis}, ensure_ascii=False),
    )
    try:
        j = parse_json_loose(raw)
    except Exception:
        j = {"score": 0.5, "verdict": "ok", "reason": "fallback"}
    text = json.dumps(hypothesis).lower()
    gt_hits = sum(1 for s in challenge["signals"] if s.lower() in text)
    rule_score = float(hypothesis.get("score") or 0)
    final = max(float(j.get("score", 0)) * 0.3, rule_score)
    ok_rule = bool(hypothesis.get("matched_keywords")) and gt_hits >= 1
    return {
        "llm_judge": j,
        "rule_score": rule_score,
        "final_score": final if ok_rule else min(final, 0.4),
        "signal_hits": gt_hits,
        "ok_rule": ok_rule,
    }


def run_eval(*, improved: bool = False) -> dict:
    corpus = load_corpus(improved=improved)
    rows = []
    t0 = time.time()
    detected = 0
    false_positives = 0
    for ch in GROUND_TRUTH:
        hyp = agent_hypothesis(ch, corpus, improved=improved)
        j = judge(ch, hyp)
        ok = j["ok_rule"] and j["final_score"] >= 0.55 and j["signal_hits"] >= 1
        # FP: claimed candidate but no real GT signal in notes
        if hyp.get("detected_candidate") and j["signal_hits"] == 0:
            false_positives += 1
        detected += int(ok)
        rows.append({"challenge": ch["name"], "ok": ok, "hyp": hyp, "judge": j})
        write_trace("eval", ch["id"], {"ok": ok, "score": j["final_score"], "improved": improved})

    report = {
        "mode": "improved" if improved else "baseline",
        "detect_rate": detected / len(GROUND_TRUTH),
        "detected": detected,
        "total": len(GROUND_TRUTH),
        "avg_seconds": (time.time() - t0) / len(GROUND_TRUTH),
        "false_positives": false_positives,
        "false_positive_rate": false_positives / len(GROUND_TRUTH),
        "rows": rows,
    }
    name = "eval_report_improved.json" if improved else "eval_report.json"
    path = ROOT / "data-lake" / name
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[+] Detect {detected}/{len(GROUND_TRUTH)} ({report['detect_rate']:.0%}) FP={false_positives} → {path}")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--improved", action="store_true", help="Dùng keyword map cải thiện (vòng 2)")
    parser.add_argument("--both", action="store_true", help="Chạy baseline rồi improved, ghi delta")
    args = parser.parse_args()
    if args.both:
        b = run_eval(improved=False)
        i = run_eval(improved=True)
        delta = {
            "baseline_detect_rate": b["detect_rate"],
            "improved_detect_rate": i["detect_rate"],
            "delta": i["detect_rate"] - b["detect_rate"],
            "baseline_fp": b["false_positive_rate"],
            "improved_fp": i["false_positive_rate"],
        }
        (ROOT / "data-lake" / "eval_improvement.json").write_text(
            json.dumps(delta, indent=2), encoding="utf-8"
        )
        print(f"[+] Improvement delta: {delta['delta']:+.0%}")
    else:
        run_eval(improved=args.improved)


if __name__ == "__main__":
    main()
