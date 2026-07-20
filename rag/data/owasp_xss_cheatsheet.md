# OWASP Cheat Sheet — XSS Prevention (tóm tắt)

1. Encode output theo context (HTML, JS, URL, CSS).
2. Content-Security-Policy (CSP) giảm impact.
3. HttpOnly cookies giảm steal session qua XSS.
4. Không dùng `innerHTML` với dữ liệu user chưa sanitize.
5. Framework auto-escape (Angular) vẫn có thể bypass bằng bypassSecurityTrust*.

**Juice Shop:** DOM XSS / reflected XSS trên search và feedback.
Payload giáo dục: `<script>alert(1)</script>`, iframe javascript URI.
