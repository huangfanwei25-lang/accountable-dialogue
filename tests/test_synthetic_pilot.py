from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from accountable_dialogue.local_pilot import (
    LocalOnlyOllamaClient,
    PilotExecutionConfig,
    execute_pilot,
    validate_loopback_base_url,
)
from accountable_dialogue.synthetic_pilot import (
    CASE_FORMAT,
    RESPONSE_FIELDS,
    annotation_key_digest,
    load_annotation_key,
    render_condition,
    validate_annotation_key,
    validate_case,
)
from scripts.run_synthetic_pilot import load_cases

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "synthetic-evaluation-case-v0.schema.json"
FIXTURES = ROOT / "fixtures" / "synthetic-pilot-v0"
CASES = FIXTURES / "cases"
ANNOTATION_KEY = FIXTURES / "annotation-key-v0.json"


def load_case(name: str) -> dict[str, object]:
    return json.loads((CASES / name).read_text(encoding="utf-8"))


class FakeOllamaTransport:
    def __init__(self, responses: list[dict[str, object]] | None = None) -> None:
        self.requests: list[tuple[str, str, dict[str, object] | None, float]] = []
        self.responses = list(responses or [])

    def request(
        self,
        method: str,
        url: str,
        payload: dict[str, object] | None,
        timeout_seconds: float,
    ) -> dict[str, object]:
        self.requests.append((method, url, payload, timeout_seconds))
        if url.endswith("/api/tags"):
            return {"models": [{"name": "tiny-a:latest"}, {"name": "tiny-b:latest"}]}
        if self.responses:
            return self.responses.pop(0)
        return {
            "response": json.dumps(
                {
                    "conclusion": "僅根據提供材料回答。",
                    "evidence_refs": ["source-hours-weekdays"],
                    "prior_claim_ref": "not_applicable",
                    "unknown_or_correction": "not_applicable",
                    "authority_next_step": "not_applicable",
                },
                ensure_ascii=False,
            )
        }


class SyntheticPilotTests(unittest.TestCase):
    def test_case_loader_can_preselect_a_narrow_smoke_scope(self) -> None:
        selected = load_cases(("h1-incomplete-library-hours",))

        self.assertEqual(["h1-incomplete-library-hours"], [case["case_id"] for case in selected])
        with self.assertRaisesRegex(ValueError, "unknown case"):
            load_cases(("case-not-present",))

    def test_schema_and_all_fixed_cases_are_public_and_valid(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        schema_validator = Draft202012Validator(schema)
        annotation_key = load_annotation_key(ANNOTATION_KEY)

        self.assertEqual("accountable-dialogue/synthetic-evaluation-case-v0", CASE_FORMAT)
        self.assertEqual(
            (
                "conclusion",
                "evidence_refs",
                "prior_claim_ref",
                "unknown_or_correction",
                "authority_next_step",
            ),
            RESPONSE_FIELDS,
        )
        self.assertEqual([], validate_annotation_key(annotation_key))

        paths = sorted(CASES.glob("*.json"))
        self.assertEqual(6, len(paths))
        for path in paths:
            case = load_case(path.name)
            schema_errors = sorted(schema_validator.iter_errors(case), key=lambda error: list(error.path))
            self.assertEqual([], schema_errors, path.name)
            self.assertEqual([], validate_case(case), path.name)
            self.assertEqual(
                annotation_key_digest(ANNOTATION_KEY),
                case["annotation_key"]["sha256"],
                path.name,
            )

    def test_b0_and_i1_share_materials_task_and_response_contract_without_label_leakage(self) -> None:
        annotation_key = load_annotation_key(ANNOTATION_KEY)
        labels = {
            label["id"]
            for case_labels in annotation_key["case_expectations"]
            for label in case_labels["labels"]
        }

        for path in sorted(CASES.glob("*.json")):
            case = load_case(path.name)
            baseline = render_condition(case, "B0_baseline")
            structured = render_condition(case, "I1_structured_context")

            self.assertEqual(baseline.material_ids, structured.material_ids, path.name)
            self.assertEqual(case["task"], baseline.task)
            self.assertEqual(case["task"], structured.task)
            self.assertEqual(list(RESPONSE_FIELDS), case["response_contract"])
            self.assertNotIn("evidence_links", baseline.prompt)
            self.assertIn("evidence_links", structured.prompt)
            for label in labels:
                self.assertNotIn(label, baseline.prompt)
                self.assertNotIn(label, structured.prompt)

    def test_metamorphic_pairs_change_only_the_declared_evidence(self) -> None:
        incomplete = load_case("h1-incomplete-library-hours.json")
        supported = load_case("h1-supported-library-hours.json")
        incomplete_materials = {item["id"]: item["text"] for item in incomplete["materials"]}
        supported_materials = {item["id"]: item["text"] for item in supported["materials"]}

        self.assertEqual(incomplete["task"], supported["task"])
        self.assertEqual(incomplete_materials, {key: supported_materials[key] for key in incomplete_materials})
        self.assertEqual({"source-hours-sunday-june"}, set(supported_materials) - set(incomplete_materials))

        counterevidence = load_case("h2-counterevidence-quiet-room.json")
        stable = load_case("h2-stable-quiet-room.json")
        counter_materials = {item["id"]: item["text"] for item in counterevidence["materials"]}
        stable_materials = {item["id"]: item["text"] for item in stable["materials"]}

        self.assertEqual(counterevidence["task"], stable["task"])
        self.assertEqual(counterevidence["structured_context"], stable["structured_context"])
        self.assertEqual(set(counter_materials), set(stable_materials))
        self.assertEqual(
            {"source-quiet-room-followup-test"},
            {key for key in counter_materials if counter_materials[key] != stable_materials[key]},
        )

    def test_semantic_validator_rejects_private_fields_unsafe_risk_and_non_equivalent_structure(self) -> None:
        case = load_case("h1-incomplete-library-hours.json")

        private_case = copy.deepcopy(case)
        private_case["raw_dialogue"] = "private conversation"
        self.assertIn("forbidden_field", {issue.code for issue in validate_case(private_case)})

        risk_case = copy.deepcopy(case)
        risk_case["risk"]["class"] = "high"
        self.assertIn("invalid_risk", {issue.code for issue in validate_case(risk_case)})

        structure_case = copy.deepcopy(case)
        structure_case["structured_context"]["evidence_links"][0]["source_ref"] = "source-not-present"
        self.assertIn("unknown_reference", {issue.code for issue in validate_case(structure_case)})

        contract_case = copy.deepcopy(case)
        contract_case["response_contract"] = ["conclusion"]
        self.assertIn("invalid_response_contract", {issue.code for issue in validate_case(contract_case)})

    def test_loopback_client_refuses_remote_urls_and_implicit_model_downloads(self) -> None:
        self.assertEqual("http://127.0.0.1:11434", validate_loopback_base_url("http://127.0.0.1:11434/"))
        with self.assertRaisesRegex(ValueError, "loopback"):
            validate_loopback_base_url("https://example.com")

        transport = FakeOllamaTransport()
        client = LocalOnlyOllamaClient("http://127.0.0.1:11434", transport=transport)
        self.assertEqual(("tiny-a:latest", "tiny-b:latest"), client.available_models())
        with self.assertRaisesRegex(ValueError, "not installed"):
            client.require_models(("tiny-a:latest", "missing:latest"))

    def test_runner_writes_blind_raw_outputs_outside_the_repository_and_never_sends_labels(self) -> None:
        case = load_case("h1-incomplete-library-hours.json")
        transport = FakeOllamaTransport()
        client = LocalOnlyOllamaClient("http://127.0.0.1:11434", transport=transport)
        config = PilotExecutionConfig(
            models=("tiny-a:latest",),
            seed=20260716,
            timeout_seconds=3,
            max_tokens=80,
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            output_dir = Path(temporary_directory) / "pilot-output"
            result = execute_pilot(
                cases=(case,),
                client=client,
                config=config,
                output_dir=output_dir,
                repository_root=ROOT,
            )

            self.assertEqual(2, len(result.rows))
            self.assertTrue((output_dir / "blind-responses.jsonl").is_file())
            self.assertTrue((output_dir / "condition-mapping.json").is_file())
            self.assertTrue((output_dir / "run-manifest.json").is_file())
            self.assertNotEqual(output_dir.resolve().parent, ROOT.resolve())
            self.assertEqual({"A", "B"}, {row["condition_alias"] for row in result.rows})
            self.assertTrue(all(row["mechanical_status"] == "valid" for row in result.rows))

        generation_payloads = [payload for _, url, payload, _ in transport.requests if url.endswith("/api/generate")]
        self.assertEqual(2, len(generation_payloads))
        for payload in generation_payloads:
            self.assertIsNotNone(payload)
            prompt = payload["prompt"]
            self.assertNotIn("appropriate_withholding", prompt)
            self.assertNotIn("annotation_key", prompt)
            self.assertEqual("json", payload["format"])

        with self.assertRaisesRegex(ValueError, "outside the repository"):
            execute_pilot(
                cases=(case,),
                client=client,
                config=config,
                output_dir=ROOT / "must-not-write-pilot-output",
                repository_root=ROOT,
            )

    def test_runner_records_invalid_json_as_unrateable_without_rewriting_it(self) -> None:
        case = load_case("h1-incomplete-library-hours.json")
        transport = FakeOllamaTransport(responses=[{"response": "not-json"}, {"response": "[]"}])
        client = LocalOnlyOllamaClient("http://127.0.0.1:11434", transport=transport)
        config = PilotExecutionConfig(models=("tiny-a:latest",), timeout_seconds=3, max_tokens=80)

        with tempfile.TemporaryDirectory() as temporary_directory:
            result = execute_pilot(
                cases=(case,),
                client=client,
                config=config,
                output_dir=Path(temporary_directory) / "pilot-output",
                repository_root=ROOT,
            )

        self.assertEqual({"invalid_json", "invalid_response_object"}, {row["mechanical_status"] for row in result.rows})


if __name__ == "__main__":
    unittest.main()
