# Recon vs Manual Attack Surface (Tuần 4)

Agent endpoints: **9** | Manual note paths: **20**

## Overlap

| Path |
|---|
| `/api/Feedbacks` |
| `/api/Users` |
| `/ftp` |
| `/metrics` |
| `/rest/basket/{id}` |
| `/rest/products/search` |

## Chỉ agent

| Path |
|---|
| `/` |
| `/main.js` |
| `/robots.txt` |

## Chỉ manual note

| Path |
|---|
| `/#/administration` |
| `/api/Challenges` |
| `/api/Products` |
| `/api/Quantitys` |
| `/encryptionkeys` |
| `/rest/admin` |
| `/rest/admin/application-configuration` |
| `/rest/basket/{id}/checkout` |
| `/rest/memories` |
| `/rest/products/{id}/reviews` |
| `/rest/user/change-password` |
| `/rest/user/login` |
| `/rest/user/reset-password` |
| `/rest/user/security-question` |

## Kết luận

- Overlap: 6
- Agent-only: 3
- Manual-only: 14 (kỳ vọng — note thủ công rộng hơn DB sample)
- Map source: `vuln_data.db+baseline`, vuln_rows=40
