# Runbook — Project Sentinel

## Start / Stop

```bash
cd Project-Sentinel
docker compose up -d --build    # juice-shop + kong
docker compose ps
docker compose logs -f kong
docker compose down
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
python agents/run_syndicate.py          # HITL auto-approve
python agents/run_syndicate.py --interactive-hitl
python agents/eval_pipeline.py
python agents/mcp_server_stub.py        # :8765
```

## Kong IAM test

```bash
python scripts/test_kong_iam.py
```

Keys demo: `recon-key-demo` (GET), `exploit-key-demo` (POST + rate-limit).

## Sự cố thường gặp

| Triệu chứng | Xử lý |
|---|---|
| Kong 502 | Đợi juice-shop healthy; `compose restart kong` |
| 401 mọi request | Thiếu header `apikey` |
| 403 POST với recon key | Đúng thiết kế ACL |
| Fuzz timeout | `compose ps`; chỉ dùng localhost |
| RAG 0 docs | `python rag/ingest.py` |
| Build juice-shop lâu | Dùng image pin, chỉ `--build` khi sửa source (Tuần 7) |

## An toàn

Chỉ tấn công service trong Compose. Không đổi `SENTINEL_KONG` sang host ngoài.
