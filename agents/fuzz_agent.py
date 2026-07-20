#!/usr/bin/env python3
"""
Tuần 5 — Fuzz Agent: HTTP chỉ qua Kong localhost:8000, rate-limited.
Payload giáo dục/demo — không nhắm host ngoài.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "agents"))

from common import (  # noqa: E402
    KONG_BASE,
    LLMClient,
    RECON_KEY,
    parse_json_loose,
    rate_limit_sleep,
    write_trace,
)

try:
    import requests
except ImportError:
    requests = None  # type: ignore

# Payload demo an toàn — chỉ dùng với localhost
DEMO_PAYLOADS = [
    "'",
    "' OR 1=1--",
    "<script>alert(1)</script>",
    "' UNION SELECT null--",
]


SYSTEM = """Bạn là Fuzz Agent. Target chỉ Juice Shop qua Kong local.
Sinh JSON {payloads:[{target,param,value}]} — payload giáo dục, không destructive."""


def kong_get(path: str, params: dict | None = None) -> dict:
    if requests is None:
        return {"error": "pip install requests", "status": 0}
    url = KONG_BASE.rstrip("/") + path
    if params:
        url += "?" + urlencode(params)
    try:
        r = requests.get(url, headers={"apikey": RECON_KEY}, timeout=3)
        body = r.text[:500]
        return {
            "url": url,
            "status": r.status_code,
            "latency_ms": int(r.elapsed.total_seconds() * 1000),
            "body_preview": body,
            "anomaly": r.status_code >= 500 or "sequelize" in body.lower() or "sqlite" in body.lower(),
        }
    except Exception as e:
        return {"url": url, "status": 0, "error": str(e), "anomaly": True}


def run_fuzz(map_path: Path | None = None, max_requests: int = 8) -> list[dict]:
    map_path = map_path or (ROOT / "data-lake" / "attack_surface_map.json")
    surface = {}
    if map_path.exists():
        surface = json.loads(map_path.read_text(encoding="utf-8"))

    llm = LLMClient()
    raw = llm.chat(SYSTEM, json.dumps({"surface": surface, "hint": "search q param"}, ensure_ascii=False))
    try:
        plan = parse_json_loose(raw)
        payloads = plan.get("payloads") or []
    except Exception:
        payloads = []

    if not payloads:
        payloads = [
            {"target": "/rest/products/search", "param": "q", "value": p} for p in DEMO_PAYLOADS
        ]

    findings = []
    for i, p in enumerate(payloads):
        if i >= max_requests:
            break
        # Chỉ cho phép path local tương đối
        target = p.get("target", "/rest/products/search")
        if not target.startswith("/"):
            continue
        if "localhost" not in KONG_BASE and "127.0.0.1" not in KONG_BASE:
            write_trace("fuzz", "blocked_non_local", {"base": KONG_BASE})
            break
        param = p.get("param", "q")
        value = str(p.get("value", ""))
        result = kong_get(target, {param: value})
        result["payload"] = value
        findings.append(result)
        write_trace("fuzz", "probe", result)
        rate_limit_sleep(0.4)
        print(f"  [{result.get('status')}] {target}?{param}=... anomaly={result.get('anomaly')}")

    out = ROOT / "data-lake" / "fuzz_findings.json"
    out.write_text(json.dumps(findings, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[+] Fuzz findings → {out}")
    return findings


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max", type=int, default=8)
    args = parser.parse_args()
    if "localhost" not in KONG_BASE and "127.0.0.1" not in KONG_BASE:
        print("[!] SENTINEL_KONG phải là localhost — abort")
        sys.exit(2)
    run_fuzz(max_requests=args.max)


if __name__ == "__main__":
    main()
