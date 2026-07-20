# CVE-2019-9193 — PostgreSQL COPY TO/FROM PROGRAM (tóm tắt)

**CVE:** CVE-2019-9193 (minh họa class RCE via SQL feature)  
**Loại:** Command execution qua SQL superuser  
**OWASP:** A03 Injection  

Khi DB user có quyền cao, `COPY ... PROGRAM` có thể chạy lệnh OS.
Juice Shop dùng SQLite — không áp dụng trực tiếp, nhưng Union SQLi vẫn đọc bảng Users.

**Liên hệ Juice Shop:** challenge Union SQL Injection trên `/rest/products/search?q=`.
