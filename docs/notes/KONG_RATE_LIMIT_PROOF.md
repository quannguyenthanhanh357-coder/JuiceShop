# Kong Rate Limit Proof (Tuần 5)

Burst POST `/api/Users` với `exploit-key-demo` (limit 20/min trên write service).

```json
{
  "url": "http://localhost:8000/api/Users",
  "requests": 25,
  "status_counts": {
    "201": 19,
    "429": 6
  },
  "got_429": true,
  "note": "Kong write service rate-limit-minute=20; GET fuzz d\u00f9ng client sleep ri\u00eang."
}
```

- Got 429: **True** (6 responses)
- Fuzz Agent (GET) dùng `rate_limit_sleep` phía client — không đi qua plugin write RL.
