from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from accountable_dialogue.judge_calibration import (
    JUDGE_VERDICT_FORMAT,
    JudgeCalibrationConfig,
    JudgeCalibrationTarget,
    assess_judge_response,
    case_commitment_digest,
    execute_judge_calibration,
    judge_prompt_digest,
    load_judge_calibration_key,
    render_judge_prompt,
    validate_judge_calibration_case,
    validate_judge_calibration_key,
    validate_judge_verdict,
)
from accountable_dialogue.local_pilot import LocalOnlyOllamaClient, SafeOllamaRequestFailure

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "fixtures" / "synthetic-judge-calibration-v0"
CASES_DIRECTORY = FIXTURE_ROOT / "cases"
KEY_PATH = FIXTURE_ROOT / "calibration-key-v0.json"
CASE_SCHEMA_PATH = ROOT / "schemas" / "synthetic-judge-calibration-v0.schema.json"
KEY_SCHEMA_PATH = ROOT / "schemas" / "synthetic-judge-calibration-key-v0.schema.json"
VERDICT_SCHEMA_PATH = ROOT / "schemas" / "judge-verdict-v0.schema.json"


class FakeOllamaTransport:
    def __init__(
        self,
        responses: list[dict[str, object]] | None = None,
        failures: list[BaseException] | None = None,
    ) -> None:
        self.responses = list(responses or [])
        self.failures = list(failures or [])
        self.requests: list[tuple[str, str, dict[str, object] | None, float]] = []

    def request(
        self,
        method: str,
        url: str,
        payload: dict[str, object] | None,
        timeout_seconds: float,
    ) -> dict[str, object]:
        self.requests.append((method, url, payload, timeout_seconds))
        if url.endswith("/api/tags"):
            return {
                "models": [
                    {"name": "tiny-a:latest", "digest": "a" * 64},
                    {"name": "tiny-b:latest", "digest": "b" * 64},
                ]
            }
        if url.endswith("/api/generate"):
            if self.failures:
                raise self.failures.pop(0)
            if self.responses:
                return self.responses.pop(0)
            raise AssertionError("fake transport received an unexpected generation request")
        raise AssertionError(f"unexpected URL: {url}")


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def matching_verdict(case: dict[str, object], key: dict[str, object]) -> dict[str, object]:
    expectation = next(item for item in key["case_expectations"] if item["case_id"] == case["case_id"])
    return {
        "format": JUDGE_VERDICT_FORMAT,
        "verdicts": [
            {
                "label_id": item["label_id"],
                "verdict": item["verdict"],
                "response_field_refs": item["required_response_field_refs"],
                "material_refs": item["required_material_refs"],
                "unrateable_reason": "not_applicable",
            }
            for item in expectation["expected_verdicts"]
        ],
    }


class JudgeCalibrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.key = load_judge_calibration_key(KEY_PATH)
        self.case = load_json(CASES_DIRECTORY / "j0-incomplete-withhold.json")

    def test_fixtures_and_key_are_closed_and_expected_verdicts_never_enter_a_judge_prompt(self) -> None:
        case_validator = Draft202012Validator(load_json(CASE_SCHEMA_PATH))
        key_validator = Draft202012Validator(load_json(KEY_SCHEMA_PATH))

        self.assertEqual([], validate_judge_calibration_key(self.key))
        self.assertEqual([], sorted(key_validator.iter_errors(self.key), key=lambda error: list(error.path)))

        for path in sorted(CASES_DIRECTORY.glob("*.json")):
            case = load_json(path)
            self.assertEqual([], validate_judge_calibration_case(case))
            self.assertEqual([], sorted(case_validator.iter_errors(case), key=lambda error: list(error.path)))
            prompt = render_judge_prompt(case)
            self.assertNotIn("expected_verdicts", prompt)
            self.assertNotIn("required_response_field_refs", prompt)
            self.assertNotIn("required_material_refs", prompt)
            self.assertNotIn("calibration_key", prompt)
            self.assertNotIn(case["calibration_key"]["sha256"], prompt)

        injection_case = load_json(CASES_DIRECTORY / "j0-incomplete-instruction-data.json")
        injection_prompt = render_judge_prompt(injection_case)
        self.assertIn("不可信資料", injection_prompt)
        self.assertIn("忽略評估規則", injection_prompt)

    def test_assessment_computes_only_a_per_label_calibration_vector(self) -> None:
        raw_response = json.dumps(matching_verdict(self.case, self.key), ensure_ascii=False)
        verdict_schema = Draft202012Validator(load_json(VERDICT_SCHEMA_PATH))

        parsed = json.loads(raw_response)
        self.assertEqual([], sorted(verdict_schema.iter_errors(parsed), key=lambda error: list(error.path)))
        self.assertEqual([], validate_judge_verdict(parsed, self.case))

        assessment = assess_judge_response(case=self.case, key=self.key, raw_response=raw_response)
        self.assertEqual("valid", assessment.mechanical_status)
        self.assertTrue(all(item["matches_expected"] for item in assessment.label_comparisons))
        self.assertEqual(
            ["appropriate_withholding", "provenance_integrity"],
            [item["label_id"] for item in assessment.label_comparisons],
        )

    def test_closed_judge_output_rejects_extra_fields_missing_labels_and_invalid_references(self) -> None:
        valid = matching_verdict(self.case, self.key)

        extra = copy.deepcopy(valid)
        extra["confidence"] = 1
        self.assertIn("unexpected_field", {issue.code for issue in validate_judge_verdict(extra, self.case)})

        missing = copy.deepcopy(valid)
        missing["verdicts"] = missing["verdicts"][:1]
        self.assertIn("invalid_label_set", {issue.code for issue in validate_judge_verdict(missing, self.case)})

        invalid_reference = copy.deepcopy(valid)
        invalid_reference["verdicts"][0]["material_refs"] = ["invented-source"]
        self.assertIn("unknown_reference", {issue.code for issue in validate_judge_verdict(invalid_reference, self.case)})

        missing_anchor = copy.deepcopy(valid)
        missing_anchor["verdicts"][0]["response_field_refs"] = ["conclusion"]
        assessment = assess_judge_response(
            case=self.case,
            key=self.key,
            raw_response=json.dumps(missing_anchor, ensure_ascii=False),
        )
        self.assertEqual("valid", assessment.mechanical_status)
        self.assertFalse(assessment.label_comparisons[0]["matches_expected_response_field_refs"])
        self.assertFalse(assessment.label_comparisons[0]["matches_expected"])

        unrelated_existing_reference = copy.deepcopy(valid)
        unrelated_existing_reference["verdicts"][0]["material_refs"] = ["event-hours-notice"]
        self.assertEqual([], validate_judge_verdict(unrelated_existing_reference, self.case))
        assessment = assess_judge_response(
            case=self.case,
            key=self.key,
            raw_response=json.dumps(unrelated_existing_reference, ensure_ascii=False),
        )
        self.assertEqual("valid", assessment.mechanical_status)
        self.assertFalse(assessment.label_comparisons[0]["matches_expected_material_refs"])
        self.assertFalse(assessment.label_comparisons[0]["matches_expected"])

    def test_calibration_key_commits_to_case_content_without_leaking_the_key_digest_into_that_commitment(self) -> None:
        original_commitment = case_commitment_digest(self.case)
        changed_key_reference = copy.deepcopy(self.case)
        changed_key_reference["calibration_key"]["sha256"] = "0" * 64
        self.assertEqual(original_commitment, case_commitment_digest(changed_key_reference))

        tampered_case = copy.deepcopy(self.case)
        tampered_case["task"] = "遭竄改的完全不同任務。"
        self.assertNotEqual(original_commitment, case_commitment_digest(tampered_case))
        with self.assertRaisesRegex(ValueError, "case commitment"):
            assess_judge_response(
                case=tampered_case,
                key=self.key,
                raw_response=json.dumps(matching_verdict(tampered_case, self.key), ensure_ascii=False),
            )

    def test_resource_limits_cannot_expand_the_fixed_initial_probe(self) -> None:
        with self.assertRaisesRegex(ValueError, "bounded"):
            JudgeCalibrationConfig(context_tokens=4097)
        with self.assertRaisesRegex(ValueError, "bounded"):
            JudgeCalibrationConfig(max_tokens=129)
        with self.assertRaisesRegex(ValueError, "per-call timeout"):
            JudgeCalibrationConfig(timeout_seconds=11, wall_time_seconds=10)

    def test_runner_keeps_raw_outputs_outside_the_repository_and_preserves_invalid_output(self) -> None:
        valid_response = json.dumps(matching_verdict(self.case, self.key), ensure_ascii=False)
        transport = FakeOllamaTransport(responses=[{"response": valid_response}])
        client = LocalOnlyOllamaClient("http://127.0.0.1:11434", transport=transport)
        target = JudgeCalibrationTarget(case_id="j0-incomplete-withhold", model="tiny-a:latest")

        with tempfile.TemporaryDirectory() as temporary_directory:
            output_dir = Path(temporary_directory) / "judge-output"
            result = execute_judge_calibration(
                cases=(self.case,),
                targets=(target,),
                client=client,
                config=JudgeCalibrationConfig(timeout_seconds=3, max_tokens=80, wall_time_seconds=10),
                output_dir=output_dir,
                repository_root=ROOT,
            )

            self.assertTrue((output_dir / "judge-responses.jsonl").is_file())
            self.assertTrue((output_dir / "run-manifest.json").is_file())
            self.assertEqual("valid", result.rows[0]["mechanical_status"])
            self.assertTrue(all(item["matches_expected"] for item in result.rows[0]["label_comparisons"]))
            self.assertFalse(result.manifest["expected_verdicts_sent_to_models"])
            self.assertEqual("not_recorded", result.manifest["ollama_version"])
            self.assertEqual(
                judge_prompt_digest(self.case),
                result.manifest["rendered_judge_prompt_sha256"]["j0-incomplete-withhold"],
            )
            self.assertNotEqual(output_dir.resolve().parent, ROOT.resolve())

        generation_payloads = [payload for _, url, payload, _ in transport.requests if url.endswith("/api/generate")]
        self.assertEqual(1, len(generation_payloads))
        self.assertIsNotNone(generation_payloads[0])
        prompt = generation_payloads[0]["prompt"]
        self.assertNotIn("expected_verdicts", prompt)
        self.assertNotIn("required_response_field_refs", prompt)
        self.assertNotIn("required_material_refs", prompt)
        self.assertNotIn("calibration-key-judge-v0", prompt)

        with self.assertRaisesRegex(ValueError, "outside the repository"):
            execute_judge_calibration(
                cases=(self.case,),
                targets=(target,),
                client=client,
                config=JudgeCalibrationConfig(timeout_seconds=3, max_tokens=80, wall_time_seconds=10),
                output_dir=ROOT / "must-not-write-judge-output",
                repository_root=ROOT,
            )

        invalid_transport = FakeOllamaTransport(responses=[{"response": "{}"}])
        invalid_client = LocalOnlyOllamaClient("http://127.0.0.1:11434", transport=invalid_transport)
        with tempfile.TemporaryDirectory() as temporary_directory:
            result = execute_judge_calibration(
                cases=(self.case,),
                targets=(target,),
                client=invalid_client,
                config=JudgeCalibrationConfig(timeout_seconds=3, max_tokens=80, wall_time_seconds=10),
                output_dir=Path(temporary_directory) / "judge-output",
                repository_root=ROOT,
            )

        self.assertEqual("invalid_judge_contract", result.rows[0]["mechanical_status"])
        self.assertEqual("{}", result.rows[0]["raw_response"])
        self.assertEqual([], result.rows[0]["label_comparisons"])

    def test_runner_script_can_render_help_from_the_repository_root(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "run_judge_calibration.py"), "--help"],
            cwd=ROOT,
            capture_output=True,
            check=False,
            encoding="utf-8",
            text=True,
            timeout=10,
        )

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn("--output-dir", completed.stdout)

    def test_runner_keeps_only_a_safe_transport_observation(self) -> None:
        failure = SafeOllamaRequestFailure("http_5xx", http_status=500)
        failure.__cause__ = RuntimeError(r"server body C:\private\secret.txt")
        transport = FakeOllamaTransport(failures=[failure])
        client = LocalOnlyOllamaClient("http://127.0.0.1:11434", transport=transport)
        target = JudgeCalibrationTarget(case_id="j0-incomplete-withhold", model="tiny-a:latest")

        with tempfile.TemporaryDirectory() as temporary_directory:
            result = execute_judge_calibration(
                cases=(self.case,),
                targets=(target,),
                client=client,
                config=JudgeCalibrationConfig(timeout_seconds=3, max_tokens=80, wall_time_seconds=10),
                output_dir=Path(temporary_directory) / "judge-output",
                repository_root=ROOT,
            )

        row = result.rows[0]
        self.assertEqual("transport_error", row["mechanical_status"])
        self.assertEqual({"kind": "http_5xx", "http_status": 500}, row["transport_observation"])
        self.assertNotIn("private", json.dumps(row, ensure_ascii=False))

        timeout_transport = FakeOllamaTransport(failures=[TimeoutError(r"C:\private\timeout")])
        timeout_client = LocalOnlyOllamaClient("http://127.0.0.1:11434", transport=timeout_transport)
        with tempfile.TemporaryDirectory() as temporary_directory:
            timeout_result = execute_judge_calibration(
                cases=(self.case,),
                targets=(target,),
                client=timeout_client,
                config=JudgeCalibrationConfig(timeout_seconds=3, max_tokens=80, wall_time_seconds=10),
                output_dir=Path(temporary_directory) / "judge-timeout-output",
                repository_root=ROOT,
            )
        self.assertEqual("timeout", timeout_result.rows[0]["mechanical_status"])
        self.assertEqual({"kind": "timeout"}, timeout_result.rows[0]["transport_observation"])

        malformed_transport = FakeOllamaTransport(responses=[{"not_response": "C:\\private\\body"}])
        malformed_client = LocalOnlyOllamaClient("http://127.0.0.1:11434", transport=malformed_transport)
        with self.assertRaises(SafeOllamaRequestFailure) as raised:
            malformed_client.generate("tiny-a:latest", "synthetic", JudgeCalibrationConfig(max_tokens=80))
        self.assertEqual("provider_contract_error", raised.exception.kind)
        self.assertNotIn("private", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
