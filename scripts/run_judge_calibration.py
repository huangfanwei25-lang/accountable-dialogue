"""Run the fixed, local-only J0 initial model-judge resource probe.

The script neither pulls models nor makes a semantic claim.  It writes raw
model output outside the repository and leaves public curation separate.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from accountable_dialogue.judge_calibration import (
    JudgeCalibrationConfig,
    JudgeCalibrationTarget,
    execute_judge_calibration,
)
from accountable_dialogue.local_pilot import LocalOnlyOllamaClient

ROOT = Path(__file__).resolve().parents[1]
CASES_DIRECTORY = ROOT / "fixtures" / "synthetic-judge-calibration-v0" / "cases"
INITIAL_PROBE_TARGETS = (
    JudgeCalibrationTarget(case_id="j0-incomplete-withhold", model="qwen2.5:1.5b"),
    JudgeCalibrationTarget(case_id="j0-incomplete-instruction-data", model="qwen2.5:1.5b"),
    JudgeCalibrationTarget(case_id="j0-incomplete-withhold", model="llama3.2:3b"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Optional directory outside the repository. Defaults to an OS temporary directory.",
    )
    return parser.parse_args()


def default_output_directory() -> Path:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return Path(tempfile.gettempdir()) / "accountable-dialogue-judge-calibration" / stamp


def load_initial_cases() -> tuple[dict[str, object], ...]:
    needed = {target.case_id for target in INITIAL_PROBE_TARGETS}
    return tuple(
        json.loads((CASES_DIRECTORY / f"{case_id}.json").read_text(encoding="utf-8"))
        for case_id in sorted(needed)
    )


def local_ollama_version() -> str:
    try:
        completed = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            check=False,
            encoding="utf-8",
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return "unavailable"
    if completed.returncode != 0:
        return "unavailable"
    return completed.stdout.strip() or "unavailable"


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir or default_output_directory()
    config = JudgeCalibrationConfig(ollama_version=local_ollama_version())
    result = execute_judge_calibration(
        cases=load_initial_cases(),
        targets=INITIAL_PROBE_TARGETS,
        client=LocalOnlyOllamaClient(args.base_url),
        config=config,
        output_dir=output_dir,
        repository_root=ROOT,
    )
    statuses = Counter(str(row["mechanical_status"]) for row in result.rows)
    print(f"Raw local-only J0 output: {result.output_dir}")
    print(f"Recorded rows: {len(result.rows)}")
    print(f"Mechanical status counts: {dict(sorted(statuses.items()))}")
    print("No human-rater, H1-condition, honesty, or consciousness conclusion has been produced.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
