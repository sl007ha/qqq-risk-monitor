# Codex Stage Task: {{stage}}

Use Superpowers and evidence-over-claims.

Task ID: {{task_id}}
Title: {{title}}

## Objective

{{objective}}

## Inputs

{{inputs}}

## Required Outputs

{{outputs}}

## Allowed Files

{{allowed_files}}

## Blocked Files

{{blocked_files}}

## Gates

{{gates}}

## Validators

{{validators}}

## Stage Routing

- Next stage on pass: {{next_stage_on_pass}}
- Next stage on fail: {{next_stage_on_fail}}
- Human approval required: {{human_approval_required}}

## Task Contract

- Audit availability, coverage, leakage, redundancy, and implementation complexity.
- Treat live text features as current-context-only unless a point-in-time archive exists.
- Do not implement features or run tests in this stage.

## Machine Context

```yaml
{{task_yaml}}
```
