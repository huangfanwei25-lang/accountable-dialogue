from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from accountable_dialogue.change_case import project_subject, validate_change_case

ROOT = Path(__file__).resolve().parents[1]
RECORDS = ROOT / "records" / "change-case-v0"
SCHEMA = ROOT / "schemas" / "change-case-v0.schema.json"


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


if __name__ == "__main__":
    unittest.main()
