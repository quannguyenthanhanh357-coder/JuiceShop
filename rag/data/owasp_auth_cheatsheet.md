# OWASP Cheat Sheet — Authentication (tóm tắt)

1. Dùng thư viện auth đã kiểm chứng; hash password (bcrypt/argon2).
2. MFA cho tài khoản nhạy cảm.
3. Rate-limit login; chống credential stuffing.
4. JWT: short TTL, verify signature, không tin role từ client nếu không ký.
5. Secure + HttpOnly + SameSite cookies.

**Juice Shop:** login admin challenge, JWT role manipulation, weak passwords (admin123…).
