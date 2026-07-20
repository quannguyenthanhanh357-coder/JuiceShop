# CVE-2017-5638 — Apache Struts RCE (tóm tắt)

**CVE:** CVE-2017-5638  
**Loại:** RCE qua Content-Type OGNL injection  
**OWASP:** A03 Injection / A06 Components  

Struts2 xử lý Content-Type lỗi → attacker inject OGNL → RCE.
Không có trên Juice Shop stack, nhưng dạy pattern "framework parse header không an toàn".

**Bài học cho agent:** luôn ghi nhận stack/version từ error page (Security Misconfiguration).
