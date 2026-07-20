# Tracing (Tuần 6) — file JSONL

Project Sentinel dùng **file traces** (không bắt buộc LangSmith/Langfuse).

## Vị trí

`data-lake/traces/{agent}_{YYYYMMDD}.jsonl`

Agents: `recon`, `fuzz`, `exploit`, `supervisor`, `llm`, `eval`.

## Schema

```json
{"ts": "ISO-8601", "agent": "fuzz", "event": "probe", "data": {}}
```

| Field | Ý nghĩa |
|---|---|
| `ts` | UTC timestamp |
| `agent` | tên agent |
| `event` | loại sự kiện (`probe`, `request`, `response`, …) |
| `data` | payload đã **PII-redact** |

## LLM FinOps fields

Trong `event=response` của agent `llm`:

- `est_tokens_in` / `est_tokens_out`
- `est_cost_usd` (MOCK = 0)

Gom báo cáo: `python scripts/finops_report.py` → `data-lake/finops_weekly.csv`.

## Message format syndicate

Supervisor dùng `{from, to, task, data}` — xem `agents/supervisor.py` và `syndicate_summary.json`.
