#!/usr/bin/env python3
"""
Tuần 6 — Supervisor: chia việc Recon → Fuzz → Exploit.
Message format chuẩn: {from, to, task, data}
"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "agents"))

from common import write_trace  # noqa: E402


@dataclass
class Message:
    from_: str
    to: str
    task: str
    data: Any

    def to_dict(self) -> dict:
        return {"from": self.from_, "to": self.to, "task": self.task, "data": self.data}


class Supervisor:
    def __init__(self) -> None:
        self.inbox: list[dict] = []

    def send(self, msg: Message) -> None:
        d = msg.to_dict()
        self.inbox.append(d)
        write_trace("supervisor", "message", d)
        print(f"  MSG {d['from']} → {d['to']} | {d['task']}")

    def run_pipeline(self, auto_approve: bool = True) -> dict:
        from fuzz_agent import run_fuzz
        from exploit_agent import run_exploit
        from recon_agent import run_recon

        self.send(Message("supervisor", "recon", "map_attack_surface", {"source": "data-lake"}))
        surface = run_recon()
        self.send(Message("recon", "supervisor", "attack_surface_done", surface))

        self.send(Message("supervisor", "fuzz", "fuzz_from_surface", {"map": "attack_surface_map.json"}))
        findings = run_fuzz(max_requests=6)
        self.send(Message("fuzz", "supervisor", "fuzz_done", {"count": len(findings)}))

        self.send(Message("supervisor", "exploit", "prove_finding", {"need_hitl": True}))
        exploit = run_exploit(auto_approve=auto_approve)
        self.send(Message("exploit", "supervisor", "exploit_done", exploit.get("status")))

        summary = {
            "messages": self.inbox,
            "surface_endpoints": len(surface.get("endpoints", [])),
            "fuzz_count": len(findings),
            "exploit_status": exploit.get("status"),
        }
        path = ROOT / "data-lake" / "syndicate_summary.json"
        path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[+] Syndicate summary → {path}")
        return summary


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--interactive-hitl", action="store_true")
    args = parser.parse_args()
    Supervisor().run_pipeline(auto_approve=not args.interactive_hitl)


if __name__ == "__main__":
    main()
