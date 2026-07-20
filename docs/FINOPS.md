# FinOps — Project Sentinel (Tuần 11)

## Nguyên tắc

- Mặc định **MOCK LLM** → $0 token.
- Bật OpenAI chỉ khi demo cần chất lượng thật.
- Không thuê GPU cloud cho thực tập.

## Telemetry

`LLMClient` ghi vào traces:

- `est_tokens_in` / `est_tokens_out` (~4 chars/token)
- `est_cost_usd` (MOCK = 0; real dùng `SENTINEL_COST_IN_PER_1M` / `OUT`)

```bash
python scripts/finops_report.py
# → data-lake/finops_weekly.csv
# ALERT nếu tổng est_cost_usd > SENTINEL_COST_ALERT_USD (mặc định 5)
```

## Ước lượng (khi dùng API)

| Hoạt động | Token TB | Cost ví dụ |
|---|---|---|
| 1× Recon | ~2k | < $0.01 |
| Full syndicate + eval | ~25k | ~$0.02–0.05 |

## Monitoring tối giản

- Trace JSONL: `data-lake/traces/`
- CSV FinOps: `data-lake/finops_weekly.csv`
- Compose: `docker stats sentinel-juice-shop sentinel-kong`
- Alert: script exit code 2 nếu vượt ngưỡng — tắt API key, về MOCK

## Tối ưu

1. Truncate vuln context trong recon.  
2. `--max` / `--mutate` giới hạn fuzz.  
3. Cache RAG ingest.  
4. Kong write rate-limit + client sleep GET.
