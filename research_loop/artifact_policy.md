# Research Artifact Policy

This policy keeps the research loop reproducible without turning the repository into a store for every regenerated data table.

## Commit By Default

- Source scripts
- YAML manifests
- Inventory summaries
- Coverage summaries
- Validation summaries
- `next_step_recommendation.md`
- Small audit files
- Prompt templates
- Reviewers
- Validators

## Do Not Commit By Default

- Large regenerated daily snapshots
- Repeated intermediate batch snapshots when a combined snapshot exists
- Raw production outputs
- Temporary Codex scratch files
- API keys or secrets

## Current PR Policy

Do not delete existing FD_001 feature lab artifacts in this hardening patch. They are part of the current draft PR baseline and preserve reviewability for the first frozen research snapshot.

## Recommendation

After the first merged baseline, consider keeping only the `FD_001_combined` full snapshot, or only a manifest plus checksum if the full snapshot can be regenerated deterministically.

For future cycles, consider moving large generated snapshots to GitHub Actions artifacts or local outputs, and add `.gitignore` rules once the storage policy is settled.
