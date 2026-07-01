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

- Do not modify blocked files.
- Do not run hypothesis tests unless this stage explicitly requires them.
- Do not modify production dashboard logic.
- Use exact file evidence in the final response.

## Machine Context

Task YAML:

```yaml
{{task_yaml}}
```

Stage YAML:

```yaml
{{stage_yaml}}
```
