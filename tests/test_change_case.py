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


if __name__ == "__main__":
    unittest.main()
