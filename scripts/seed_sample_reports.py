#!/usr/bin/env python3
"""
Tuần 1 — Seed báo cáo Semgrep/ZAP mẫu vào data-lake rồi parse → SQLite.
Không cần chạy scan thật; đủ cho demo RAG/agent offline.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPORTS = os.path.join(ROOT, "data-lake", "reports")
DB = os.path.join(ROOT, "data-lake", "vuln_data.db")


SAMPLE_SEMGREP = {
    "results": [
        {
            "check_id": "javascript.express.security.audit.xss.direct-response-write",
            "path": "juice-shop/routes/search.ts",
            "extra": {
                "severity": "WARNING",
                "message": "Potential XSS via unsanitized search query reflection.",
            },
        },
        {
            "check_id": "javascript.lang.security.audit.sqli.node-sqli",
            "path": "juice-shop/routes/search.ts",
            "extra": {
                "severity": "ERROR",
                "message": "SQL Injection: user input concatenated into Sequelize query (q param).",
            },
        },
        {
            "check_id": "javascript.express.security.audit.express-check-csurf",
            "path": "juice-shop/server.ts",
            "extra": {
                "severity": "INFO",
                "message": "Missing CSRF protection on state-changing routes.",
            },
        },
    ],
    "errors": [],
}

SAMPLE_ZAP = {
    "site": [
        {
            "@name": "http://localhost:3000",
            "alerts": [
                {
                    "name": "SQL Injection",
                    "riskdesc": "High (High)",
                    "riskcode": "3",
                    "desc": "The q parameter in /rest/products/search appears vulnerable to SQLi.",
                    "instances": [
                        {"uri": "http://localhost:3000/rest/products/search?q='"}
                    ],
                },
                {
                    "name": "Cross Site Scripting (Reflected)",
                    "riskdesc": "Medium (Medium)",
                    "riskcode": "2",
                    "desc": "Search reflects unsanitized input.",
                    "instances": [
                        {
                            "uri": "http://localhost:3000/rest/products/search?q=<script>alert(1)</script>"
                        }
                    ],
                },
                {
                    "name": "Absence of Anti-CSRF Tokens",
                    "riskdesc": "Low (Medium)",
                    "riskcode": "1",
                    "desc": "Forms may lack CSRF tokens.",
                    "instances": [{"uri": "http://localhost:3000/#/login"}],
                },
            ],
        }
    ]
}


def main() -> int:
    os.makedirs(REPORTS, exist_ok=True)
    semgrep_path = os.path.join(REPORTS, "semgrep-sample.json")
    zap_path = os.path.join(REPORTS, "zap-sample.json")

    with open(semgrep_path, "w", encoding="utf-8") as f:
        json.dump(SAMPLE_SEMGREP, f, indent=2)
    with open(zap_path, "w", encoding="utf-8") as f:
        json.dump(SAMPLE_ZAP, f, indent=2)

    print(f"[+] Wrote {semgrep_path}")
    print(f"[+] Wrote {zap_path}")

    parse_script = os.path.join(ROOT, "scripts", "parse_results.py")
    cmd = [
        sys.executable,
        parse_script,
        "--semgrep",
        semgrep_path,
        "--zap",
        zap_path,
        "--db",
        DB,
    ]
    print(f"[*] Running: {' '.join(cmd)}")
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(cmd, cwd=ROOT, env=env)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
