# CVE-2021-44228 — Log4Shell (tóm tắt giáo dục)

**CVE:** CVE-2021-44228  
**Loại:** Remote Code Execution qua JNDI lookup trong Log4j  
**OWASP:** A06 Vulnerable Components / A03 Injection  

Log4j phiên bản cũ parse `${jndi:ldap://...}` trong log message → server kết nối attacker → RCE.

**Liên hệ Juice Shop:** không dùng Log4j, nhưng challenge "Vulnerable Library" minh họa dependency lỗi thời.
Payload kiểu JNDI chỉ demo trên lab local, không gửi ra internet.

**Mitigation:** nâng Log4j ≥ 2.17, tắt lookups, WAF rule chặn `${jndi:`.
