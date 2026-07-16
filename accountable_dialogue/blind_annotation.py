"""Build condition-blind, public-safe packets for future semantic annotation.

This module does not generate model answers, assign labels, store rater identity,
or reveal a B0/I1 mapping.  It only converts two already mechanically-valid
synthetic responses into separate packets containing shared material and a
precommitted case-local rubric.
"""

from __future__ import annotations

import copy
import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from accountable_dialogue.synthetic_pilot import (
    RESPONSE_FIELDS,
    canonical_json_digest,
    validate_annotation_key,
    validate_case,
)

BLIND_ANNOTATION_PACKET_FORMAT = "accountable-dialogue/blind-semantic-annotation-packet-v0"
BLIND_ALIASES = frozenset({"A", "B"})
PACKET_KEYS = frozenset(
    {
        "format",
        "packet_id",
        "case_id",
        "blind_alias",
        "shared_task",
        "shared_materials",
        "response",
        "rubric",
        "rubric_sha256",
        "mechanical_status",
        "known_limitations",
    }
)
SHARED_MATERIAL_KEYS = frozenset({"id", "kind", "text"})
RUBRIC_KEYS = frozenset({"key_id", "labels", "allowed_verdicts"})
RUBRIC_LABEL_KEYS = frozenset({"id", "pass_when", "fail_when"})
ALLOWED_VERDICTS = frozenset({"pass", "fail", "not_applicable", "unrateable"})
ID_PATTERN = re.compile(r"^[a-z][a-z0-9-]{2,63}$")
LABEL_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_-]{2,63}$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
PRIVATE_VALUE_PATTERNS = (
    re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b"),
    re.compile(r"(?:^[A-Za-z]:[\\/]|^/(?:Users|home)/)"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
)


@dataclass(frozen=True)
class BlindAnnotationIssue:
    """Public-safe structural or privacy issue in a blind annotation packet."""

    path: str
    code: str
    message: str


def build_blind_annotation_packets(
    *,
    case: Mapping[str, Any],
    annotation_key: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
) -> tuple[dict[str, object], ...]:
    """Create exactly one condition-blind packet per A/B response alias.

    The caller must keep the condition mapping outside the rater's packet.  Any
    unrateable, duplicate, non-paired, changed-key, or non-public-safe input is
    rejected rather than silently excluded.
    """

    case_issues = validate_case(case)
    if case_issues:
        rendered = "; ".join(f"{issue.path}: {issue.message}" for issue in case_issues)
        raise ValueError(f"cannot packetize invalid synthetic case: {rendered}")
    key_issues = validate_annotation_key(annotation_key)
    if key_issues:
        rendered = "; ".join(f"{issue.path}: {issue.message}" for issue in key_issues)
        raise ValueError(f"cannot packetize invalid annotation key: {rendered}")

    case_id = _required_string(case, "case_id")
    expected_digest = _annotation_key_digest_from_case(case)
    actual_digest = canonical_json_digest(annotation_key)
    if actual_digest != expected_digest:
        raise ValueError("annotation key digest does not match the fixture commitment")
    rubric_labels = _labels_for_case(annotation_key, case_id)
    normalized_rows = _validate_rows(rows, case_id)
    shared_materials = [
        {"id": item["id"], "kind": item["kind"], "text": item["text"]}
        for item in case["materials"]
    ]
    rubric = {
        "key_id": _required_string(annotation_key, "key_id"),
        "labels": copy.deepcopy(rubric_labels),
        "allowed_verdicts": sorted(ALLOWED_VERDICTS),
    }

    packets: list[dict[str, object]] = []
    for alias in ("A", "B"):
        row = normalized_rows[alias]
        response = _parse_valid_response(row["raw_response"])
        packet: dict[str, object] = {
            "format": BLIND_ANNOTATION_PACKET_FORMAT,
            "packet_id": f"blind-{case_id}-{alias.lower()}",
            "case_id": case_id,
            "blind_alias": alias,
            "shared_task": case["task"],
            "shared_materials": copy.deepcopy(shared_materials),
            "response": response,
            "rubric": copy.deepcopy(rubric),
            "rubric_sha256": expected_digest,
            "mechanical_status": "valid",
            "known_limitations": [
                "此 packet 只支援對完全合成輸出的獨立可觀察標註，不測量模型內在性質。",
                "packet 不含 B0／I1 mapping、condition-specific structured context、模型、provider 或 settings。",
                "此 rubric 已在輸出前由 fixture digest 鎖定；它不保證語義標註者之間必然一致。",
            ],
        }
        issues = validate_blind_annotation_packet(packet)
        if issues:
            rendered = "; ".join(f"{issue.path}: {issue.message}" for issue in issues)
            raise ValueError(f"generated invalid blind annotation packet: {rendered}")
        packets.append(packet)
    return tuple(packets)


def validate_blind_annotation_packet(packet: Mapping[str, Any] | object) -> list[BlindAnnotationIssue]:
    """Validate a closed, condition-blind packet without evaluating its verdicts."""

    issues: list[BlindAnnotationIssue] = []
    _find_private_content(packet, "$", issues)
    if not isinstance(packet, Mapping):
        _issue(issues, "$", "invalid_type", "packet must be an object")
        return issues

    _check_keys(packet, PACKET_KEYS, "$", issues)
    _require_keys(packet, PACKET_KEYS, "$", issues)
    if packet.get("format") != BLIND_ANNOTATION_PACKET_FORMAT:
        _issue(issues, "$.format", "invalid_format", "unexpected blind annotation packet format")
    _validate_id(packet.get("packet_id"), "$.packet_id", issues)
    _validate_id(packet.get("case_id"), "$.case_id", issues)
    if packet.get("blind_alias") not in BLIND_ALIASES:
        _issue(issues, "$.blind_alias", "invalid_alias", "blind alias must be A or B")
    _validate_text(packet.get("shared_task"), "$.shared_task", issues, "shared task")
    _validate_shared_materials(packet.get("shared_materials"), "$.shared_materials", issues)
    _validate_response(packet.get("response"), "$.response", issues)
    _validate_rubric(packet.get("rubric"), "$.rubric", issues)
    digest = packet.get("rubric_sha256")
    if not isinstance(digest, str) or not SHA256_PATTERN.fullmatch(digest):
        _issue(issues, "$.rubric_sha256", "invalid_digest", "rubric digest must be lowercase SHA-256")
    if packet.get("mechanical_status") != "valid":
        _issue(issues, "$.mechanical_status", "invalid_status", "packet may contain only mechanically valid output")
    _validate_text_list(packet.get("known_limitations"), "$.known_limitations", issues, minimum=1)
    return issues


def _annotation_key_digest_from_case(case: Mapping[str, Any]) -> str:
    reference = case.get("annotation_key")
    if not isinstance(reference, Mapping):
        raise ValueError("synthetic case annotation key reference is invalid")
    digest = reference.get("sha256")
    if not isinstance(digest, str):
        raise ValueError("synthetic case annotation key digest is invalid")
    return digest


def _labels_for_case(annotation_key: Mapping[str, Any], case_id: str) -> list[dict[str, object]]:
    expectations = annotation_key.get("case_expectations")
    if not isinstance(expectations, list):
        raise ValueError("annotation key has no case expectations")
    matches = [item for item in expectations if isinstance(item, Mapping) and item.get("case_id") == case_id]
    if len(matches) != 1:
        raise ValueError(f"annotation key must have exactly one expectation for {case_id}")
    labels = matches[0].get("labels")
    if not isinstance(labels, list):
        raise ValueError(f"annotation key labels are invalid for {case_id}")
    return [dict(label) for label in labels if isinstance(label, Mapping)]


def _validate_rows(rows: Sequence[Mapping[str, Any]], case_id: str) -> dict[str, Mapping[str, Any]]:
    if len(rows) != 2:
        raise ValueError("blind annotation packetization requires exactly two paired rows")
    by_alias: dict[str, Mapping[str, Any]] = {}
    models: set[str] = set()
    for index, row in enumerate(rows):
        if row.get("case_id") != case_id:
            raise ValueError(f"row {index} does not belong to case {case_id}")
        alias = row.get("condition_alias")
        if alias not in BLIND_ALIASES or not isinstance(alias, str):
            raise ValueError("blind annotation packetization requires exactly aliases A and B")
        if alias in by_alias:
            raise ValueError("blind annotation packetization requires exactly aliases A and B")
        if row.get("mechanical_status") != "valid":
            raise ValueError("blind annotation packetization requires mechanically valid rows")
        raw_response = row.get("raw_response")
        if not isinstance(raw_response, str):
            raise ValueError("blind annotation packetization requires a raw response string")
        model = row.get("model")
        if not isinstance(model, str) or not model:
            raise ValueError("blind annotation packetization requires one named model")
        models.add(model)
        by_alias[alias] = row
    if set(by_alias) != BLIND_ALIASES:
        raise ValueError("blind annotation packetization requires exactly aliases A and B")
    if len(models) != 1:
        raise ValueError("blind annotation packetization requires one model per paired case")
    return by_alias


def _parse_valid_response(value: object) -> dict[str, object]:
    if not isinstance(value, str):
        raise ValueError("blind annotation packetization requires a raw response string")
    try:
        response = json.loads(value)
    except json.JSONDecodeError as error:
        raise ValueError("blind annotation packetization requires parseable output") from error
    issues: list[BlindAnnotationIssue] = []
    _validate_response(response, "$.response", issues)
    if issues:
        rendered = "; ".join(f"{issue.path}: {issue.message}" for issue in issues)
        raise ValueError(f"blind annotation packetization requires a valid response envelope: {rendered}")
    return dict(response)


def _validate_shared_materials(value: object, path: str, issues: list[BlindAnnotationIssue]) -> None:
    if not isinstance(value, list) or not value:
        _issue(issues, path, "invalid_list", "shared materials must be a non-empty list")
        return
    seen_ids: set[str] = set()
    for index, material in enumerate(value):
        material_path = f"{path}[{index}]"
        if not isinstance(material, Mapping):
            _issue(issues, material_path, "invalid_type", "shared material must be an object")
            continue
        _check_keys(material, SHARED_MATERIAL_KEYS, material_path, issues)
        _require_keys(material, SHARED_MATERIAL_KEYS, material_path, issues)
        material_id = material.get("id")
        if _validate_id(material_id, f"{material_path}.id", issues) and isinstance(material_id, str):
            if material_id in seen_ids:
                _issue(issues, f"{material_path}.id", "duplicate_id", "shared material ids must be unique")
            seen_ids.add(material_id)
        _validate_text(material.get("kind"), f"{material_path}.kind", issues, "shared material kind")
        _validate_text(material.get("text"), f"{material_path}.text", issues, "shared material text")


def _validate_response(value: object, path: str, issues: list[BlindAnnotationIssue]) -> None:
    if not isinstance(value, Mapping):
        _issue(issues, path, "invalid_type", "response must be an object")
        return
    _check_keys(value, frozenset(RESPONSE_FIELDS), path, issues)
    _require_keys(value, frozenset(RESPONSE_FIELDS), path, issues)
    for field in RESPONSE_FIELDS:
        field_path = f"{path}.{field}"
        if field == "evidence_refs":
            evidence_refs = value.get(field)
            if not isinstance(evidence_refs, list) or not evidence_refs or any(
                not isinstance(item, str) or not item.strip() for item in evidence_refs
            ):
                _issue(issues, field_path, "invalid_evidence_refs", "evidence refs must be a non-empty string list")
        else:
            _validate_text(value.get(field), field_path, issues, field)


def _validate_rubric(value: object, path: str, issues: list[BlindAnnotationIssue]) -> None:
    if not isinstance(value, Mapping):
        _issue(issues, path, "invalid_type", "rubric must be an object")
        return
    _check_keys(value, RUBRIC_KEYS, path, issues)
    _require_keys(value, RUBRIC_KEYS, path, issues)
    _validate_id(value.get("key_id"), f"{path}.key_id", issues)
    verdicts = value.get("allowed_verdicts")
    if not isinstance(verdicts, list) or set(verdicts) != ALLOWED_VERDICTS or len(verdicts) != len(ALLOWED_VERDICTS):
        _issue(issues, f"{path}.allowed_verdicts", "invalid_verdicts", "rubric must include the four allowed verdicts")
    labels = value.get("labels")
    if not isinstance(labels, list) or not labels:
        _issue(issues, f"{path}.labels", "invalid_list", "rubric labels must be a non-empty list")
        return
    seen_labels: set[str] = set()
    for index, label in enumerate(labels):
        label_path = f"{path}.labels[{index}]"
        if not isinstance(label, Mapping):
            _issue(issues, label_path, "invalid_type", "rubric label must be an object")
            continue
        _check_keys(label, RUBRIC_LABEL_KEYS, label_path, issues)
        _require_keys(label, RUBRIC_LABEL_KEYS, label_path, issues)
        label_id = label.get("id")
        if isinstance(label_id, str) and LABEL_ID_PATTERN.fullmatch(label_id):
            if label_id in seen_labels:
                _issue(issues, f"{label_path}.id", "duplicate_id", "rubric label ids must be unique")
            seen_labels.add(label_id)
        else:
            _issue(issues, f"{label_path}.id", "invalid_id", "rubric label id is invalid")
        _validate_text(label.get("pass_when"), f"{label_path}.pass_when", issues, "pass condition")
        _validate_text(label.get("fail_when"), f"{label_path}.fail_when", issues, "fail condition")


def _validate_text_list(value: object, path: str, issues: list[BlindAnnotationIssue], *, minimum: int) -> None:
    if not isinstance(value, list) or len(value) < minimum:
        _issue(issues, path, "invalid_list", f"list must contain at least {minimum} item(s)")
        return
    for index, item in enumerate(value):
        _validate_text(item, f"{path}[{index}]", issues, "list item")


def _required_string(value: Mapping[str, Any], key: str) -> str:
    candidate = value.get(key)
    if not isinstance(candidate, str) or not candidate:
        raise ValueError(f"required string {key!r} is invalid")
    return candidate


def _validate_id(value: object, path: str, issues: list[BlindAnnotationIssue]) -> bool:
    if not isinstance(value, str) or not ID_PATTERN.fullmatch(value):
        _issue(issues, path, "invalid_id", "id must be a public-safe lowercase identifier")
        return False
    return True


def _validate_text(value: object, path: str, issues: list[BlindAnnotationIssue], label: str) -> None:
    if not isinstance(value, str) or not value.strip() or len(value) > 2000:
        _issue(issues, path, "invalid_text", f"{label} must be non-empty and at most 2000 characters")


def _check_keys(
    value: Mapping[str, Any], allowed: frozenset[str], path: str, issues: list[BlindAnnotationIssue]
) -> None:
    for key in value:
        if key not in allowed:
            _issue(issues, f"{path}.{key}", "unexpected_field", f"field {key!r} is not part of blind packet v0")


def _require_keys(
    value: Mapping[str, Any], required: frozenset[str], path: str, issues: list[BlindAnnotationIssue]
) -> None:
    for key in required:
        if key not in value:
            _issue(issues, f"{path}.{key}", "missing_field", f"missing required field {key!r}")


def _find_private_content(value: object, path: str, issues: list[BlindAnnotationIssue]) -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            _find_private_content(nested, f"{path}.{key}", issues)
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _find_private_content(nested, f"{path}[{index}]", issues)
    elif isinstance(value, str) and any(pattern.search(value) for pattern in PRIVATE_VALUE_PATTERNS):
        _issue(issues, path, "private_value", "value resembles private contact, credential, or absolute local-path data")


def _issue(issues: list[BlindAnnotationIssue], path: str, code: str, message: str) -> None:
    issues.append(BlindAnnotationIssue(path=path, code=code, message=message))
