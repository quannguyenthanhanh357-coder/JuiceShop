# Project Sentinel

Hạ tầng DevSecOps + AI-assisted pentest thực hành trên **OWASP Juice Shop** (staging giả lập bằng Docker Compose).

## Phiên bản target

| Mục | Giá trị |
|---|---|
| Juice Shop | **v20.1.1** |
| Commit | `f915bddd82790d0f3018902d36ae9b4241a5f51f` |
| Pin file | `juice-shop/.sentinel-pin` |
| App (ZAP/debug) | http://localhost:3000 |
| Kong (agents) | http://localhost:8000 |

## Cấu trúc thư mục

```
Project-Sentinel/
├── juice-shop/              # Source OWASP Juice Shop (pin v20.1.1)
├── kong/kong.yml            # Key-auth + ACL (recon GET / exploit POST)
├── docker-compose.yml       # juice-shop + Kong (db-less)
├── .github/workflows/       # CI: Semgrep + ZAP
├── scripts/                 # parse, seed reports, test Kong IAM
├── data-lake/               # reports, SQLite, traces, agent outputs
├── agents/                  # Recon / Fuzz / Exploit / Supervisor / guardrails
├── rag/                     # ingest, hybrid search, eval retrieval
├── docs/                    # PRD, Business Case, Runbook, FinOps, Benchmark
└── README.md
```

## Chạy staging

```bash
# Khuyến nghị: dùng image pin (không build — tránh npm ECONNRESET)
docker compose up -d
# http://localhost:3000  — Juice Shop
# http://localhost:8000  — Kong gateway
docker compose ps
docker compose down
```

Build từ source (chỉ khi sửa `juice-shop/`, VD Tuần 7):

```bash
docker compose -f docker-compose.yml -f docker-compose.from-source.yml up -d --build
```

## Python setup & demo offline (MOCK LLM)

Không cần `OPENAI_API_KEY` — agents trả JSON deterministic.

```bash
pip install -r requirements.txt
python scripts/seed_sample_reports.py
python rag/ingest.py && python rag/evaluate_retrieval.py
python agents/run_syndicate.py          # auto HITL
python agents/eval_pipeline.py
python scripts/test_kong_iam.py         # cần compose up
```

API keys Kong demo: `recon-key-demo` (GET), `exploit-key-demo` (POST).

## Tiến độ (12 tuần)

| Tuần | Nội dung | Trạng thái |
|---|---|---|
| 0 | Clone Juice Shop + Compose | ✅ Done |
| 1 | SAST/DAST CI + parse + Attack Surface + seed reports | ✅ CI verified + demo |
| 2 | Kong IAM + `test_kong_iam.py` + MCP stub | ✅ Skeleton + demo |
| 3 | RAG ingest / hybrid / retrieval eval | ✅ Skeleton + demo (BOW fallback) |
| 4 | Recon Agent → Attack Surface Map | ✅ Skeleton + demo (mock LLM) |
| 5 | Fuzz Agent qua Kong rate-limit | ✅ Skeleton + demo |
| 6 | Multi-agent Supervisor + traces | ✅ Skeleton + demo |
| 7 | Indirect prompt injection + guardrails | ✅ Skeleton + demo |
| 8 | HITL CLI approve/reject | ✅ Skeleton + demo |
| 9 | PII redaction | ✅ Skeleton + demo |
| 10 | Eval pipeline 10 challenges | ✅ Skeleton + demo |
| 11 | Full Compose + FinOps + Runbook | ✅ Skeleton + demo |
| 12 | PRD + Business Case | ✅ Skeleton + demo |

Chi tiết nhật ký: `docs/notes/TIEN_DO.md`. Runbook: `docs/RUNBOOK.md`.

**Tài liệu kiến thức Security (HTML):** mở file
`C:\Users\ADMIN\Desktop\VInSOC\Project_Sentinel_Kien_Thuc_Security.html` trên trình duyệt.

## An toàn

Mọi fuzz/exploit **chỉ** nhắm `localhost` / dịch vụ Compose. Không tấn công host ngoài.
