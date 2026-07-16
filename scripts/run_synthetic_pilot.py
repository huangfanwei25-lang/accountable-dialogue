"""Run the bounded synthetic pilot against already-installed local Ollama models.

Raw outputs are intentionally written outside this repository.  This script
does not train a model, download a model, read private memory, or upload data.
"""

from __future__ import annotations

import argparse
import json
import tempfile
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from accountable_dialogue.local_pilot import (
    LocalOnlyOllamaClient,
    PilotExecutionConfig,
    execute_pilot,
)

ROOT = Path(__file__).resolve().parents[1]
CASES_DIRECTORY = ROOT / "fixtures" / "synthetic-pilot-v0" / "cases"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    parser.add_argument(
        "--models",
        nargs="+",
        default=["qwen2.5:1.5b", "llama3.2:3b"],
        help="Names that must already appear in local Ollama /api/tags; no implicit pull occurs.",
    )
    parser.add_argument("--seed", type=int, default=20260716)
    parser.add_argument("--timeout-seconds", type=float, default=120.0)
    parser.add_argument("--max-tokens", type=int, default=360)
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Optional directory outside the repository. Defaults to an OS temporary directory.",
    )
    return parser.parse_args()


def default_output_directory() -> Path:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return Path(tempfile.gettempdir()) / "accountable-dialogue-pilot" / stamp


def load_cases() -> tuple[dict[str, object], ...]:
    return tuple(json.loads(path.read_text(encoding="utf-8")) for path in sorted(CASES_DIRECTORY.glob("*.json")))


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir or default_output_directory()
    client = LocalOnlyOllamaClient(args.base_url)
    config = PilotExecutionConfig(
        models=tuple(args.models),
        seed=args.seed,
        max_tokens=args.max_tokens,
        timeout_seconds=args.timeout_seconds,
    )
    result = execute_pilot(
        cases=load_cases(),
        client=client,
        config=config,
        output_dir=output_dir,
        repository_root=ROOT,
    )
    statuses = Counter(str(row["mechanical_status"]) for row in result.rows)
    print(f"Raw local-only pilot output: {result.output_dir}")
    print(f"Responses: {len(result.rows)}")
    print(f"Mechanical status counts: {dict(sorted(statuses.items()))}")
    print("No semantic score or effect conclusion has been produced.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
