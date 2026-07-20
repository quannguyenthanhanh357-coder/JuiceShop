# Attack Surface — OWASP Juice Shop (thủ công, Tuần 1)

> Target: `http://localhost:3000` (direct) / `http://localhost:8000` (qua Kong).
> Chỉ phân tích môi trường Compose local — không quét host ngoài.

## Tổng quan

Juice Shop là web shop cố ý insecure (Node/Express + Angular + SQLite).
Attack surface chính nằm ở REST API (`/rest/*`), REST-ish API (`/api/*`), auth, và vài endpoint admin/debug.

## Auth & Session

| Endpoint | Method | Ghi chú |
|---|---|---|
| `/rest/user/login` | POST | Login email/password → JWT |
| `/rest/user/security-question` | GET | Reset password flow |
| `/rest/user/reset-password` | POST | Đổi mật khẩu qua security Q |
| `/api/Users` | POST | Đăng ký user mới |
| Cookie / `Authorization: Bearer` | — | JWT thường dễ decode; role trong token |

**Rủi ro:** weak password, JWT manipulation, đăng ký với `role: admin` (challenge Register Admin).

## `/rest/*` (business logic)

| Endpoint | Method | Rủi ro điển hình |
|---|---|---|
| `/rest/products/search?q=` | GET | **SQLi** (Union SQLi challenge), XSS reflected |
| `/rest/products/{id}/reviews` | GET/PUT | NoSQL / forged review |
| `/rest/basket/{id}` | GET | IDOR — xem basket user khác |
| `/rest/basket/{id}/checkout` | POST | Logic giá / coupon |
| `/rest/user/change-password` | GET | Authz yếu |
| `/rest/admin/application-configuration` | GET | Info leak nếu bypass authz |
| `/rest/memories` | GET | PII / image metadata |

## `/api/*` (Sequelize REST)

| Endpoint | Method | Rủi ro |
|---|---|---|
| `/api/Users` | GET/POST | Mass assignment, enum users, register admin |
| `/api/Users/{id}` | GET/PUT/DELETE | IDOR, privilege escalation |
| `/api/Products` | GET | Data exposure |
| `/api/Feedbacks` | POST | XSS stored trong feedback |
| `/api/Challenges` | GET | Score board / meta |
| `/api/Quantitys` | — | Inventory race |

## Injection surfaces

1. **SQLi search** — `GET /rest/products/search?q=<payload>`  
   Payload giáo dục (localhost only): `' OR 1=1--`, Union select trên bảng Users.
2. **XSS** — search box, feedback, product reviews. Payload demo: `<iframe src="javascript:alert(`xss`)">`.
3. **NoSQL / JSON injection** — review update với operator `$ne` / forged author.

## Admin & sensitive

| Đường dẫn | Ghi chú |
|---|---|
| `/#/administration` | UI admin — cần role |
| `/rest/admin/*` | API admin |
| `/ftp/` | Directory listing — file nhạy cảm (Tuần 7: `sentinel_indirect_injection.txt`) |
| `/metrics` | Prometheus metrics exposed (challenge) |
| `/encryptionkeys/` | Key files có thể lộ |

## So với SAST/DAST sample

Seed report (`scripts/seed_sample_reports.py`) đã gắn SQLi + XSS trên search — khớp note này.
Agent Recon (Tuần 4) nên map lại các endpoint trên thành JSON Attack Surface Map.
