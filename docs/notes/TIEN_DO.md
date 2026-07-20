# Tiến độ Project Sentinel

Cập nhật: 2026-07-20

## Kết luận ngắn

**Tuần 0–12 đã có skeleton + demo local.** LLM mặc định **MOCK** (không cần `OPENAI_API_KEY`) — phản hồi JSON deterministic để chạy offline. Traffic agent chỉ qua Kong `localhost:8000`.

## Chi tiết theo tuần

### Tuần 0 — Chuẩn bị nền tảng
| Hạng mục | Trạng thái | Ghi chú |
|---|---|---|
| Clone Juice Shop v20.1.1 + Compose | ✅ | localhost:3000 |
| Cấu trúc folder | ✅ | |

### Tuần 1 — SAST/DAST + CI/CD
| Hạng mục | Trạng thái | Ghi chú |
|---|---|---|
| CI Semgrep/ZAP | ✅ verified | Run [29714467839](https://github.com/quannguyenthanhanh357-coder/JuiceShop/actions/runs/29714467839) — Semgrep+ZAP success; artifacts trong `data-lake/ci-artifacts/` |
| `parse_results.py` + seed reports | ✅ | CI reports → `data-lake/vuln_data.db` (Semgrep+ZAP) |
| `ATTACK_SURFACE.md` | ✅ | `docs/notes/` |

### Tuần 2 — Kong & IAM
| Hạng mục | Trạng thái | Ghi chú |
|---|---|---|
| Kong db-less trong Compose | ✅ | port 8000 |
| recon / exploit API keys + ACL | ✅ | `kong/kong.yml` |
| `test_kong_iam.py` | ✅ | |
| MCP stub `get_scan_results` | ✅ | `agents/mcp_server_stub.py` |

### Tuần 3 — RAG
| Hạng mục | Trạng thái | Ghi chú |
|---|---|---|
| ingest / query / hybrid / eval | ✅ | Chroma optional → BOW+BM25 fallback |
| 10-question retrieval eval | ✅ | `rag/evaluate_retrieval.py` |

### Tuần 4–6 — Agents
| Hạng mục | Trạng thái | Ghi chú |
|---|---|---|
| Recon / Fuzz / Exploit / Supervisor | ✅ | mock LLM |
| Traces `data-lake/traces/` | ✅ | |
| `run_syndicate.py` E2E | ✅ | |

### Tuần 7–9 — Bảo vệ AI
| Hạng mục | Trạng thái | Ghi chú |
|---|---|---|
| FTP indirect injection file | ✅ | `juice-shop/ftp/sentinel_indirect_injection.txt` |
| Guardrails | ✅ | regex + classifier |
| HITL CLI | ✅ | |
| PII redaction | ✅ | email/phone/SSN |

### Tuần 10–12 — LLMOps & bàn giao
| Hạng mục | Trạng thái | Ghi chú |
|---|---|---|
| Eval 10 challenges | ✅ | mock judge |
| FinOps + Runbook | ✅ | `docs/` |
| PRD + Business Case + Benchmark | ✅ | |

## Mock mode

- Không set `OPENAI_API_KEY` → `LLMClient.mock = True`.
- Set key → dùng OpenAI (`openai` package).
- Demo đầy đủ: xem `docs/RUNBOOK.md`.
