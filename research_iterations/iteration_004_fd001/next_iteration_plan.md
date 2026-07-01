# iteration_004_fd001 Next Iteration Plan

## Recommended Next Action

Run a rewrite iteration focused on FD_001 volatility-term persistence burden reduction.

## Candidate Rewrite Directions

- Keep `FD001_H002_VOL_TERM_PERSISTENT_ACUTE_STRESS` as the parent.
- Try pre-declared confirmation overlays that reduce burden without optimizing thresholds:
  - volatility disagreement as context;
  - safe-haven state as context only;
  - stricter persistence combinations with fixed thresholds chosen before testing.
- Preserve H002's acute-shock target: 15BD MDD <= -5%.

## Do Not Repeat

- Do not retest H001 or H004 as direct false-calm triggers against the same target.
- Do not use context-only features as standalone alerts.
- Do not use diagnostics-only repair features as direct triggers.
- Do not optimize thresholds.
- Do not promote to production without human approval.
