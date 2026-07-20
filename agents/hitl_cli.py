#!/usr/bin/env python3
"""
Tuần 8 — HITL CLI: approve/reject hành động nguy hiểm (local, không cần Slack).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HITL_LOG = ROOT / "data-lake" / "hitl_decisions.jsonl"


def _log(decision: str, title: str, details: str) -> None:
    HITL_LOG.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "title": title,
        "details_preview": details[:1000],
    }
    with open(HITL_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def request_approval(title: str, details: str, auto_approve: bool = False) -> bool:
    """
    Trả True nếu approve.
    auto_approve=True dùng cho demo/CI offline.
    """
    print("\n========== HITL APPROVAL ==========")
    print(f"Title: {title}")
    print(details[:2000])
    print("===================================")

    if auto_approve:
        print("[HITL] auto-approve (--yes / demo mode)")
        _log("approve", title, details)
        return True

    try:
        ans = input("Approve? [y/N]: ").strip().lower()
    except EOFError:
        ans = "n"
    ok = ans in ("y", "yes")
    _log("approve" if ok else "reject", title, details)
    print(f"[HITL] {'APPROVED' if ok else 'REJECTED'}")
    return ok


if __name__ == "__main__":
    ok = request_approval("Demo", '{"action":"sqli_probe"}', auto_approve=True)
    print("result", ok)
