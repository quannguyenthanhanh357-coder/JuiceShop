#!/usr/bin/env python3
"""
Tuần 2 — Chứng minh IAM qua Kong.
Chạy khi stack đã up: docker compose up -d
Target: http://localhost:8000 (Kong) → juice-shop:3000
"""
from __future__ import annotations

import sys

try:
    import requests
except ImportError:
    print("[!] Cần: pip install requests")
    sys.exit(1)

KONG = "http://localhost:8000"
RECON_KEY = "recon-key-demo"
EXPLOIT_KEY = "exploit-key-demo"


def check(name: str, ok: bool, detail: str = "") -> bool:
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))
    return ok


def main() -> int:
    print("[*] Test Kong IAM (chỉ localhost:8000)\n")
    passed = 0
    total = 0

    # 1) Không có key → 401
    total += 1
    try:
        r = requests.get(f"{KONG}/rest/products/search?q=apple", timeout=10)
        if check("GET không key → 401", r.status_code == 401, f"got {r.status_code}"):
            passed += 1
    except requests.RequestException as e:
        check("GET không key → 401", False, str(e))

    # 2) Recon key + GET → 200 (hoặc 2xx từ Juice Shop)
    total += 1
    try:
        r = requests.get(
            f"{KONG}/rest/products/search?q=apple",
            headers={"apikey": RECON_KEY},
            timeout=10,
        )
        if check("Recon GET products → 2xx", 200 <= r.status_code < 300, f"got {r.status_code}"):
            passed += 1
    except requests.RequestException as e:
        check("Recon GET products → 2xx", False, str(e))

    # 3) Recon key + POST admin/Users → 403 (ACL không cho write)
    total += 1
    try:
        r = requests.post(
            f"{KONG}/api/Users",
            headers={"apikey": RECON_KEY, "Content-Type": "application/json"},
            json={"email": "recon@test.local", "password": "x", "passwordRepeat": "x"},
            timeout=10,
        )
        if check("Recon POST /api/Users → 403", r.status_code == 403, f"got {r.status_code}"):
            passed += 1
    except requests.RequestException as e:
        check("Recon POST /api/Users → 403", False, str(e))

    # 4) Exploit key + POST → không bị Kong 403 (có thể 4xx từ app — vẫn OK)
    total += 1
    try:
        r = requests.post(
            f"{KONG}/api/Users",
            headers={"apikey": EXPLOIT_KEY, "Content-Type": "application/json"},
            json={"email": "exploit-demo@test.local", "password": "x", "passwordRepeat": "x"},
            timeout=10,
        )
        # Kong cho qua → không phải 401/403 từ gateway
        ok = r.status_code not in (401, 403)
        if check("Exploit POST /api/Users → không 401/403 Kong", ok, f"got {r.status_code}"):
            passed += 1
    except requests.RequestException as e:
        check("Exploit POST /api/Users → không 401/403 Kong", False, str(e))

    print(f"\n[*] Kết quả: {passed}/{total} PASS")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
