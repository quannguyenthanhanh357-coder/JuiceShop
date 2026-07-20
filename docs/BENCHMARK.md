# Benchmark — Eval Juice Shop Challenges (Tuần 10)

Chạy:

```bash
python agents/eval_pipeline.py
# → data-lake/eval_report.json
```

## Ground truth (10 challenges)

| # | Challenge | Signals kỳ vọng |
|---|---|---|
| 1 | Login Admin | admin, login, password |
| 2 | Union SQL Injection | sql, union, search |
| 3 | DOM XSS | xss, script, search |
| 4 | Score Board | score, challenge |
| 5 | Admin Registration | register, role, admin |
| 6 | View Basket (IDOR) | basket, idor |
| 7 | Forged Feedback | feedback, xss |
| 8 | JWT Issues | jwt, token, role |
| 9 | Directory Listing FTP | ftp, directory |
| 10 | Exposed Metrics | metrics, prometheus |

## Cách chấm

1. Agent hypothesis (MOCK JSON).  
2. LLM-as-judge (MOCK) + rule: ≥1 signal trong output.  
3. `final_score >= 0.6` → detected.

## Kỳ vọng demo (MOCK)

Detect rate thường **≥ 80%** vì mock + rule bám signals.
Với OpenAI thật: so sánh lại và chỉnh prompt Recon nếu FP/FN cao.

## Retrieval (RAG)

```bash
python rag/evaluate_retrieval.py
# → rag/store/retrieval_eval.json
```

Mục tiêu: ≥ 8/10 câu hỏi gold có doc đúng trong top-3 (hybrid).
