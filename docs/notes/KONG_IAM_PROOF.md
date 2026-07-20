# Kong IAM Proof (Tuần 2)

Chạy: `python scripts/test_kong_iam.py` (Compose up, Kong healthy).

## Kết quả (2026-07-20)

```
[*] Test Kong IAM (chỉ localhost:8000)

  [PASS] GET không key → 401 — got 401
  [PASS] Recon GET products → 2xx — got 200
  [PASS] Recon POST /api/Users → 403 — got 403
  [PASS] Exploit POST /api/Users → không 401/403 Kong — got 400

[*] Kết quả: 4/4 PASS
```

| Case | Kỳ vọng | Thực tế |
|---|---|---|
| No API key | 401 | 401 |
| `recon-key-demo` GET | 2xx | 200 |
| `recon-key-demo` POST | 403 ACL | 403 |
| `exploit-key-demo` POST | không bị Kong 401/403 | 400 (app validation — IAM OK) |

Keys demo: xem `kong/kong.yml`. Rate-limit write: `docs/notes/KONG_RATE_LIMIT_PROOF.md`.
