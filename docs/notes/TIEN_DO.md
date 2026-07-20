# Tiến độ Project Sentinel

Cập nhật: 2026-07-20 (honest-done pass)

## Kết luận ngắn

**Tuần 0–12: verified demo local + CI.** LLM mặc định **MOCK**. Guardrails/PII/HITL/eval improvement/FinOps CSV đã nối vào pipeline. Traffic agent qua Kong `localhost:8000`.

## Chi tiết theo tuần

### Tuần 0 — Chuẩn bị nền tảng
| Hạng mục | Trạng thái | Ghi chú |
|---|---|---|
| Clone Juice Shop v20.1.1 + Compose | ✅ | localhost:3000 |
| Cấu trúc folder | ✅ | |

### Tuần 1 — SAST/DAST + CI/CD
| Hạng mục | Trạng thái | Ghi chú |
|---|---|---|
| CI Semgrep/ZAP | ✅ verified | [Run 29714467839](https://github.com/quannguyenthanhanh357-coder/JuiceShop/actions/runs/29714467839) |
| `parse_results.py` + seed | ✅ | → `vuln_data.db` |
| `ATTACK_SURFACE.md` | ✅ | |

### Tuần 2 — Kong & IAM
| Hạng mục | Trạng thái | Ghi chú |
|---|---|---|
| Kong + keys ACL | ✅ | `kong/kong.yml` |
| `test_kong_iam.py` | ✅ | proof: `docs/notes/KONG_IAM_PROOF.md` |
| MCP stub | ✅ | |

### Tuần 3 — RAG
| Hạng mục | Trạng thái | Ghi chú |
|---|---|---|
| ingest / hybrid BOW+BM25 | ✅ | Recon dùng `hybrid_search` |
| Eval accuracy + P@3 + MRR | ✅ | `rag/evaluate_retrieval.py` |

### Tuần 4–6 — Agents
| Hạng mục | Trạng thái | Ghi chú |
|---|---|---|
| Recon DB-driven + so sánh manual | ✅ | `RECON_VS_MANUAL.md` |
| Fuzz mutate-on-anomaly | ✅ | + `KONG_RATE_LIMIT_PROOF.md` |
| Supervisor + file traces | ✅ | `docs/notes/TRACING.md` |

### Tuần 7–9 — Bảo vệ AI
| Hạng mục | Trạng thái | Ghi chú |
|---|---|---|
| Injection before/after | ✅ | `injection_before.json` / `after.json` |
| HITL approve + reject | ✅ | `--reject-demo` |
| PII trong traces + GDPR note | ✅ | `docs/PII_GDPR_NOTE.md` |

### Tuần 10–12 — LLMOps & bàn giao
| Hạng mục | Trạng thái | Ghi chú |
|---|---|---|
| Eval non-circular + improvement | ✅ | `eval_improvement.json` |
| FinOps CSV + alert threshold | ✅ | `scripts/finops_report.py` |
| PRD / Business / Demo checklist | ✅ | `docs/DEMO_CHECKLIST.md` |

## Mock mode

- Không set `OPENAI_API_KEY` → `LLMClient.mock = True`.
- Demo: `docs/DEMO_CHECKLIST.md` + `docs/RUNBOOK.md`.
