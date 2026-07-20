# Project Sentinel

Hạ tầng DevSecOps + AI-assisted pentest thực hành trên **OWASP Juice Shop** (staging giả lập bằng Docker Compose).

## Phiên bản target

| Mục | Giá trị |
|---|---|
| Juice Shop | **v20.1.1** |
| Commit | `f915bddd82790d0f3018902d36ae9b4241a5f51f` |
| Pin file | `juice-shop/.sentinel-pin` |
| Staging URL | http://localhost:3000 |

## Cấu trúc thư mục

```
Project-Sentinel/
├── juice-shop/              # Source OWASP Juice Shop (đã clone, pin v20.1.1)
├── docker-compose.yml       # Deploy giả lập staging
├── .github/workflows/       # CI: SAST (Semgrep) + DAST (ZAP)
├── scripts/                 # parse_results.py → SQLite data-lake
├── data-lake/               # Báo cáo / DB lỗ hổng
│   └── reports/
├── agents/                  # (Tuần 4+) AI agents
├── rag/                     # (Tuần 3+) RAG pipeline
├── docs/notes/              # Attack Surface notes, nhật ký
└── README.md
```

## Chạy staging (Docker Compose)

```bash
docker compose up -d --build
# Mở http://localhost:3000
docker compose ps
docker compose logs -f juice-shop
docker compose down
```

> Lần build đầu từ source có thể mất nhiều phút. Trong CI, DAST dùng image `bkimminich/juice-shop:v20.1.1` (cùng version) để nhanh hơn.

## Gom kết quả scan vào data-lake

```bash
python scripts/parse_results.py --semgrep semgrep-report.json --zap zap-report.json --db data-lake/vuln_data.db
```

## Tiến độ (theo kế hoạch 12 tuần)

Xem checklist chi tiết trong repo gốc `Ke_Hoach_Chi_Tiet_Thuc_Tap_Project_Sentinel.md`.

| Tuần | Nội dung | Trạng thái |
|---|---|---|
| 0 | Clone Juice Shop + Compose + cấu trúc folder | ✅ Xong (Compose đã chạy localhost:3000) |
| 1 | SAST/DAST CI + parse script + data-lake | **Skeleton có sẵn** — cần verify end-to-end |
| 2–12 | Kong, RAG, Agents, Guardrails… | Chưa bắt đầu |

## Mục tiêu giai đoạn 1

- Triển khai Juice Shop trên localhost qua Compose
- CI quét SAST (Semgrep trên `juice-shop/`) + DAST (ZAP)
- Gom kết quả vào data-lake (SQLite) để phân tích Attack Surface
