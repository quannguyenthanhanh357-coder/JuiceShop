# Project Sentinel

## Mục tiêu dự án
Project Sentinel là một dự án thực tập nhằm xây dựng hạ tầng cơ bản và thiết lập các tiêu chuẩn bảo mật (Security Baseline) thông qua việc tích hợp các quy trình kiểm tra tự động vào CI/CD pipeline. 

Mục tiêu cụ thể trong giai đoạn đầu:
- **Triển khai ứng dụng mục tiêu**: Khởi chạy thành công OWASP Juice Shop trên môi trường giả lập (localhost/staging).
- **Thiết lập CI/CD & DevSecOps**: Tích hợp các luồng quét tự động (GitHub Actions) để kiểm tra mã nguồn (SAST) sử dụng Semgrep/SonarQube.
- **Quét lỗ hổng động (DAST)**: Sử dụng OWASP ZAP để dò quét các điểm yếu bảo mật trên ứng dụng đang chạy.
- **Quản lý dữ liệu lỗ hổng**: Thu thập và gom nhóm các kết quả quét (JSON/XML) vào hệ thống lưu trữ tập trung (Data Lake/SQLite) để tiến hành phân tích bề mặt tấn công (Attack Surface).

Dự án này giúp củng cố kiến thức về bảo mật ứng dụng web và khả năng tự động hóa trong an toàn thông tin.
