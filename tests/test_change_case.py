from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from accountable_dialogue.change_case import project_subject, validate_change_case

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples" / "change-case-v0"
SCHEMA = ROOT / "schemas" / "change-case-v0.schema.json"


def load_case(name: str) -> dict[str, object]:
    return json.loads((EXAMPLES / name).read_text(encoding="utf-8"))


class ChangeCaseTests(unittest.TestCase):
    def assert_valid(self, case: dict[str, object]) -> None:
        self.assertEqual([], validate_change_case(case))

    def assert_has_code(self, case: dict[str, object], code: str) -> None:
        self.assertIn(code, {issue.code for issue in validate_change_case(case)})

    def test_schema_is_parseable_and_declares_the_public_format(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

        self.assertEqual("accountable-dialogue/change-case-v0", schema["properties"]["format"]["const"])
        self.assertFalse(schema["additionalProperties"])
        Draft202012Validator.check_schema(schema)

        validator = Draft202012Validator(schema)
        for path in EXAMPLES.glob("*.json"):
            errors = sorted(validator.iter_errors(load_case(path.name)), key=lambda error: list(error.path))
            self.assertEqual([], errors, f"{path.name} must validate against the public schema")

    def test_proposal_and_governance_decision_are_different_layers(self) -> None:
        case = load_case("proposal-ratification.json")

        self.assert_valid(case)
        proposal = case["subjects"][0]
        self.assertEqual("proposal", proposal["kind"])
        self.assertNotIn("governance_status", proposal)

        projection = project_subject(case, "proposal-subject-event-model")
        self.assertEqual("ratified", projection.governance)
        self.assertEqual("no_terminal_event", projection.lifecycle)

    def test_supersession_is_an_event_while_claims_remain_subjects(self) -> None:
        case = load_case("verification-supersession.json")

        self.assert_valid(case)
        subjects = {subject["id"]: subject for subject in case["subjects"]}
        self.assertEqual("claim", subjects["claim-broad-v1"]["kind"])
        self.assertEqual("claim", subjects["claim-narrow-v2"]["kind"])

        original = project_subject(case, "claim-broad-v1")
        successor = project_subject(case, "claim-narrow-v2")
        self.assertEqual("superseded", original.lifecycle)
        self.assertEqual("failed", original.verification)
        self.assertEqual("no_terminal_event", successor.lifecycle)

    def test_withdrawal_preserves_a_commitment_subject_and_its_failed_check(self) -> None:
        case = load_case("commitment-withdrawal.json")

        self.assert_valid(case)
        projection = project_subject(case, "commitment-single-score-v1")

        self.assertEqual("commitment", case["subjects"][0]["kind"])
        self.assertEqual("ratified", projection.governance)
        self.assertEqual("withdrawn", projection.lifecycle)
        self.assertEqual("failed", projection.verification)
        self.assertEqual("event-single-score-check", projection.verification_event_id)

    def test_rejects_status_fields_or_a_change_as_a_subject_kind(self) -> None:
        status_case = copy.deepcopy(load_case("proposal-ratification.json"))
        status_case["subjects"][0]["governance_status"] = "ratified"
        self.assert_has_code(status_case, "forbidden_field")

        type_case = copy.deepcopy(load_case("proposal-ratification.json"))
        type_case["subjects"][0]["kind"] = "superseded"
        self.assert_has_code(type_case, "invalid_subject_kind")

    def test_rejects_authority_status_and_agent_governance_decision(self) -> None:
        authority_case = copy.deepcopy(load_case("proposal-ratification.json"))
        decision = authority_case["events"][2]["decision"]
        decision["authority_basis"]["status"] = "ratified"
        self.assert_has_code(authority_case, "forbidden_field")

        agent_case = copy.deepcopy(load_case("proposal-ratification.json"))
        agent_case["events"][2]["decision"]["made_by"]["kind"] = "agent"
        self.assert_has_code(agent_case, "unauthorized_governance_decision")

        mixed_case = copy.deepcopy(load_case("proposal-ratification.json"))
        mixed_case["events"][0]["decision"] = copy.deepcopy(mixed_case["events"][2]["decision"])
        self.assert_has_code(mixed_case, "unexpected_field")
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        schema_errors = list(Draft202012Validator(schema).iter_errors(mixed_case))
        self.assertTrue(schema_errors, "the Schema must reject a decision on a non-governance event")

    def test_rejects_invalid_or_private_supersession(self) -> None:
        invalid_case = copy.deepcopy(load_case("verification-supersession.json"))
        invalid_case["events"][3]["successor_subject_id"] = "claim-broad-v1"
        self.assert_has_code(invalid_case, "invalid_supersession")

        private_case = copy.deepcopy(load_case("proposal-ratification.json"))
        private_case["subjects"][0]["raw_dialogue"] = "private conversation"
        self.assert_has_code(private_case, "forbidden_field")

        path_case = copy.deepcopy(load_case("proposal-ratification.json"))
        path_case["artifacts"][0]["locator"] = "C:\\Users\\person\\private.txt"
        self.assert_has_code(path_case, "private_value")

    def test_rejects_histories_that_need_last_write_wins(self) -> None:
        missing_creation = copy.deepcopy(load_case("proposal-ratification.json"))
        missing_creation["events"] = missing_creation["events"][1:]
        self.assert_has_code(missing_creation, "missing_subject_creation")
        self.assert_has_code(missing_creation, "invalid_event_order")

        no_review = copy.deepcopy(load_case("proposal-ratification.json"))
        no_review["events"].pop(1)
        self.assert_has_code(no_review, "invalid_governance_order")

        conflicting_terminal = copy.deepcopy(load_case("verification-supersession.json"))
        conflicting_terminal["events"].append(
            {
                "id": "event-claim-archived",
                "kind": "archived",
                "sequence": 5,
                "recorded_at": "2026-07-15T10:20:00Z",
                "recorded_by": {"kind": "human", "role": "repository_owner"},
                "public_summary": "合成範例中封存已替換的 Claim。",
                "subject_refs": ["claim-broad-v1"],
            }
        )
        self.assert_has_code(conflicting_terminal, "terminal_subject_referenced")

    def test_projection_identifies_the_latest_repeatable_report_without_erasing_history(self) -> None:
        case = copy.deepcopy(load_case("proposal-ratification.json"))
        case["evidence"].extend(
            [
                {
                    "id": "evidence-proposal-first-check",
                    "kind": "test_result",
                    "relation": "limits",
                    "subject_refs": ["proposal-subject-event-model"],
                    "artifact_refs": ["artifact-contract-v0"],
                    "public_summary": "第一份合成檢查只確認資料形狀。",
                },
                {
                    "id": "evidence-proposal-second-check",
                    "kind": "test_result",
                    "relation": "supports",
                    "subject_refs": ["proposal-subject-event-model"],
                    "artifact_refs": ["artifact-contract-v0"],
                    "public_summary": "第二份合成檢查確認列出的歷史規則。",
                },
            ]
        )
        case["events"].extend(
            [
                {
                    "id": "event-proposal-first-implemented",
                    "kind": "implementation_reported",
                    "sequence": 4,
                    "recorded_at": "2026-07-15T09:15:00Z",
                    "recorded_by": {"kind": "agent", "role": "assistant"},
                    "public_summary": "第一份合成實作報告為部分完成。",
                    "subject_refs": ["proposal-subject-event-model"],
                    "implementation": {
                        "outcome": "reported_partial",
                        "scope": "只建立了資料形狀。",
                        "limitations": ["尚未加入事件順序檢查。"],
                    },
                },
                {
                    "id": "event-proposal-first-verified",
                    "kind": "verification_recorded",
                    "sequence": 5,
                    "recorded_at": "2026-07-15T09:16:00Z",
                    "recorded_by": {"kind": "agent", "role": "assistant"},
                    "public_summary": "第一份合成驗證記錄為未定論。",
                    "subject_refs": ["proposal-subject-event-model"],
                    "evidence_refs": ["evidence-proposal-first-check"],
                    "verification": {
                        "outcome": "inconclusive",
                        "method": "synthetic first pass",
                        "scope": "只涵蓋結構形狀。",
                        "limitations": ["未檢查事件順序。"],
                    },
                },
                {
                    "id": "event-proposal-second-implemented",
                    "kind": "implementation_reported",
                    "sequence": 6,
                    "recorded_at": "2026-07-15T09:14:00Z",
                    "recorded_by": {"kind": "agent", "role": "assistant"},
                    "public_summary": "第二份合成實作報告為範圍內完成。",
                    "subject_refs": ["proposal-subject-event-model"],
                    "implementation": {
                        "outcome": "reported_implemented",
                        "scope": "加入列出的事件順序檢查。",
                        "limitations": ["未提供儲存或網路服務。"],
                    },
                },
                {
                    "id": "event-proposal-second-verified",
                    "kind": "verification_recorded",
                    "sequence": 7,
                    "recorded_at": "2026-07-15T09:10:00Z",
                    "recorded_by": {"kind": "agent", "role": "assistant"},
                    "public_summary": "第二份合成驗證記錄為範圍內通過。",
                    "subject_refs": ["proposal-subject-event-model"],
                    "evidence_refs": ["evidence-proposal-second-check"],
                    "verification": {
                        "outcome": "verified_within_scope",
                        "method": "synthetic second pass",
                        "scope": "涵蓋列出的結構與事件順序。",
                        "limitations": ["未涵蓋未列出的工作負載。"],
                    },
                },
            ]
        )

        self.assert_valid(case)
        projection = project_subject(case, "proposal-subject-event-model")

        self.assertLess(case["events"][-1]["recorded_at"], case["events"][-2]["recorded_at"])
        self.assertEqual("reported_implemented", projection.implementation)
        self.assertEqual("event-proposal-second-implemented", projection.implementation_event_id)
        self.assertEqual("verified_within_scope", projection.verification)
        self.assertEqual("event-proposal-second-verified", projection.verification_event_id)
        self.assertEqual(2, sum(event["kind"] == "implementation_reported" for event in case["events"]))
        self.assertEqual(2, sum(event["kind"] == "verification_recorded" for event in case["events"]))

    def test_rejects_unsafe_public_locators_and_references(self) -> None:
        locator_case = copy.deepcopy(load_case("proposal-ratification.json"))
        locator_case["artifacts"][0]["locator"] = "../../.env"
        self.assert_has_code(locator_case, "unsafe_locator")
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertTrue(list(Draft202012Validator(schema).iter_errors(locator_case)))

        reference_case = copy.deepcopy(load_case("proposal-ratification.json"))
        decision = reference_case["events"][2]["decision"]
        decision["made_by"]["role"] = "authorized_delegate"
        decision["authority_basis"] = {
            "kind": "explicit_delegation",
            "scope": ["public_schema_prototype"],
            "reference": "file:///private/delegation.txt",
        }
        self.assert_has_code(reference_case, "unsafe_reference")

        credential_case = copy.deepcopy(load_case("proposal-ratification.json"))
        credential_case["artifacts"][0]["revision"] = "ghp_abcdefghijklmnopqrstuv"
        self.assert_has_code(credential_case, "private_value")

    def test_unknown_subject_projection_has_a_clear_error(self) -> None:
        case = load_case("proposal-ratification.json")

        with self.assertRaisesRegex(ValueError, "unknown subject"):
            project_subject(case, "proposal-not-present")


if __name__ == "__main__":
    unittest.main()
