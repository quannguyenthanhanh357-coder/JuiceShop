# PRD — Project Sentinel

## Problem

Đội bảo mật nhỏ không đủ bandwidth pentest liên tục trên mọi release. SAST/DAST tạo nhiều finding nhưng thiếu ngữ cảnh ưu tiên và chứng minh khai thác an toàn trên staging.

## Solution

Project Sentinel = **DevSecOps baseline + AI-assisted pentest syndicate** chạy trên OWASP Juice Shop (Compose local):

1. CI Semgrep + ZAP → data-lake  
2. Kong IAM cho agent identities  
3. RAG threat intel  
4. Multi-agent Recon → Fuzz → Exploit (HITL)  
5. Guardrails, PII redaction, eval pipeline  

## Users

- Intern / junior AppSec học thực chiến an toàn  
- Mentor đánh giá deliverable 12 tuần  

## Architecture (Compose)

```
Client/Agent → Kong:8000 (key-auth, ACL, rate-limit) → juice-shop:3000
ZAP/debug có thể gọi thẳng :3000
RAG + agents = process Python trên host (mock LLM offline)
```

## Non-goals

- Không pentest hệ thống production/thật  
- Không bắt buộc GPU/vLLM  
- Không thay thế pentest thủ công cấp độ advanced  

## Risks

| Risk | Mitigation |
|---|---|
| Agent tấn công nhầm host | Hardcode localhost / Kong only |
| Prompt injection | Guardrails Tuần 7 |
| Chi phí API | MOCK mode + FinOps log |
| Juice Shop "đỏ" CI | fail_action false / || true |

## Success metrics

- `docker compose up` chạy Juice Shop + Kong  
- Syndicate E2E với MOCK LLM  
- Eval ≥ 70% detect trên 10 challenge ground truth (mock)  
- Tài liệu PRD + Business Case + Runbook  
