# Tiến độ Project Sentinel

Cập nhật: 2026-07-20

## Kết luận ngắn

**Tuần 0 đã xong.** Đang ở **đầu/giữa Tuần 1**: CI + parse script đã có skeleton; còn verify pipeline trên GitHub và viết Attack Surface note.

## Chi tiết theo tuần

### Tuần 0 — Chuẩn bị nền tảng
| Hạng mục | Trạng thái | Ghi chú |
|---|---|---|
| Docker / Git / GitHub repo | ✅ | Repo `JuiceShop_VinSoc` trên GitHub |
| Clone OWASP Juice Shop vào `juice-shop/` | ✅ | Pin **v20.1.1** (`f915bdd…`) |
| `docker-compose.yml` giả lập staging | ✅ | Build từ `./juice-shop`, port 3000 |
| Cấu trúc folder (agents, rag, data-lake, docs…) | ✅ | Đã tạo kèm `.gitkeep` |
| README mô tả mục tiêu | ✅ | Đã cập nhật |
| Verify `compose up` chạy được trên máy | ✅ | http://localhost:3000 → v20.1.1 |
| Hello Agent / API key LLM | ⬜ | Chưa thấy trong repo |
| Đọc OWASP Top 10 | ⬜ | Ngoài repo — tự check |

### Tuần 1 — SAST/DAST + CI/CD
| Hạng mục | Trạng thái | Ghi chú |
|---|---|---|
| GitHub Actions SAST (Semgrep) | ✅ skeleton | Đã chỉnh quét `juice-shop/` trong repo |
| GitHub Actions DAST (ZAP) | ✅ skeleton | Dùng image pin v20.1.1 trong CI |
| `scripts/parse_results.py` → SQLite | ✅ | Có sẵn |
| `data-lake/` | ✅ folder | Chưa chắc đã có DB/report thật từ lần chạy |
| Attack Surface note thủ công | ⬜ | Chưa có trong `docs/notes/` |
| Verify pipeline xanh trên GitHub | ⬜ | Cần push + kiểm tra Actions |

### Tuần 2+
Chưa bắt đầu (Kong, RAG, Agents, …).

## Việc nên làm tiếp (theo thứ tự)

1. Push thay đổi lên GitHub → xem workflow SAST/DAST chạy trên `juice-shop/`.
2. Tải artifact report → chạy `python scripts/parse_results.py ...` → ghi Attack Surface vào `docs/notes/`.
3. Sang Tuần 2: thêm Kong vào Compose.
