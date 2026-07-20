# Benchmark — Eval Juice Shop Challenges (Tuần 10)

```bash
python agents/eval_pipeline.py --both
# → data-lake/eval_report.json (baseline)
# → data-lake/eval_report_improved.json
# → data-lake/eval_improvement.json
```

## Cách chấm (không circular)

1. Gom **corpus** từ `attack_surface_map.json` + `vuln_data.db` + fuzz + excerpt `ATTACK_SURFACE.md`.
2. Hypothesis = keyword hits trên corpus (baseline vs improved synonym map) — **không** copy sẵn `GROUND_TRUTH.signals` vào output.
3. Detect khi có matched keywords **và** ≥1 ground-truth signal xuất hiện trong hypothesis text.
4. FP = `detected_candidate` nhưng `signal_hits == 0`.

## Ground truth (10 challenges)

| # | Challenge | Signals |
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

## Vòng cải thiện prompt/rule

| Mode | Keyword map |
|---|---|
| baseline | `BASELINE_KEYWORDS` trong `eval_pipeline.py` |
| improved | thêm path aliases / CWE synonyms (`IMPROVED_KEYWORDS`) |

Ghi `eval_improvement.json`: `delta = improved_detect_rate - baseline_detect_rate`.

Ví dụ lần verify local (MOCK, corpus map+DB vs +ATTACK_SURFACE note):

| Mode | Detect | FP |
|---|---|---|
| baseline | 70% (7/10) | 0 |
| improved | 100% (10/10) | 0 |
| **delta** | **+30%** | — |

## Retrieval (RAG)

```bash
python rag/evaluate_retrieval.py
```

Metrics: accuracy, **Precision@3**, **MRR** (hybrid BOW+BM25).
