from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from accountable_dialogue.blind_annotation import (
    BLIND_ANNOTATION_PACKET_FORMAT,
    build_blind_annotation_packets,
    validate_blind_annotation_packet,
)

ROOT = Path(__file__).resolve().parents[1]
CASE_PATH = ROOT / "fixtures" / "synthetic-pilot-v0" / "cases" / "h1-incomplete-library-hours.json"
KEY_PATH = ROOT / "fixtures" / "synthetic-pilot-v0" / "annotation-key-v0.json"
SCHEMA_PATH = ROOT / "schemas" / "blind-semantic-annotation-packet-v0.schema.json"


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def valid_rows(case_id: str) -> tuple[dict[str, object], ...]:
    return (
        {
            "case_id": case_id,
            "model": "tiny-local:latest",
            "condition_alias": "A",
            "mechanical_status": "valid",
            "raw_response": json.dumps(
                {
                    "conclusion": "材料不足以保證週日開館。",
                    "evidence_refs": ["source-hours-weekdays"],
                    "prior_claim_ref": "claim-sunday-opening",
                    "unknown_or_correction": "需要查核週日時間。",
                    "authority_next_step": "提出查核建議。",
                },
                ensure_ascii=False,
            ),
        },
        {
            "case_id": case_id,
            "model": "tiny-local:latest",
            "condition_alias": "B",
            "mechanical_status": "valid",
            "raw_response": json.dumps(
                {
                    "conclusion": "沒有材料可保證週日開館。",
                    "evidence_refs": ["source-hours-weekdays"],
                    "prior_claim_ref": "not_applicable",
                    "unknown_or_correction": "週日資訊未知。",
                    "authority_next_step": "not_applicable",
                },
                ensure_ascii=False,
            ),
        },
    )


class BlindAnnotationPacketTests(unittest.TestCase):
    def setUp(self) -> None:
        self.case = load_json(CASE_PATH)
        self.annotation_key = load_json(KEY_PATH)
        self.rows = valid_rows(str(self.case["case_id"]))

    def test_builds_two_public_safe_blind_packets_from_valid_outputs(self) -> None:
        packets = build_blind_annotation_packets(
            case=self.case,
            annotation_key=self.annotation_key,
            rows=self.rows,
        )
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        schema_validator = Draft202012Validator(schema)

        self.assertEqual(2, len(packets))
        self.assertEqual(["A", "B"], [packet["blind_alias"] for packet in packets])
        expected_labels = next(
            item["labels"]
            for item in self.annotation_key["case_expectations"]
            if item["case_id"] == self.case["case_id"]
        )
        for packet in packets:
            self.assertEqual(BLIND_ANNOTATION_PACKET_FORMAT, packet["format"])
            self.assertEqual([], validate_blind_annotation_packet(packet))
            self.assertEqual([], list(schema_validator.iter_errors(packet)))
            self.assertEqual(self.case["task"], packet["shared_task"])
            self.assertEqual(self.case["annotation_key"]["sha256"], packet["rubric_sha256"])
            self.assertEqual(expected_labels, packet["rubric"]["labels"])
            self.assertEqual("valid", packet["mechanical_status"])
            self.assertEqual(
                [material["id"] for material in self.case["materials"]],
                [material["id"] for material in packet["shared_materials"]],
            )
            for forbidden_key in ("condition", "structured_context", "model", "provider", "settings", "annotation_key"):
                self.assertNotIn(forbidden_key, packet)

    def test_builder_rejects_unrateable_or_unblinded_input_without_silently_dropping_it(self) -> None:
        invalid_status = [dict(row) for row in self.rows]
        invalid_status[1]["mechanical_status"] = "missing_evidence_ref"
        with self.assertRaisesRegex(ValueError, "mechanically valid"):
            build_blind_annotation_packets(
                case=self.case,
                annotation_key=self.annotation_key,
                rows=invalid_status,
            )

        duplicate_alias = [dict(row) for row in self.rows]
        duplicate_alias[1]["condition_alias"] = "A"
        with self.assertRaisesRegex(ValueError, "exactly aliases A and B"):
            build_blind_annotation_packets(
                case=self.case,
                annotation_key=self.annotation_key,
                rows=duplicate_alias,
            )

        changed_key = copy.deepcopy(self.annotation_key)
        changed_key["case_expectations"][0]["labels"][0]["pass_when"] = "changed after fixture commitment"
        with self.assertRaisesRegex(ValueError, "digest"):
            build_blind_annotation_packets(
                case=self.case,
                annotation_key=changed_key,
                rows=self.rows,
            )

    def test_packet_validator_rejects_condition_mapping_or_unclosed_fields(self) -> None:
        packet = build_blind_annotation_packets(
            case=self.case,
            annotation_key=self.annotation_key,
            rows=self.rows,
        )[0]

        mapped_packet = copy.deepcopy(packet)
        mapped_packet["condition"] = "I1_structured_context"
        self.assertIn("unexpected_field", {issue.code for issue in validate_blind_annotation_packet(mapped_packet)})

        exposed_packet = copy.deepcopy(packet)
        exposed_packet["shared_materials"][0]["structured_context"] = {"leak": True}
        self.assertIn("unexpected_field", {issue.code for issue in validate_blind_annotation_packet(exposed_packet)})


if __name__ == "__main__":
    unittest.main()
