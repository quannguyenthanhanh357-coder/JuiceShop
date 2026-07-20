# Demo day checklist — Project Sentinel

Chạy trên máy có Docker + Python 3.10+. **Không cần** `OPENAI_API_KEY` (MOCK).

## 1. Staging

```bash
cd Project-Sentinel
docker compose up -d
docker compose ps
# http://localhost:3000  Juice Shop
# http://localhost:8000  Kong
```

## 2. Seed + RAG

```bash
pip install -r requirements.txt
python scripts/seed_sample_reports.py
python rag/ingest.py
python rag/evaluate_retrieval.py
```

Kỳ vọng: hybrid accuracy ≥ 80%, có P@3 / MRR trong `rag/store/retrieval_eval.json`.

## 3. Syndicate E2E

```bash
python agents/run_syndicate.py
```

Artifacts: `attack_surface_map.json`, `fuzz_findings.json` (có `mutations`), `exploit_result.json`, `syndicate_summary.json`, `injection_before.json` / `injection_after.json`.

## 4. HITL reject (Tuần 8)

```bash
python agents/exploit_agent.py --reject-demo
# hoặc: python agents/hitl_cli.py --reject-demo
```

## 5. PII + Eval + FinOps + Kong

```bash
python agents/pii_redaction.py --demo
python agents/eval_pipeline.py --both
python scripts/finops_report.py
python scripts/test_kong_iam.py
python scripts/test_kong_rate_limit.py
```

## 6. Nói với người xem (30s)

1. CI Semgrep+ZAP trên GitHub Actions.  
2. Kong tách recon (GET) / exploit (POST+RL).  
3. Agents MOCK + guardrail FTP + HITL + PII redaction.  
4. Eval baseline→improved; FinOps CSV $0 khi MOCK.

Keys demo: `recon-key-demo`, `exploit-key-demo`.
