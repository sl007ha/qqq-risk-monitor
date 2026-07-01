# Artifact Cleanup Recommendation

No artifacts were deleted in this patch.

## Large Generated Artifacts

Largest current generated feature lab artifacts:

| File | Size bytes | Current role |
|---|---:|---|
| `feature_lab/FD_001_combined/experimental_feature_snapshot.csv` | 1,019,275 | Frozen combined research snapshot |
| `feature_lab/FD_001_batch_A_v2/experimental_feature_snapshot.csv` | 756,121 | Intermediate batch snapshot |
| `feature_lab/FD_001_batch_A/experimental_feature_snapshot.csv` | 719,638 | Superseded intermediate batch snapshot |
| `feature_lab/FD_001_batch_B_v2/experimental_feature_snapshot.csv` | 355,220 | Intermediate batch snapshot used by combined |
| `feature_lab/FD_001_batch_B/experimental_feature_snapshot.csv` | 302,638 | Superseded intermediate batch snapshot |

## Necessary For Reproducibility

- `feature_lab/FD_001_combined/experimental_feature_snapshot.csv`
- `feature_lab/FD_001_combined/experimental_feature_inventory.csv`
- `feature_lab/FD_001_combined/coverage_summary.csv`
- `feature_lab/FD_001_combined/validation_summary.md`
- `feature_lab/FD_001_combined/feature_snapshot_manifest.yaml`
- `feature_lab/FD_001_combined/next_step_recommendation.md`
- Batch A v2 and Batch B v2 scripts and manifests, because they explain how the combined snapshot was produced.

## Could Be Removed In A Future Cleanup PR

Only after the first merged baseline and after validators pass from retained artifacts:

- Superseded intermediate full snapshots under `feature_lab/FD_001_batch_A/`
- Superseded intermediate full snapshots under `feature_lab/FD_001_batch_B/`
- Potentially Batch A v2 and Batch B v2 full CSV snapshots if the combined snapshot plus scripts/manifests are retained.

## Recommended Future Policy

Keep small review artifacts in git: scripts, manifests, inventories, coverage summaries, validation summaries, and next-step recommendations.

For future cycles, store large regenerated daily snapshots as GitHub Actions artifacts or local outputs unless the snapshot is the active frozen research snapshot required for the next stage.
