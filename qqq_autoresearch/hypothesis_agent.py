"""Ollama-powered hypothesis-generation workflow.

This module reads the local dashboard outputs, builds a compact research context,
asks a local Ollama model to generate structured hypotheses, and writes a human
registry plus a machine-readable JSON/YAML-compatible registry.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from .ollama_client import OllamaClient, OllamaError

REQUIRED_FIELDS = [
    "hypothesis_id",
    "title",
    "plain_english_thesis",
    "economic_market_mechanism",
    "feature_families_used",
    "exact_feature_columns_used",
    "expected_direction",
    "target_horizon",
    "target_type",
    "target_definition",
    "trigger_logic_pseudocode",
    "why_this_should_work",
    "when_this_may_fail",
    "data_quality_or_leakage_risks",
    "minimum_data_coverage_requirement",
    "validation_plan",
    "dashboard_implication",
    "priority_score",
]


def _read_text(path: Path, default: str = "") -> str:
    return path.read_text(encoding="utf-8") if path.exists() else default


def _read_csv(path: Path, max_rows: int | None = None) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    if max_rows is not None:
        return df.head(max_rows)
    return df


def _df_markdown_or_csv(df: pd.DataFrame, max_rows: int = 120, max_cols: int = 12) -> str:
    if df.empty:
        return "<missing or empty>"
    d = df.head(max_rows).copy()
    if len(d.columns) > max_cols:
        d = d.iloc[:, :max_cols]
    try:
        return d.to_markdown(index=False)
    except Exception:
        return d.to_csv(index=False)


def _select_feature_inventory(inventory: pd.DataFrame, max_features: int = 220) -> pd.DataFrame:
    if inventory.empty:
        return inventory
    d = inventory.copy()
    if "coverage_pct" in d.columns:
        d["coverage_pct"] = pd.to_numeric(d["coverage_pct"], errors="coerce")
    if "non_null_count" in d.columns:
        d["non_null_count"] = pd.to_numeric(d["non_null_count"], errors="coerce")
    # Prefer real available features with coverage, but keep some placeholders visible.
    if "non_null_count" in d.columns:
        real = d[d["non_null_count"].fillna(0) > 0].copy()
        placeholder = d[d["non_null_count"].fillna(0) <= 0].copy().head(35)
        sort_cols = [c for c in ["family_guess", "coverage_pct", "non_null_count", "column"] if c in real.columns]
        if sort_cols:
            real = real.sort_values(sort_cols, ascending=[True, False, False, True][: len(sort_cols)])
        d = pd.concat([real.head(max_features), placeholder], ignore_index=True)
    return d


def _latest_snapshot_summary(snapshot: pd.DataFrame, max_rows: int = 160) -> pd.DataFrame:
    if snapshot.empty:
        return snapshot
    keep = [c for c in ["family", "feature", "latest_value", "status", "source_note"] if c in snapshot.columns]
    return snapshot[keep].head(max_rows)


def build_hypothesis_prompt(repo_root: Path, output_dir: Path, max_features: int, n_hypotheses: int) -> str:
    program = _read_text(repo_root / "program_hypothesis_generation.md")
    feature_universe = _read_text(repo_root / "FEATURE_UNIVERSE.md")

    prefix = "qqq_r2_mmdi_v1_3_1"
    inventory = _read_csv(output_dir / f"{prefix}_all_feature_inventory.csv")
    catalog = _read_csv(output_dir / f"{prefix}_feature_catalog.csv")
    latest = _read_csv(output_dir / f"{prefix}_feature_snapshot_latest.csv")
    sentiment_summary = _read_csv(output_dir / f"{prefix}_sentiment_summary.csv")
    sentiment_headlines = _read_csv(output_dir / f"{prefix}_sentiment_headlines.csv", max_rows=40)

    selected_inventory = _select_feature_inventory(inventory, max_features=max_features)
    latest_summary = _latest_snapshot_summary(latest, max_rows=min(max_features, 180))

    prompt = f"""
You are generating a disciplined QQQ Risk Monitor hypothesis registry.

Follow this program exactly:

<PROGRAM>
{program}
</PROGRAM>

Feature-universe documentation:

<FEATURE_UNIVERSE>
{feature_universe}
</FEATURE_UNIVERSE>

Available feature inventory sample. Use column names exactly as shown.

<ALL_FEATURE_INVENTORY_SAMPLE>
{_df_markdown_or_csv(selected_inventory, max_rows=max_features, max_cols=8)}
</ALL_FEATURE_INVENTORY_SAMPLE>

Feature catalog sample:

<FEATURE_CATALOG_SAMPLE>
{_df_markdown_or_csv(catalog, max_rows=220, max_cols=8)}
</FEATURE_CATALOG_SAMPLE>

Latest feature snapshot sample:

<LATEST_FEATURE_SNAPSHOT_SAMPLE>
{_df_markdown_or_csv(latest_summary, max_rows=180, max_cols=6)}
</LATEST_FEATURE_SNAPSHOT_SAMPLE>

Mainstream narrative / semantic summary:

<SENTIMENT_SUMMARY>
{_df_markdown_or_csv(sentiment_summary, max_rows=20, max_cols=10)}
</SENTIMENT_SUMMARY>

Recent mainstream narrative / semantic headlines sample. Remember: live RSS sentiment is current-context only, not historical/backtest-ready.

<SENTIMENT_HEADLINES_SAMPLE>
{_df_markdown_or_csv(sentiment_headlines, max_rows=40, max_cols=8)}
</SENTIMENT_HEADLINES_SAMPLE>

Return ONLY valid JSON. Do not use Markdown fences. Do not include prose outside JSON.

The JSON schema should be:
{{
  "hypotheses": [
    {{
      "hypothesis_id": "H001",
      "title": "...",
      "plain_english_thesis": "...",
      "economic_market_mechanism": "...",
      "feature_families_used": ["..."],
      "exact_feature_columns_used": ["..."],
      "expected_direction": {{"feature_name": "higher_is_worse_or_lower_is_worse_or_context_dependent"}},
      "target_horizon": "15BD/30BD/60BD/126BD",
      "target_type": "path_risk | bearish_return | repair_failure | acute_shock | narrow_leadership_fragility | cross_asset_stress",
      "target_definition": "...",
      "trigger_logic_pseudocode": "...",
      "why_this_should_work": "...",
      "when_this_may_fail": "...",
      "data_quality_or_leakage_risks": "...",
      "minimum_data_coverage_requirement": "...",
      "validation_plan": ["..."],
      "dashboard_implication": "...",
      "priority_score": 1
    }}
  ]
}}

Generate {n_hypotheses} hypotheses.
"""
    return prompt


def _normalize_hypotheses(obj: dict[str, Any]) -> list[dict[str, Any]]:
    hypotheses = obj.get("hypotheses")
    if not isinstance(hypotheses, list):
        raise ValueError("Model JSON must contain a top-level list field named 'hypotheses'.")
    out: list[dict[str, Any]] = []
    for i, h in enumerate(hypotheses, start=1):
        if not isinstance(h, dict):
            continue
        item = {field: h.get(field, "") for field in REQUIRED_FIELDS}
        if not item["hypothesis_id"]:
            item["hypothesis_id"] = f"H{i:03d}"
        try:
            item["priority_score"] = int(float(item.get("priority_score", 0)))
        except Exception:
            item["priority_score"] = 0
        out.append(item)
    return out


def _write_markdown(hypotheses: list[dict[str, Any]], path: Path) -> None:
    lines = ["# QQQ Risk Monitor v2 — Hypothesis Registry", ""]
    lines.append("Generated by a local Ollama model from the local feature inventory. These are research hypotheses only, not trading recommendations.")
    lines.append("")
    for h in hypotheses:
        lines.append(f"## {h['hypothesis_id']} — {h['title']}")
        lines.append("")
        lines.append(f"**Priority score:** {h['priority_score']}/10")
        lines.append("")
        lines.append(f"**Thesis:** {h['plain_english_thesis']}")
        lines.append("")
        lines.append(f"**Mechanism:** {h['economic_market_mechanism']}")
        lines.append("")
        lines.append(f"**Target:** {h['target_type']} / {h['target_horizon']} — {h['target_definition']}")
        lines.append("")
        lines.append("**Features:**")
        for f in h.get("exact_feature_columns_used", []) or []:
            lines.append(f"- `{f}`")
        lines.append("")
        lines.append("**Expected direction:**")
        exp = h.get("expected_direction", {})
        if isinstance(exp, dict):
            for k, v in exp.items():
                lines.append(f"- `{k}`: {v}")
        else:
            lines.append(str(exp))
        lines.append("")
        lines.append(f"**Trigger logic:** `{h['trigger_logic_pseudocode']}`")
        lines.append("")
        lines.append(f"**Why it should work:** {h['why_this_should_work']}")
        lines.append("")
        lines.append(f"**When it may fail:** {h['when_this_may_fail']}")
        lines.append("")
        lines.append(f"**Data / leakage risks:** {h['data_quality_or_leakage_risks']}")
        lines.append("")
        lines.append(f"**Minimum data coverage:** {h['minimum_data_coverage_requirement']}")
        lines.append("")
        lines.append("**Validation plan:**")
        for step in h.get("validation_plan", []) or []:
            lines.append(f"- {step}")
        lines.append("")
        lines.append(f"**Dashboard implication:** {h['dashboard_implication']}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def generate_hypotheses_with_ollama(
    repo_root: Path,
    output_dir: Path,
    hypotheses_dir: Path,
    model: str,
    ollama_url: str,
    n_hypotheses: int = 24,
    max_features: int = 220,
    temperature: float = 0.25,
    num_ctx: int = 32768,
    dry_run_prompt: bool = False,
) -> dict[str, Any]:
    hypotheses_dir.mkdir(parents=True, exist_ok=True)
    prompt = build_hypothesis_prompt(repo_root, output_dir, max_features=max_features, n_hypotheses=n_hypotheses)
    prompt_path = hypotheses_dir / "last_hypothesis_prompt.txt"
    prompt_path.write_text(prompt, encoding="utf-8")

    if dry_run_prompt:
        return {"prompt_path": str(prompt_path), "dry_run": True}

    client = OllamaClient(base_url=ollama_url, model=model)
    client.health_check()
    raw_obj = client.generate_json(
        prompt=prompt,
        system="You are a disciplined quantitative research hypothesis-generation agent. Return valid JSON only.",
        temperature=temperature,
        num_ctx=num_ctx,
    )
    hypotheses = _normalize_hypotheses(raw_obj)
    if not hypotheses:
        raise OllamaError("No valid hypotheses were generated.")

    payload = {"hypotheses": hypotheses}
    json_path = hypotheses_dir / "hypotheses.json"
    yaml_path = hypotheses_dir / "hypotheses.yaml"
    md_path = hypotheses_dir / "HYPOTHESES.md"

    json_text = json.dumps(payload, indent=2, ensure_ascii=False)
    json_path.write_text(json_text, encoding="utf-8")
    # JSON is valid YAML 1.2, so this is machine-readable without adding PyYAML.
    yaml_path.write_text(json_text, encoding="utf-8")
    _write_markdown(hypotheses, md_path)

    return {
        "model": model,
        "ollama_url": ollama_url,
        "hypothesis_count": len(hypotheses),
        "prompt_path": str(prompt_path),
        "json_path": str(json_path),
        "yaml_path": str(yaml_path),
        "markdown_path": str(md_path),
    }
