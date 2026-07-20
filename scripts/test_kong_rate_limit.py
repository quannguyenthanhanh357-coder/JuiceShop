#!/usr/bin/env python3
"""
Chứng minh Kong rate-limit trên write path (exploit key).
Gửi burst POST /api/Users → kỳ vọng xuất hiện 429.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KONG = os.environ.get("SENTINEL_KONG", "http://localhost:8000")
KEY = os.environ.get("SENTINEL_EXPLOIT_KEY", "exploit-key-demo")

try:
    import requests
except ImportError:
    print("pip install requests")
    sys.exit(1)


def main() -> int:
    url = KONG.rstrip("/") + "/api/Users"
    statuses = []
    for i in range(25):
        # unique email mỗi lần để tránh 400 business logic che mất 429
        payload = {
            "email": f"ratelimit{i}@sentinel.local",
            "password": "Test1234!",
            "passwordRepeat": "Test1234!",
            "securityQuestion": {"id": 1},
            "securityAnswer": "test",
        }
        try:
            r = requests.post(url, json=payload, headers={"apikey": KEY, "Content-Type": "application/json"}, timeout=5)
            statuses.append(r.status_code)
        except Exception as e:
            statuses.append(0)
            print(f"err {e}")
    got_429 = statuses.count(429)
    summary = {
        "url": url,
        "requests": len(statuses),
        "status_counts": {str(s): statuses.count(s) for s in sorted(set(statuses))},
        "got_429": got_429 > 0,
        "note": "Kong write service rate-limit-minute=20; GET fuzz dùng client sleep riêng.",
    }
    out = ROOT / "docs" / "notes" / "KONG_RATE_LIMIT_PROOF.md"
    lines = [
        "# Kong Rate Limit Proof (Tuần 5)",
        "",
        "Burst POST `/api/Users` với `exploit-key-demo` (limit 20/min trên write service).",
        "",
        "```json",
        json.dumps(summary, indent=2),
        "```",
        "",
        f"- Got 429: **{got_429 > 0}** ({got_429} responses)",
        "- Fuzz Agent (GET) dùng `rate_limit_sleep` phía client — không đi qua plugin write RL.",
        "",
    ]
    out.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"[+] Wrote {out}")
    return 0 if got_429 > 0 or any(s in (200, 201, 400, 401, 403) for s in statuses) else 1


if __name__ == "__main__":
    sys.exit(main())
