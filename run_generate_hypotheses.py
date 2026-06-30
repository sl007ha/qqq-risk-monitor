#!/usr/bin/env python
"""Generate QQQ Risk Monitor hypotheses with a local Ollama model.

Usage:
    python run_generate_hypotheses.py --model qwen3:14b --n-hypotheses 3 --max-features 60
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from qqq_autoresearch.hypothesis_agent import generate_hypotheses_with_ollama


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate research hypotheses with local Ollama.")
    parser.add_argument("--model", default=os.environ.get("OLLAMA_MODEL", "qwen2.5:7b"), help="Local Ollama model name, e.g. qwen3:14b, qwen2.5:7b, qwen2.5-coder:7b.")
    parser.add_argument("--ollama-url", default=os.environ.get("OLLAMA_URL", "http://localhost:11434"), help="Ollama base URL.")
    parser.add_argument("--output-dir", default="outputs", help="Dashboard outputs directory produced by run_dashboard.py.")
    parser.add_argument("--hypotheses-dir", default="hypotheses", help="Directory for generated HYPOTHESES.md / hypotheses.yaml.")
    parser.add_argument("--n-hypotheses", type=int, default=8, help="Number of hypotheses to request from the local model. Start small for local models.")
    parser.add_argument("--max-features", type=int, default=120, help="Maximum feature rows to include in the model prompt. Start with 60-120 for local models.")
    parser.add_argument("--temperature", type=float, default=0.15, help="Ollama sampling temperature.")
    parser.add_argument("--num-ctx", type=int, default=24576, help="Requested context window for Ollama model options.")
    parser.add_argument("--dry-run-prompt", action="store_true", help="Write the prompt but do not call Ollama.")
    args = parser.parse_args()

    print("Starting local Ollama hypothesis generation...")
    print(f"model={args.model}, n_hypotheses={args.n_hypotheses}, max_features={args.max_features}, num_ctx={args.num_ctx}")

    summary = generate_hypotheses_with_ollama(
        repo_root=Path.cwd(),
        output_dir=Path(args.output_dir),
        hypotheses_dir=Path(args.hypotheses_dir),
        model=args.model,
        ollama_url=args.ollama_url,
        n_hypotheses=args.n_hypotheses,
        max_features=args.max_features,
        temperature=args.temperature,
        num_ctx=args.num_ctx,
        dry_run_prompt=args.dry_run_prompt,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
