#!/usr/bin/env python3
"""
Tuần 2 (tuỳ chọn) — MCP server stub (stdlib HTTP).
Tool: get_scan_results — đọc data-lake SQLite / JSON.
Chạy: python agents/mcp_server_stub.py
GET http://127.0.0.1:8765/tools/get_scan_results
"""
from __future__ import annotations

import json
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data-lake" / "vuln_data.db"
HOST, PORT = "127.0.0.1", 8765


def get_scan_results(limit: int = 50) -> dict:
    if not DB.exists():
        return {"ok": False, "error": "no database — run scripts/seed_sample_reports.py", "results": []}
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, tool, severity, name, description, path_or_url, timestamp "
        "FROM vulnerabilities ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return {"ok": True, "count": len(rows), "results": [dict(r) for r in rows]}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        print(f"[mcp-stub] {args[0]}")

    def _json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path in ("/", "/health"):
            self._json(200, {"service": "sentinel-mcp-stub", "tools": ["get_scan_results"]})
            return
        if path == "/tools/get_scan_results":
            self._json(200, get_scan_results())
            return
        self._json(404, {"error": "not found"})


def main() -> None:
    httpd = HTTPServer((HOST, PORT), Handler)
    print(f"[*] MCP stub listening http://{HOST}:{PORT}/tools/get_scan_results")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
