#!/usr/bin/env python3
"""
Tuần 9 — PII redaction: email / phone / SSN-like trước khi ghi log hoặc RAG.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
# US-ish phone
PHONE_RE = re.compile(r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b")
# SSN-like ###-##-####
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


def redact(text: str) -> str:
    text = EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    text = PHONE_RE.sub("[REDACTED_PHONE]", text)
    text = SSN_RE.sub("[REDACTED_SSN]", text)
    return text


def redact_file(src: Path, dst: Path) -> None:
    raw = src.read_text(encoding="utf-8", errors="replace")
    dst.write_text(redact(raw), encoding="utf-8")


def demo() -> None:
    sample = (
        "User jane.doe@juiceshop.local phone 555-123-4567 SSN 123-45-6789 "
        "bought Apple Juice."
    )
    print("BEFORE:", sample)
    print("AFTER: ", redact(sample))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--in", dest="infile", type=Path)
    parser.add_argument("--out", dest="outfile", type=Path)
    args = parser.parse_args()
    if args.demo or not args.infile:
        demo()
    else:
        out = args.outfile or args.infile.with_suffix(args.infile.suffix + ".redacted")
        redact_file(args.infile, out)
        print(f"[+] {args.infile} → {out}")
