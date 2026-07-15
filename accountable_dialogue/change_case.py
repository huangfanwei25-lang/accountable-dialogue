"""Validation and read-only projections for the public change-case-v0 format.

The format deliberately separates the subject under discussion from evidence,
artifacts, and events that later occur.  This module validates only public,
bounded JSON-like values; it does not persist, transmit, or infer private data.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Any

FORMAT = "accountable-dialogue/change-case-v0"

SUBJECT_KINDS = frozenset({"observation", "claim", "proposal", "commitment"})
ARTIFACT_KINDS = frozenset({"document", "schema", "source_file", "test", "external_source"})
EVIDENCE_KINDS = frozenset(
    {
        "test_result",
        "schema_check",
        "artifact_review",
        "source",
        "runtime_observation",
        "attestation",
    }
)
EVIDENCE_RELATIONS = frozenset({"supports", "challenges", "limits"})
EVENT_KINDS = frozenset(
    {
        "subject_created",
        "review_requested",
        "governance_decided",
        "implementation_reported",
        "verification_recorded",
        "withdrawn",
        "superseded",
        "archived",
    }
)
DECISION_OUTCOMES = frozenset({"ratified", "rejected"})
IMPLEMENTATION_OUTCOMES = frozenset({"reported_partial", "reported_implemented"})
VERIFICATION_OUTCOMES = frozenset(
    {"inconclusive", "partially_verified", "verified_within_scope", "failed"}
)

TOP_LEVEL_KEYS = frozenset(
    {"format", "case_id", "public_summary", "visibility", "subjects", "artifacts", "evidence", "events"}
)
SUBJECT_KEYS = frozenset({"id", "kind", "public_summary"})
ARTIFACT_KEYS = frozenset({"id", "kind", "locator", "revision"})
EVIDENCE_KEYS = frozenset(
    {"id", "kind", "relation", "subject_refs", "artifact_refs", "public_summary"}
)
COMMON_EVENT_KEYS = frozenset(
    {
        "id",
        "kind",
        "sequence",
        "recorded_at",
        "recorded_by",
        "public_summary",
    }
)
EVENT_PAYLOAD_KEYS = {
    "subject_created": frozenset({"subject_refs"}),
    "review_requested": frozenset({"subject_refs"}),
    "governance_decided": frozenset({"subject_refs", "decision"}),
    "implementation_reported": frozenset({"subject_refs", "implementation"}),
    "verification_recorded": frozenset({"subject_refs", "evidence_refs", "verification"}),
    "withdrawn": frozenset({"subject_refs"}),
    "superseded": frozenset({"previous_subject_id", "successor_subject_id"}),
    "archived": frozenset({"subject_refs"}),
}
ALL_EVENT_KEYS = COMMON_EVENT_KEYS | frozenset(
    {
        "subject_refs",
        "evidence_refs",
        "decision",
        "implementation",
        "verification",
        "previous_subject_id",
        "successor_subject_id",
    }
)
ACTOR_KEYS = frozenset({"kind", "role"})
DECISION_KEYS = frozenset({"outcome", "made_by", "authority_basis", "effective_at"})
AUTHORITY_BASIS_KEYS = frozenset({"kind", "scope", "reference"})
IMPLEMENTATION_KEYS = frozenset({"outcome", "scope", "limitations"})
VERIFICATION_KEYS = frozenset({"outcome", "method", "scope", "limitations"})

FORBIDDEN_FIELD_NAMES = frozenset(
    {
        "api_key",
        "authority",
        "email",
        "engineering_status",
        "governance_status",
        "hidden_reasoning",
        "lifecycle_status",
        "password",
        "private_context",
        "prompt",
        "raw_dialogue",
        "status",
        "supersedes",
        "token",
        "verification_status",
    }
)

ID_PATTERN = re.compile(r"^[a-z][a-z0-9-]{2,63}$")
ROLE_PATTERN = re.compile(r"^[a-z][a-z0-9_-]{1,63}$")
PRIVATE_VALUE_PATTERNS = (
    re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b"),
    re.compile(r"(?:^[A-Za-z]:[\\/]|^/(?:Users|home)/)"),
    re.compile(r"\b(?:sk|ghp|github_pat)-[A-Za-z0-9_-]{8,}\b"),
)


@dataclass(frozen=True)
class ValidationIssue:
    """A deterministic, public-safe explanation of a rejected value."""

    path: str
    code: str
    message: str


@dataclass(frozen=True)
class SubjectProjection:
    """A read-only statement that can be recomputed from a valid change case."""

    subject_id: str
    subject_kind: str
    governance: str
    lifecycle: str
    implementation: str
    verification: str


def validate_change_case(case: Mapping[str, Any] | object) -> list[ValidationIssue]:
    """Return all discoverable public-format issues without mutating *case*.

    The validator intentionally has a closed input shape.  It can block known
    private-looking fields and contradictions, but it cannot prove that prose
    contains no sensitive information.
    """

    issues: list[ValidationIssue] = []
    _find_forbidden_content(case, "$", issues)
    if not isinstance(case, Mapping):
        _issue(issues, "$", "invalid_type", "change case must be an object")
        return issues

    _check_keys(case, TOP_LEVEL_KEYS, "$", issues)
    _require_keys(
        case,
        ("format", "case_id", "public_summary", "visibility", "subjects", "artifacts", "evidence", "events"),
        "$",
        issues,
    )
    if case.get("format") != FORMAT:
        _issue(issues, "$.format", "invalid_format", f"format must be {FORMAT!r}")
    _validate_id(case.get("case_id"), "$.case_id", issues)
    _validate_summary(case.get("public_summary"), "$.public_summary", issues)
    if case.get("visibility") != "public":
        _issue(issues, "$.visibility", "invalid_visibility", "v0 only accepts public cases")

    subjects = _validate_list(case.get("subjects"), "$.subjects", issues)
    artifacts = _validate_list(case.get("artifacts"), "$.artifacts", issues)
    evidence = _validate_list(case.get("evidence"), "$.evidence", issues)
    events = _validate_list(case.get("events"), "$.events", issues)

    if subjects is not None and not subjects:
        _issue(issues, "$.subjects", "missing_subject", "a change case needs at least one subject")

    subject_ids = _validate_subjects(subjects, issues)
    artifact_ids = _validate_artifacts(artifacts, issues)
    evidence_ids = _validate_evidence(evidence, subject_ids, artifact_ids, issues)
    _validate_events(events, subject_ids, evidence_ids, issues)
    _validate_global_ids(subjects, artifacts, evidence, events, issues)
    return issues


def project_subject(case: Mapping[str, Any], subject_id: str) -> SubjectProjection:
    """Derive a subject view from a valid case without writing any state back.

    Absence is represented explicitly.  For example, no verification event
    yields ``no_verification_record`` rather than a claim that verification did
    not happen in the world.
    """

    issues = validate_change_case(case)
    if issues:
        rendered = "; ".join(f"{issue.path}: {issue.message}" for issue in issues)
        raise ValueError(f"cannot project an invalid change case: {rendered}")

    subjects = case["subjects"]
    subject = next(item for item in subjects if item["id"] == subject_id)
    governance = "no_governance_record"
    lifecycle = "no_terminal_event"
    implementation = "no_implementation_report"
    verification = "no_verification_record"

    for event in sorted(case["events"], key=lambda item: item["sequence"]):
        event_kind = event["kind"]
        subject_refs = event.get("subject_refs", [])

        if subject_id in subject_refs:
            if event_kind == "review_requested":
                governance = "under_review"
            elif event_kind == "governance_decided":
                governance = event["decision"]["outcome"]
            elif event_kind == "implementation_reported":
                implementation = event["implementation"]["outcome"]
            elif event_kind == "verification_recorded":
                verification = event["verification"]["outcome"]
            elif event_kind == "withdrawn":
                lifecycle = "withdrawn"
            elif event_kind == "archived":
                lifecycle = "archived"

        if event_kind == "superseded" and event["previous_subject_id"] == subject_id:
            lifecycle = "superseded"

    return SubjectProjection(
        subject_id=subject_id,
        subject_kind=subject["kind"],
        governance=governance,
        lifecycle=lifecycle,
        implementation=implementation,
        verification=verification,
    )


def _validate_subjects(
    items: list[object] | None, issues: list[ValidationIssue]
) -> set[str]:
    identifiers: set[str] = set()
    if items is None:
        return identifiers

    for index, item in enumerate(items):
        path = f"$.subjects[{index}]"
        if not isinstance(item, Mapping):
            _issue(issues, path, "invalid_type", "subject must be an object")
            continue
        _check_keys(item, SUBJECT_KEYS, path, issues)
        _require_keys(item, ("id", "kind", "public_summary"), path, issues)
        identifier = item.get("id")
        if _validate_id(identifier, f"{path}.id", issues):
            _register_id(identifier, identifiers, f"{path}.id", issues)
        if item.get("kind") not in SUBJECT_KINDS:
            _issue(
                issues,
                f"{path}.kind",
                "invalid_subject_kind",
                f"subject kind must be one of {sorted(SUBJECT_KINDS)}",
            )
        _validate_summary(item.get("public_summary"), f"{path}.public_summary", issues)
    return identifiers


def _validate_artifacts(
    items: list[object] | None, issues: list[ValidationIssue]
) -> set[str]:
    identifiers: set[str] = set()
    if items is None:
        return identifiers

    for index, item in enumerate(items):
        path = f"$.artifacts[{index}]"
        if not isinstance(item, Mapping):
            _issue(issues, path, "invalid_type", "artifact must be an object")
            continue
        _check_keys(item, ARTIFACT_KEYS, path, issues)
        _require_keys(item, ("id", "kind", "locator", "revision"), path, issues)
        identifier = item.get("id")
        if _validate_id(identifier, f"{path}.id", issues):
            _register_id(identifier, identifiers, f"{path}.id", issues)
        if item.get("kind") not in ARTIFACT_KINDS:
            _issue(
                issues,
                f"{path}.kind",
                "invalid_artifact_kind",
                f"artifact kind must be one of {sorted(ARTIFACT_KINDS)}",
            )
        _validate_short_text(item.get("locator"), f"{path}.locator", issues, "locator")
        _validate_short_text(item.get("revision"), f"{path}.revision", issues, "revision")
    return identifiers


def _validate_evidence(
    items: list[object] | None,
    subject_ids: set[str],
    artifact_ids: set[str],
    issues: list[ValidationIssue],
) -> set[str]:
    identifiers: set[str] = set()
    if items is None:
        return identifiers

    for index, item in enumerate(items):
        path = f"$.evidence[{index}]"
        if not isinstance(item, Mapping):
            _issue(issues, path, "invalid_type", "evidence must be an object")
            continue
        _check_keys(item, EVIDENCE_KEYS, path, issues)
        _require_keys(
            item,
            ("id", "kind", "relation", "subject_refs", "artifact_refs", "public_summary"),
            path,
            issues,
        )
        identifier = item.get("id")
        if _validate_id(identifier, f"{path}.id", issues):
            _register_id(identifier, identifiers, f"{path}.id", issues)
        if item.get("kind") not in EVIDENCE_KINDS:
            _issue(
                issues,
                f"{path}.kind",
                "invalid_evidence_kind",
                f"evidence kind must be one of {sorted(EVIDENCE_KINDS)}",
            )
        if item.get("relation") not in EVIDENCE_RELATIONS:
            _issue(
                issues,
                f"{path}.relation",
                "invalid_evidence_relation",
                f"evidence relation must be one of {sorted(EVIDENCE_RELATIONS)}",
            )
        _validate_references(item.get("subject_refs"), subject_ids, f"{path}.subject_refs", "subject", issues)
        _validate_references(item.get("artifact_refs"), artifact_ids, f"{path}.artifact_refs", "artifact", issues)
        _validate_summary(item.get("public_summary"), f"{path}.public_summary", issues)
    return identifiers


def _validate_events(
    items: list[object] | None,
    subject_ids: set[str],
    evidence_ids: set[str],
    issues: list[ValidationIssue],
) -> None:
    if items is None:
        return

    event_ids: set[str] = set()
    seen_sequences: set[int] = set()
    last_sequence = 0
    for index, item in enumerate(items):
        path = f"$.events[{index}]"
        if not isinstance(item, Mapping):
            _issue(issues, path, "invalid_type", "event must be an object")
            continue
        kind = item.get("kind")
        allowed_keys = COMMON_EVENT_KEYS | EVENT_PAYLOAD_KEYS.get(kind, ALL_EVENT_KEYS)
        _check_keys(item, allowed_keys, path, issues)
        _require_keys(
            item,
            ("id", "kind", "sequence", "recorded_at", "recorded_by", "public_summary"),
            path,
            issues,
        )
        identifier = item.get("id")
        if _validate_id(identifier, f"{path}.id", issues):
            _register_id(identifier, event_ids, f"{path}.id", issues)

        if kind not in EVENT_KINDS:
            _issue(
                issues,
                f"{path}.kind",
                "invalid_event_kind",
                f"event kind must be one of {sorted(EVENT_KINDS)}",
            )
        sequence = item.get("sequence")
        if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1:
            _issue(issues, f"{path}.sequence", "invalid_sequence", "sequence must be a positive integer")
        elif sequence in seen_sequences or sequence <= last_sequence:
            _issue(
                issues,
                f"{path}.sequence",
                "invalid_sequence",
                "event sequences must be unique and listed in ascending order",
            )
        else:
            seen_sequences.add(sequence)
            last_sequence = sequence

        _validate_timestamp(item.get("recorded_at"), f"{path}.recorded_at", issues)
        _validate_actor(item.get("recorded_by"), f"{path}.recorded_by", issues)
        _validate_summary(item.get("public_summary"), f"{path}.public_summary", issues)

        if kind in {
            "subject_created",
            "review_requested",
            "governance_decided",
            "implementation_reported",
            "verification_recorded",
            "withdrawn",
            "archived",
        }:
            _validate_references(item.get("subject_refs"), subject_ids, f"{path}.subject_refs", "subject", issues)

        if kind == "governance_decided":
            _validate_decision(item.get("decision"), f"{path}.decision", issues)
        elif kind == "implementation_reported":
            _validate_implementation(item.get("implementation"), f"{path}.implementation", issues)
        elif kind == "verification_recorded":
            _validate_references(item.get("evidence_refs"), evidence_ids, f"{path}.evidence_refs", "evidence", issues)
            _validate_verification(item.get("verification"), f"{path}.verification", issues)
        elif kind == "superseded":
            _validate_supersession(item, path, subject_ids, issues)


def _validate_global_ids(
    subjects: list[object] | None,
    artifacts: list[object] | None,
    evidence: list[object] | None,
    events: list[object] | None,
    issues: list[ValidationIssue],
) -> None:
    seen: dict[str, str] = {}
    for collection_name, items in (
        ("subjects", subjects),
        ("artifacts", artifacts),
        ("evidence", evidence),
        ("events", events),
    ):
        if items is None:
            continue
        for index, item in enumerate(items):
            if not isinstance(item, Mapping) or not isinstance(item.get("id"), str):
                continue
            identifier = item["id"]
            path = f"$.{collection_name}[{index}].id"
            if identifier in seen:
                _issue(
                    issues,
                    path,
                    "duplicate_id",
                    f"id {identifier!r} is already used at {seen[identifier]}",
                )
            else:
                seen[identifier] = path


def _validate_decision(value: object, path: str, issues: list[ValidationIssue]) -> None:
    if not isinstance(value, Mapping):
        _issue(issues, path, "missing_decision", "governance_decided requires a decision object")
        return
    _check_keys(value, DECISION_KEYS, path, issues)
    _require_keys(value, ("outcome", "made_by", "authority_basis", "effective_at"), path, issues)
    if value.get("outcome") not in DECISION_OUTCOMES:
        _issue(
            issues,
            f"{path}.outcome",
            "invalid_decision_outcome",
            f"decision outcome must be one of {sorted(DECISION_OUTCOMES)}",
        )
    made_by = value.get("made_by")
    _validate_actor(made_by, f"{path}.made_by", issues)
    authority = value.get("authority_basis")
    _validate_authority_basis(authority, f"{path}.authority_basis", issues)
    _validate_timestamp(value.get("effective_at"), f"{path}.effective_at", issues)

    if isinstance(made_by, Mapping):
        maker_kind = made_by.get("kind")
        maker_role = made_by.get("role")
        if maker_kind != "human" or maker_role not in {"repository_owner", "authorized_delegate"}:
            _issue(
                issues,
                f"{path}.made_by",
                "unauthorized_governance_decision",
                "v0 governance decisions require a human repository_owner or authorized_delegate",
            )
        elif isinstance(authority, Mapping):
            basis_kind = authority.get("kind")
            if maker_role == "repository_owner" and basis_kind != "owner":
                _issue(
                    issues,
                    f"{path}.authority_basis.kind",
                    "invalid_authority_basis",
                    "repository_owner decisions require owner authority basis",
                )
            if maker_role == "authorized_delegate" and basis_kind != "explicit_delegation":
                _issue(
                    issues,
                    f"{path}.authority_basis.kind",
                    "invalid_authority_basis",
                    "authorized_delegate decisions require explicit_delegation basis",
                )


def _validate_authority_basis(value: object, path: str, issues: list[ValidationIssue]) -> None:
    if not isinstance(value, Mapping):
        _issue(issues, path, "missing_authority_basis", "decision requires authority_basis")
        return
    _check_keys(value, AUTHORITY_BASIS_KEYS, path, issues)
    _require_keys(value, ("kind", "scope"), path, issues)
    if value.get("kind") not in {"owner", "explicit_delegation"}:
        _issue(
            issues,
            f"{path}.kind",
            "invalid_authority_basis",
            "authority basis must be owner or explicit_delegation",
        )
    _validate_string_list(value.get("scope"), f"{path}.scope", issues, "scope", minimum=1)
    if "reference" in value:
        _validate_short_text(value.get("reference"), f"{path}.reference", issues, "reference")
    if value.get("kind") == "explicit_delegation" and "reference" not in value:
        _issue(
            issues,
            f"{path}.reference",
            "missing_reference",
            "explicit_delegation requires a public delegation reference",
        )


def _validate_implementation(value: object, path: str, issues: list[ValidationIssue]) -> None:
    if not isinstance(value, Mapping):
        _issue(issues, path, "missing_implementation", "implementation_reported requires implementation")
        return
    _check_keys(value, IMPLEMENTATION_KEYS, path, issues)
    _require_keys(value, ("outcome", "scope", "limitations"), path, issues)
    if value.get("outcome") not in IMPLEMENTATION_OUTCOMES:
        _issue(
            issues,
            f"{path}.outcome",
            "invalid_implementation_outcome",
            f"implementation outcome must be one of {sorted(IMPLEMENTATION_OUTCOMES)}",
        )
    _validate_summary(value.get("scope"), f"{path}.scope", issues)
    _validate_string_list(value.get("limitations"), f"{path}.limitations", issues, "limitations")


def _validate_verification(value: object, path: str, issues: list[ValidationIssue]) -> None:
    if not isinstance(value, Mapping):
        _issue(issues, path, "missing_verification", "verification_recorded requires verification")
        return
    _check_keys(value, VERIFICATION_KEYS, path, issues)
    _require_keys(value, ("outcome", "method", "scope", "limitations"), path, issues)
    if value.get("outcome") not in VERIFICATION_OUTCOMES:
        _issue(
            issues,
            f"{path}.outcome",
            "invalid_verification_outcome",
            f"verification outcome must be one of {sorted(VERIFICATION_OUTCOMES)}",
        )
    _validate_summary(value.get("method"), f"{path}.method", issues)
    _validate_summary(value.get("scope"), f"{path}.scope", issues)
    _validate_string_list(value.get("limitations"), f"{path}.limitations", issues, "limitations")


def _validate_supersession(
    event: Mapping[str, Any], path: str, subject_ids: set[str], issues: list[ValidationIssue]
) -> None:
    previous = event.get("previous_subject_id")
    successor = event.get("successor_subject_id")
    previous_valid = _validate_reference(previous, subject_ids, f"{path}.previous_subject_id", "subject", issues)
    successor_valid = _validate_reference(successor, subject_ids, f"{path}.successor_subject_id", "subject", issues)
    if previous_valid and successor_valid and previous == successor:
        _issue(
            issues,
            path,
            "invalid_supersession",
            "a supersession needs a distinct successor subject",
        )


def _validate_actor(value: object, path: str, issues: list[ValidationIssue]) -> None:
    if not isinstance(value, Mapping):
        _issue(issues, path, "invalid_actor", "actor must be an object")
        return
    _check_keys(value, ACTOR_KEYS, path, issues)
    _require_keys(value, ("kind", "role"), path, issues)
    if value.get("kind") not in {"human", "agent", "automation"}:
        _issue(issues, f"{path}.kind", "invalid_actor", "actor kind must be human, agent, or automation")
    role = value.get("role")
    if not isinstance(role, str) or not ROLE_PATTERN.fullmatch(role):
        _issue(issues, f"{path}.role", "invalid_actor", "actor role must be a public-safe identifier")


def _validate_references(
    values: object,
    known_identifiers: set[str],
    path: str,
    label: str,
    issues: list[ValidationIssue],
) -> None:
    if not isinstance(values, list) or not values:
        _issue(issues, path, "missing_reference", f"at least one {label} reference is required")
        return
    seen: set[str] = set()
    for index, value in enumerate(values):
        item_path = f"{path}[{index}]"
        if not _validate_reference(value, known_identifiers, item_path, label, issues):
            continue
        if value in seen:
            _issue(issues, item_path, "duplicate_reference", f"duplicate {label} reference {value!r}")
        seen.add(value)


def _validate_reference(
    value: object,
    known_identifiers: set[str],
    path: str,
    label: str,
    issues: list[ValidationIssue],
) -> bool:
    if not _validate_id(value, path, issues):
        return False
    if value not in known_identifiers:
        _issue(issues, path, "unknown_reference", f"unknown {label} reference {value!r}")
        return False
    return True


def _validate_list(value: object, path: str, issues: list[ValidationIssue]) -> list[object] | None:
    if not isinstance(value, list):
        _issue(issues, path, "invalid_type", "value must be an array")
        return None
    return value


def _validate_id(value: object, path: str, issues: list[ValidationIssue]) -> bool:
    if not isinstance(value, str) or not ID_PATTERN.fullmatch(value):
        _issue(issues, path, "invalid_id", "id must be a public-safe lowercase identifier")
        return False
    return True


def _validate_summary(value: object, path: str, issues: list[ValidationIssue]) -> None:
    if not isinstance(value, str) or not value.strip() or len(value) > 2000:
        _issue(issues, path, "invalid_summary", "public_summary must be non-empty and at most 2000 characters")


def _validate_short_text(value: object, path: str, issues: list[ValidationIssue], label: str) -> None:
    if not isinstance(value, str) or not value.strip() or len(value) > 512:
        _issue(issues, path, "invalid_text", f"{label} must be non-empty and at most 512 characters")


def _validate_string_list(
    value: object,
    path: str,
    issues: list[ValidationIssue],
    label: str,
    *,
    minimum: int = 0,
) -> None:
    if not isinstance(value, list) or len(value) < minimum:
        _issue(issues, path, "invalid_list", f"{label} must be a list with at least {minimum} item(s)")
        return
    seen: set[str] = set()
    for index, item in enumerate(value):
        item_path = f"{path}[{index}]"
        if not isinstance(item, str) or not item.strip() or len(item) > 2000:
            _issue(issues, item_path, "invalid_text", f"{label} items must be public-safe text")
            continue
        if item in seen:
            _issue(issues, item_path, "duplicate_value", f"duplicate {label} value {item!r}")
        seen.add(item)


def _validate_timestamp(value: object, path: str, issues: list[ValidationIssue]) -> None:
    if not isinstance(value, str) or not value.endswith("Z"):
        _issue(issues, path, "invalid_timestamp", "timestamp must be an ISO 8601 UTC value ending in Z")
        return
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        _issue(issues, path, "invalid_timestamp", "timestamp must be an ISO 8601 UTC value")


def _check_keys(
    value: Mapping[str, Any], allowed: frozenset[str], path: str, issues: list[ValidationIssue]
) -> None:
    for key in value:
        if key not in allowed:
            _issue(issues, f"{path}.{key}", "unexpected_field", f"field {key!r} is not part of v0")


def _require_keys(
    value: Mapping[str, Any], required: Sequence[str], path: str, issues: list[ValidationIssue]
) -> None:
    for key in required:
        if key not in value:
            _issue(issues, f"{path}.{key}", "missing_field", f"missing required field {key!r}")


def _register_id(identifier: str, seen: set[str], path: str, issues: list[ValidationIssue]) -> None:
    if identifier in seen:
        _issue(issues, path, "duplicate_id", f"duplicate id {identifier!r}")
    seen.add(identifier)


def _find_forbidden_content(value: object, path: str, issues: list[ValidationIssue]) -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            nested_path = f"{path}.{key}"
            if key in FORBIDDEN_FIELD_NAMES:
                _issue(
                    issues,
                    nested_path,
                    "forbidden_field",
                    f"field {key!r} is not permitted in a public change case",
                )
            _find_forbidden_content(nested, nested_path, issues)
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _find_forbidden_content(nested, f"{path}[{index}]", issues)
    elif isinstance(value, str) and any(pattern.search(value) for pattern in PRIVATE_VALUE_PATTERNS):
        _issue(
            issues,
            path,
            "private_value",
            "value resembles private contact, credential, or absolute local-path data",
        )


def _issue(issues: list[ValidationIssue], path: str, code: str, message: str) -> None:
    issues.append(ValidationIssue(path=path, code=code, message=message))
