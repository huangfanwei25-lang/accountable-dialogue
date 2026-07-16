from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from accountable_dialogue.change_case import project_subject, validate_change_case

ROOT = Path(__file__).resolve().parents[1]
RECORDS = ROOT / "records" / "change-case-v0"
SCHEMA = ROOT / "schemas" / "change-case-v0.schema.json"
SEQUENCE_PROJECTION_REVISION = "7372348aa6372feda6765a21cec7368377852216"
PROTOCOL_REVISION = "c9d43c52320c90d598e5ad899c51416c091cb880"
PROTOCOL_REFINEMENT_REVISION = "eacb0b8b4f872b6e56283eef2de34e682cfa414a"
EVALUATION_CASE_DESIGN_REVISION = "ed8acc6ac1aa6aebb02d775cfe9dffed22bc3845"
SMALL_MODEL_PILOT_PLAN_REVISION = "790663cf9929e2d3ff28c24d271c477d6a110013"
SMALL_MODEL_PILOT_HARNESS_REVISION = "625356bad1db84a2627854fe702109437b58d948"
SMALL_MODEL_PILOT_ATTEMPT_REVISION = "b3dba53b756237bd5bc2dc2a75dc23a1ee1d2df4"
LOCAL_RESOURCE_SMOKE_REVISION = "2dca34ae9073dd29a7e9913e48644257b2c70ca7"
LOCAL_RESOURCE_SMOKE_V02_CONTRACT_REVISION = "395b6fd2a8d17840ee6360cbe72441874021abcf"
LOCAL_RESOURCE_SMOKE_V02_RESULT_REVISION = "a7482601783a927997f178fa65317bb62e8b8af8"


def load_record(name: str) -> dict[str, object]:
    return json.loads((RECORDS / name).read_text(encoding="utf-8"))


class RepositoryChangeCaseTests(unittest.TestCase):
    def assert_artifacts_are_locatable(self, record: dict[str, object]) -> None:
        for artifact in record["artifacts"]:
            locator = artifact["locator"]
            if locator.startswith("https://"):
                self.assertEqual("external_source", artifact["kind"])
            else:
                self.assertTrue((ROOT / locator).is_file(), locator)

    def test_public_repository_records_match_the_schema_and_validator(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)

        for path in RECORDS.glob("*.json"):
            record = load_record(path.name)
            schema_errors = sorted(validator.iter_errors(record), key=lambda error: list(error.path))
            self.assertEqual([], schema_errors, f"{path.name} must validate against the public schema")
            self.assertEqual([], validate_change_case(record), f"{path.name} must pass semantic validation")
            self.assert_artifacts_are_locatable(record)

    def test_change_case_prototype_record_keeps_artifacts_evidence_authority_and_limits_separate(self) -> None:
        record = load_record("change-case-v0-prototype.json")

        self.assertEqual([], validate_change_case(record))
        self.assert_artifacts_are_locatable(record)

        projection = project_subject(record, "proposal-change-case-v0-prototype")
        self.assertEqual("ratified", projection.governance)
        self.assertEqual("reported_implemented", projection.implementation)
        self.assertEqual("event-prototype-implemented", projection.implementation_event_id)
        self.assertEqual("verified_within_scope", projection.verification)
        self.assertEqual("event-prototype-verified", projection.verification_event_id)
        self.assertEqual("no_terminal_event", projection.lifecycle)

        decision_event = next(event for event in record["events"] if event["kind"] == "governance_decided")
        self.assertIn("不是身分", decision_event["public_summary"])

        limitation_evidence = [
            item for item in record["evidence"] if item["relation"] == "limits"
        ]
        self.assertEqual(1, len(limitation_evidence))

    def test_research_direction_record_remains_a_proposal_under_review(self) -> None:
        record = load_record("accountable-agent-continuity-research-proposal.json")

        self.assertEqual([], validate_change_case(record))
        projection = project_subject(record, "proposal-accountable-agent-continuity")
        self.assertEqual("under_review", projection.governance)
        self.assertEqual("no_implementation_report", projection.implementation)
        self.assertEqual("no_verification_record", projection.verification)

    def test_sequence_projection_revision_has_a_bounded_successor_record(self) -> None:
        record = load_record("sequence-report-projection-v0.json")

        self.assertEqual([], validate_change_case(record))
        self.assert_artifacts_are_locatable(record)
        self.assertTrue(
            all(artifact["revision"] == SEQUENCE_PROJECTION_REVISION for artifact in record["artifacts"])
        )

        projection = project_subject(record, "proposal-sequence-report-projection")
        self.assertEqual("ratified", projection.governance)
        self.assertEqual("reported_implemented", projection.implementation)
        self.assertEqual("event-projection-implemented", projection.implementation_event_id)
        self.assertEqual("verified_within_scope", projection.verification)
        self.assertEqual("event-projection-verified", projection.verification_event_id)

    def test_synthetic_protocol_stays_under_review_without_a_runtime_claim(self) -> None:
        record = load_record("synthetic-evaluation-protocol-proposal.json")

        self.assertEqual([], validate_change_case(record))
        self.assert_artifacts_are_locatable(record)
        artifacts = {artifact["id"]: artifact for artifact in record["artifacts"]}
        self.assertEqual(PROTOCOL_REVISION, artifacts["artifact-synthetic-protocol"]["revision"])
        self.assertEqual(
            PROTOCOL_REFINEMENT_REVISION,
            artifacts["artifact-synthetic-protocol-v2"]["revision"],
        )

        original = project_subject(record, "proposal-synthetic-evaluation-protocol")
        current = project_subject(record, "proposal-synthetic-evaluation-protocol-v2")
        self.assertEqual("superseded", original.lifecycle)
        self.assertEqual("under_review", current.governance)
        self.assertEqual("no_implementation_report", current.implementation)
        self.assertEqual("no_verification_record", current.verification)

    def test_evaluation_case_boundary_stays_a_non_executable_proposal(self) -> None:
        record = load_record("synthetic-evaluation-case-format-proposal.json")

        self.assertEqual([], validate_change_case(record))
        self.assert_artifacts_are_locatable(record)
        artifacts = {artifact["id"]: artifact for artifact in record["artifacts"]}
        self.assertEqual(
            EVALUATION_CASE_DESIGN_REVISION,
            artifacts["artifact-evaluation-case-design"]["revision"],
        )

        projection = project_subject(record, "proposal-synthetic-evaluation-case-format")
        self.assertEqual("under_review", projection.governance)
        self.assertEqual("no_implementation_report", projection.implementation)
        self.assertEqual("no_verification_record", projection.verification)

    def test_small_model_pilot_has_limited_authorization_and_a_harness_but_no_live_run_claim(self) -> None:
        record = load_record("synthetic-small-model-pilot-proposal.json")

        self.assertEqual([], validate_change_case(record))
        self.assert_artifacts_are_locatable(record)
        artifacts = {artifact["id"]: artifact for artifact in record["artifacts"]}
        self.assertEqual(
            SMALL_MODEL_PILOT_PLAN_REVISION,
            artifacts["artifact-small-model-pilot-plan"]["revision"],
        )
        self.assertEqual(
            SMALL_MODEL_PILOT_HARNESS_REVISION,
            artifacts["artifact-pilot-harness-source"]["revision"],
        )

        projection = project_subject(record, "proposal-synthetic-small-model-pilot")
        self.assertEqual("ratified", projection.governance)
        self.assertEqual("reported_implemented", projection.implementation)
        self.assertEqual("verified_within_scope", projection.verification)
        self.assertEqual("event-small-model-pilot-harness-implemented", projection.implementation_event_id)
        self.assertEqual("event-small-model-pilot-harness-verified", projection.verification_event_id)

        decision = next(event["decision"] for event in record["events"] if event["kind"] == "governance_decided")
        self.assertEqual("human", decision["made_by"]["kind"])
        self.assertEqual(
            ["synthetic_pilot", "local_model_execution"],
            decision["authority_basis"]["scope"],
        )

    def test_inconclusive_pilot_attempt_preserves_a_resource_limit_without_model_claims(self) -> None:
        record = load_record("synthetic-small-model-pilot-attempt-one.json")

        self.assertEqual([], validate_change_case(record))
        self.assert_artifacts_are_locatable(record)
        artifacts = {artifact["id"]: artifact for artifact in record["artifacts"]}
        self.assertEqual(
            SMALL_MODEL_PILOT_ATTEMPT_REVISION,
            artifacts["artifact-pilot-attempt-status"]["revision"],
        )

        projection = project_subject(record, "observation-pilot-resource-boundary")
        self.assertEqual("no_governance_record", projection.governance)
        self.assertEqual("no_implementation_report", projection.implementation)
        self.assertEqual("inconclusive", projection.verification)
        self.assertEqual("event-pilot-attempt-inconclusive", projection.verification_event_id)

    def test_resource_smoke_preserves_contract_failure_without_a_semantic_effect_claim(self) -> None:
        record = load_record("synthetic-local-resource-smoke-result.json")

        self.assertEqual([], validate_change_case(record))
        self.assert_artifacts_are_locatable(record)
        artifacts = {artifact["id"]: artifact for artifact in record["artifacts"]}
        self.assertEqual(
            {
                "artifact-smoke-status",
                "artifact-smoke-manifest",
                "artifact-smoke-responses",
                "artifact-smoke-plan",
                "artifact-smoke-fixture",
                "artifact-smoke-prompt-renderer",
                "artifact-smoke-response-validator",
                "artifact-smoke-commit",
            },
            set(artifacts),
        )
        self.assertTrue(
            all(artifact["revision"] == LOCAL_RESOURCE_SMOKE_REVISION for artifact in artifacts.values())
        )

        verification_event = next(event for event in record["events"] if event["id"] == "event-smoke-inconclusive")
        self.assertEqual("inconclusive", verification_event["verification"]["outcome"])
        self.assertEqual(
            [
                "evidence-smoke-completion-with-contract-failure",
                "evidence-smoke-no-semantic-evaluation",
                "evidence-smoke-contract-inputs",
            ],
            verification_event["evidence_refs"],
        )
        self.assertIn(
            "不推論模型的知識邊界、誠實、人格、意識或 structured context 的效果。",
            verification_event["verification"]["limitations"],
        )

        projection = project_subject(record, "observation-smoke-evidence-contract-gap")
        self.assertEqual("no_governance_record", projection.governance)
        self.assertEqual("no_implementation_report", projection.implementation)
        self.assertEqual("inconclusive", projection.verification)
        self.assertEqual("event-smoke-inconclusive", projection.verification_event_id)

    def test_v02_resource_smoke_preserves_empty_evidence_as_an_inconclusive_contract_gap(self) -> None:
        record = load_record("synthetic-local-resource-smoke-v0.2-result.json")

        self.assertEqual([], validate_change_case(record))
        self.assert_artifacts_are_locatable(record)
        artifacts = {artifact["id"]: artifact for artifact in record["artifacts"]}
        self.assertEqual(LOCAL_RESOURCE_SMOKE_V02_RESULT_REVISION, artifacts["artifact-smoke-v02-status"]["revision"])
        self.assertEqual(LOCAL_RESOURCE_SMOKE_V02_RESULT_REVISION, artifacts["artifact-smoke-v02-responses"]["revision"])
        for artifact_id in (
            "artifact-smoke-v02-plan",
            "artifact-smoke-v02-fixture",
            "artifact-smoke-v02-renderer",
            "artifact-smoke-v02-validator",
            "artifact-smoke-v02-tests",
        ):
            self.assertEqual(LOCAL_RESOURCE_SMOKE_V02_CONTRACT_REVISION, artifacts[artifact_id]["revision"])

        verification_event = next(event for event in record["events"] if event["id"] == "event-smoke-v02-inconclusive")
        self.assertEqual("inconclusive", verification_event["verification"]["outcome"])
        self.assertIn(
            "不推論 H1 回答真值、B0／I1 差異、structured context 效果，或模型的知識邊界、誠實、人格、意識與內在狀態。",
            verification_event["verification"]["limitations"],
        )

        projection = project_subject(record, "observation-smoke-v02-empty-evidence-gap")
        self.assertEqual("no_governance_record", projection.governance)
        self.assertEqual("no_implementation_report", projection.implementation)
        self.assertEqual("inconclusive", projection.verification)
        self.assertEqual("event-smoke-v02-inconclusive", projection.verification_event_id)


if __name__ == "__main__":
    unittest.main()
