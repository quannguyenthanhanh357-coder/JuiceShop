# FinOps — Project Sentinel (Tuần 11)

## Nguyên tắc

- Mặc định **MOCK LLM** → $0 token.  
- Bật OpenAI chỉ khi demo cần chất lượng thật.  
- Không thuê GPU cloud cho thực tập.

## Đo chi phí (ước lượng)

| Hoạt động | Token TB (input+output) | Cost @ $0.15/1M in + $0.60/1M out (ví dụ) |
|---|---|---|
| 1× Recon | ~2k | < $0.01 |
| 1× Fuzz plan | ~1k | < $0.01 |
| 1× Eval 10 cases | ~15k | ~$0.01–0.02 |
| Full syndicate + eval | ~25k | ~$0.02–0.05 |

Ghi log token thật khi có API: thêm field trong `data-lake/traces/` (LLM client đã trace request/response length).

## Monitoring tối giản

- Trace file: `data-lake/traces/*.jsonl` (latency cảm nhận = timestamp)  
- Compose: `docker stats sentinel-juice-shop sentinel-kong`  
- Alert thủ công: nếu chi phí tuần > $5 → tắt API key, về MOCK  

## Tối ưu

1. Tóm tắt vuln trước khi đưa vào prompt (recon đã truncate 6000 chars).  
2. Giới hạn fuzz `--max`.  
3. Cache RAG ingest; không embed lại mỗi lần.  
4. Rate-limit Kong giảm spam request.
