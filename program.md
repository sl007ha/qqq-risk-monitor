# QQQ Risk Monitor v1.3.1 — Autoresearch-Style Local Port

Current phase: **dashboard port only**.

Goal:
- Rewrite the Colab dashboard into an autoresearch-style local codebase.
- The local runner should reproduce the same R2 × MMDI calculation logic as the Colab notebook.
- Output a single HTML dashboard plus CSV artifacts.

Run:

```bash
python run_dashboard.py --output-dir outputs
```

Important governance:
- Do not optimize signals in this phase.
- Do not add new features in this phase.
- Do not change thresholds in this phase.
- Do not change data sources unless explicitly requested.

Autoresearch structure:
- `prepare.py` freezes raw data and feature construction.
- `qqq_autoresearch/candidate.py` contains the candidate signal logic. In a future optimization phase, this should be the only file an AI agent modifies.
- `run_experiment.py` provides a stable runner compatible with future autoresearch loops.
- `run_dashboard.py` is the production-style local entry point for dashboard generation.

Validation for this phase:
- Code imports successfully.
- `python run_dashboard.py --output-dir outputs` completes locally with internet access.
- `outputs/qqq_r2_mmdi_v1_3_1_dashboard.html` is created.
- CSV artifacts are created in the same output directory.
