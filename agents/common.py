#!/usr/bin/env python3
"""
Common utilities cho agents: LLM client (mock/real), file tracer.
MOCK khi không có OPENAI_API_KEY — demo offline deterministic JSON.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
TRACE_DIR = ROOT / "data-lake" / "traces"
KONG_BASE = os.environ.get("SENTINEL_KONG", "http://localhost:8000")
RECON_KEY = os.environ.get("SENTINEL_RECON_KEY", "recon-key-demo")
EXPLOIT_KEY = os.environ.get("SENTINEL_EXPLOIT_KEY", "exploit-key-demo")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_trace_dir() -> Path:
    TRACE_DIR.mkdir(parents=True, exist_ok=True)
    return TRACE_DIR


def write_trace(agent: str, event: str, data: Any) -> Path:
    """Ghi trace JSONL vào data-lake/traces/."""
    ensure_trace_dir()
    path = TRACE_DIR / f"{agent}_{datetime.now().strftime('%Y%m%d')}.jsonl"
    record = {"ts": utc_now(), "agent": agent, "event": event, "data": data}
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return path


class LLMClient:
    """OpenAI nếu có key; không thì mock deterministic."""

    def __init__(self) -> None:
        self.api_key = os.environ.get("OPENAI_API_KEY", "").strip()
        self.model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        self.mock = not bool(self.api_key)

    def chat(self, system: str, user: str, *, expect_json: bool = True) -> str:
        write_trace("llm", "request", {"mock": self.mock, "system_len": len(system), "user_len": len(user)})
        if self.mock:
            out = self._mock_response(system, user)
        else:
            out = self._openai_chat(system, user)
        write_trace("llm", "response", {"mock": self.mock, "preview": out[:500]})
        return out

    def _openai_chat(self, system: str, user: str) -> str:
        try:
            from openai import OpenAI  # type: ignore
        except ImportError as e:
            raise SystemExit("Cần: pip install openai") from e
        client = OpenAI(api_key=self.api_key)
        resp = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.2,
        )
        return resp.choices[0].message.content or ""

    def _mock_response(self, system: str, user: str) -> str:
        """Phản hồi JSON cố định theo 'ý định' trong prompt — không gọi mạng."""
        blob = (system + "\n" + user).lower()
        digest = hashlib.sha256(blob.encode()).hexdigest()[:8]

        if "attack surface" in blob or ("recon" in blob and "endpoint" in blob):
            return json.dumps(
                {
                    "mock": True,
                    "id": digest,
                    "endpoints": [
                        {
                            "path": "/rest/products/search",
                            "method": "GET",
                            "risk": "high",
                            "issue": "SQL Injection",
                            "cve_related": ["CWE-89"],
                        },
                        {
                            "path": "/api/Users",
                            "method": "POST",
                            "risk": "high",
                            "issue": "Broken Access Control / mass assignment",
                            "cve_related": ["CWE-284"],
                        },
                        {
                            "path": "/api/Feedbacks",
                            "method": "POST",
                            "risk": "medium",
                            "issue": "Stored XSS",
                            "cve_related": ["CWE-79"],
                        },
                    ],
                    "summary": "Juice Shop local: SQLi search, XSS feedback, weak admin registration.",
                },
                indent=2,
            )

        # Exploit trước fuzz — vì user prompt exploit có chứa "fuzz_findings"
        if "exploit" in blob or "dangerous" in blob or "proof" in blob:
            return json.dumps(
                {
                    "mock": True,
                    "id": digest,
                    "action": "sqli_probe",
                    "dangerous": True,
                    "justification": "Confirm SQLi on local Juice Shop search only.",
                    "request": {
                        "method": "GET",
                        "path": "/rest/products/search",
                        "params": {"q": "' OR '1'='1"},
                    },
                },
                indent=2,
            )

        if "fuzz" in blob or ("payload" in blob and "target" in blob):
            return json.dumps(
                {
                    "mock": True,
                    "id": digest,
                    "payloads": [
                        {"target": "/rest/products/search", "param": "q", "value": "' OR 1=1--"},
                        {"target": "/rest/products/search", "param": "q", "value": "<script>alert(1)</script>"},
                        {"target": "/rest/products/search", "param": "q", "value": "' UNION SELECT null--"},
                    ],
                },
                indent=2,
            )

        if "judge" in blob or "evaluate" in blob or "verdict" in blob:
            return json.dumps(
                {
                    "mock": True,
                    "score": 0.85,
                    "verdict": "partial_match",
                    "reason": "Mock judge: endpoint/risk aligned.",
                },
                indent=2,
            )

        # default
        return json.dumps({"mock": True, "id": digest, "message": "OK", "echo_hash": digest}, indent=2)


def parse_json_loose(text: str) -> Any:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start : end + 1])
        raise


def rate_limit_sleep(seconds: float = 0.3) -> None:
    time.sleep(seconds)
