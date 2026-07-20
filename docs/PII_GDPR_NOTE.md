# PII & GDPR note (Tuần 9) — Project Sentinel

## Mục đích

Lab chỉ dùng dữ liệu giả (Juice Shop / sample). Redaction trước khi persist log/trace để minh họa **data minimization**.

## Biện pháp

| Biện pháp | Cách làm |
|---|---|
| Minimization | Chỉ giữ field cần cho demo (status, path, preview đã cắt) |
| Redaction before persist | `write_trace()` gọi `pii_redaction.redact` trên mọi payload |
| Demo evidence | `data-lake/pii_before.txt` / `pii_after.txt` (`python agents/pii_redaction.py --demo`) |

## Tinh thần GDPR (lab)

1. **Purpose limitation** — PII trong log chỉ để chứng minh pipeline, không dùng marketing.
2. **Storage limitation** — traces local; không đẩy cloud trừ khi mentor yêu cầu.
3. **Integrity & confidentiality** — không commit `.env` / API keys; `.gitignore` che DB runtime.

Đây **không** phải tư vấn pháp lý — chỉ checklist thực tập.
