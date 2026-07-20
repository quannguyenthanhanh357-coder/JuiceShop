# Runbook — Project Sentinel

## Start / Stop

```bash
cd Project-Sentinel
docker compose up -d          # image pin (khuyến nghị)
docker compose ps
docker compose logs -f kong
docker compose down
```

Build từ source (Tuần 7 FTP file / sửa juice-shop):

```bash
docker compose -f docker-compose.yml -f docker-compose.from-source.yml up -d --build
```

- App debug/ZAP: http://localhost:3000  
- Agent gateway: http://localhost:8000 (header `apikey`)

## Seed & RAG

```bash
pip install -r requirements.txt
python scripts/seed_sample_reports.py
python rag/ingest.py
python rag/evaluate_retrieval.py
```

## Agents (MOCK nếu không có OPENAI_API_KEY)

```bash
python agents/run_syndicate.py          # HITL auto-approve + injection before/after
python agents/run_syndicate.py --interactive-hitl
python agents/exploit_agent.py --reject-demo   # Tuần 8 reject evidence
python agents/pii_redaction.py --demo
python agents/eval_pipeline.py --both
python agents/mcp_server_stub.py        # :8765
```

Demo checklist: `docs/DEMO_CHECKLIST.md`.

## Kong IAM & rate limit

```bash
python scripts/test_kong_iam.py
python scripts/test_kong_rate_limit.py
```

Keys: `recon-key-demo` (GET), `exploit-key-demo` (POST + rate-limit).

## FinOps

```bash
python scripts/finops_report.py
```

## Sự cố thường gặp

| Triệu chứng | Xử lý |
|---|---|
| Kong 502 | Đợi juice-shop healthy; `compose restart kong` |
| 401 mọi request | Thiếu header `apikey` |
| 403 POST với recon key | Đúng thiết kế ACL |
| Fuzz timeout | `compose ps`; chỉ dùng localhost |
| RAG 0 docs | `python rag/ingest.py` |
| UnicodeEncodeError Windows | `$env:PYTHONIOENCODING="utf-8"` |
| Build juice-shop lâu | Dùng image pin; `--build` chỉ khi sửa source |

## An toàn

Chỉ tấn công service trong Compose. Không đổi `SENTINEL_KONG` sang host ngoài.
