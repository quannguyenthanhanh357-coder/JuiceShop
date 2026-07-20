# OWASP Cheat Sheet — SQL Injection Prevention (tóm tắt)

1. Dùng prepared statements / parameterized queries — không nối chuỗi SQL.
2. Stored procedures an toàn chỉ khi không ghép dynamic SQL bên trong.
3. Allow-list validate input (kiểu, độ dài, charset).
4. Escape chỉ là lớp phụ, không thay parameterization.
5. Least privilege cho DB account ứng dụng.

**Juice Shop:** `/rest/products/search` cố ý nối query → SQLi challenge.
Agent fuzz nên thử `'`, `"`, `OR 1=1`, UNION SELECT — chỉ localhost.
