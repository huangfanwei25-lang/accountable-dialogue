"""Local-only execution support for the bounded synthetic small-model pilot.

The runner accepts only a loopback Ollama endpoint and models that endpoint
already reports as installed. Raw responses are intentionally written outside
the repository so public curation remains a separate human decision.
"""

from __future__ import annotations

import hashlib
import json
import random
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from accountable_dialogue.synthetic_pilot import (
    RESPONSE_FIELDS,
    annotation_key_digest,
    load_annotation_key,
    render_condition,
    validate_annotation_key,
    validate_case,
)


class OllamaTransport(Protocol):
    """Small transport seam so unit tests never need a live model server."""

    def request(
        self,
        method: str,
        url: str,
        payload: dict[str, object] | None,
        timeout_seconds: float,
    ) -> dict[str, object]: ...


class UrllibOllamaTransport:
    """A standard-library JSON client with no credentials or remote fallback."""

    def request(
        self,
        method: str,
        url: str,
        payload: dict[str, object] | None,
        timeout_seconds: float,
    ) -> dict[str, object]:
        body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = Request(
            url,
            data=body,
            method=method,
            headers={"Content-Type": "application/json"} if body is not None else {},
        )
        try:
            with urlopen(request, timeout=timeout_seconds) as response:
                decoded = response.read().decode("utf-8")
        except URLError as error:
            raise ConnectionError("local Ollama request failed") from error
        try:
            value = json.loads(decoded)
        except json.JSONDecodeError as error:
            raise ValueError("local Ollama response was not JSON") from error
        if not isinstance(value, dict):
            raise ValueError("local Ollama response must be an object")
        return value


@dataclass(frozen=True)
class PilotExecutionConfig:
    """The small, fixed surface declared by the pilot plan."""

    models: tuple[str, ...]
    seed: int = 20260716
    temperature: int = 0
    context_tokens: int = 4096
    max_tokens: int = 360
    timeout_seconds: float = 120.0

    def __post_init__(self) -> None:
        if not self.models or any(not model.strip() for model in self.models):
            raise ValueError("at least one non-empty installed model name is required")
        if self.temperature != 0:
            raise ValueError("pilot v0 fixes temperature at 0")
        if self.context_tokens < 512 or self.max_tokens < 1 or self.timeout_seconds <= 0:
            raise ValueError("pilot execution limits must be positive and bounded")


@dataclass(frozen=True)
class PilotExecutionResult:
    """References to local-only output and its public-safe mechanical status."""

    output_dir: Path
    rows: tuple[dict[str, object], ...]
    manifest: dict[str, object]


class LocalOnlyOllamaClient:
    """Reject remote endpoints and implicit downloads before every generation."""

    def __init__(self, base_url: str, *, transport: OllamaTransport | None = None) -> None:
        self.base_url = validate_loopback_base_url(base_url)
        self.transport: OllamaTransport = transport or UrllibOllamaTransport()

    def available_models(self) -> tuple[str, ...]:
        models = self._model_catalog()
        return tuple(models)

    def require_models(self, models: Sequence[str]) -> dict[str, str]:
        catalog = self._model_catalog()
        missing = [model for model in models if model not in catalog]
        if missing:
            rendered = ", ".join(sorted(missing))
            raise ValueError(f"requested model is not installed locally: {rendered}")
        return {model: catalog[model] for model in models}

    def generate(self, model: str, prompt: str, config: PilotExecutionConfig) -> str:
        self.require_models((model,))
        response = self.transport.request(
            "POST",
            f"{self.base_url}/api/generate",
            {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": config.temperature,
                    "seed": config.seed,
                    "num_ctx": config.context_tokens,
                    "num_predict": config.max_tokens,
                },
            },
            config.timeout_seconds,
        )
        output = response.get("response")
        if not isinstance(output, str):
            raise ValueError("local Ollama generation did not include a string response")
        return output

    def _model_catalog(self) -> dict[str, str]:
        response = self.transport.request("GET", f"{self.base_url}/api/tags", None, 10.0)
        values = response.get("models")
        if not isinstance(values, list):
            raise ValueError("local Ollama model listing is invalid")
        catalog: dict[str, str] = {}
        for item in values:
            if not isinstance(item, Mapping):
                continue
            name = item.get("name")
            if not isinstance(name, str) or not name:
                continue
            digest = item.get("digest")
            catalog[name] = digest if isinstance(digest, str) and digest else "unknown"
        return dict(sorted(catalog.items()))


def validate_loopback_base_url(value: str) -> str:
    """Allow only plain HTTP to a local server root, never a proxy or remote host."""

    parsed = urlparse(value)
    if (
        parsed.scheme != "http"
        or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or parsed.path not in {"", "/"}
    ):
        raise ValueError("pilot provider must be a loopback HTTP base URL")
    host = parsed.hostname
    if host is None:
        raise ValueError("pilot provider must be a loopback HTTP base URL")
    rendered_host = f"[{host}]" if host == "::1" else host
    port = f":{parsed.port}" if parsed.port is not None else ""
    return f"http://{rendered_host}{port}"


def execute_pilot(
    *,
    cases: Sequence[Mapping[str, Any]],
    client: LocalOnlyOllamaClient,
    config: PilotExecutionConfig,
    output_dir: Path,
    repository_root: Path,
) -> PilotExecutionResult:
    """Run the fixed B0/I1 matrix into a directory outside the repository.

    The result deliberately contains only mechanical parse/reference outcomes.
    It does not compute semantic labels or a total score.
    """

    normalized_cases = tuple(cases)
    if not normalized_cases:
        raise ValueError("at least one synthetic case is required")
    _ensure_output_is_outside_repository(output_dir, repository_root)
    _validate_cases_and_annotation_commitments(normalized_cases, repository_root)
    resolved_models = client.require_models(config.models)
    if output_dir.exists():
        raise FileExistsError(f"pilot output directory already exists: {output_dir}")
    output_dir.mkdir(parents=True)

    rng = random.Random(config.seed)
    mappings = _build_condition_mappings(normalized_cases, rng)
    plan: list[tuple[Mapping[str, Any], str, str, str]] = []
    for case in normalized_cases:
        mapping = mappings[case["case_id"]]
        for model in config.models:
            for alias in ("A", "B"):
                plan.append((case, model, alias, mapping[alias]))
    rng.shuffle(plan)

    rows: list[dict[str, object]] = []
    for case, model, alias, condition in plan:
        rendered = render_condition(case, condition)
        started = time.perf_counter()
        raw_response: str | None = None
        try:
            raw_response = client.generate(model, rendered.prompt, config)
            mechanical_status = _mechanical_response_status(raw_response, rendered.material_ids, case)
        except TimeoutError:
            mechanical_status = "timeout"
        except (ConnectionError, ValueError):
            mechanical_status = "transport_error"
        latency_ms = round((time.perf_counter() - started) * 1000, 3)
        rows.append(
            {
                "case_id": case["case_id"],
                "model": model,
                "condition_alias": alias,
                "mechanical_status": mechanical_status,
                "latency_ms": latency_ms,
                "raw_response": raw_response,
            }
        )

    mapping_payload = {
        "format": "accountable-dialogue/synthetic-pilot-condition-mapping-v0",
        "mapping": mappings,
    }
    mapping_bytes = json.dumps(mapping_payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    mapping_digest = hashlib.sha256(mapping_bytes).hexdigest()
    manifest = {
        "format": "accountable-dialogue/synthetic-pilot-run-manifest-v0",
        "created_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "models": [{"name": name, "resolved_id": resolved_models[name]} for name in config.models],
        "settings": {
            "seed": config.seed,
            "temperature": config.temperature,
            "num_ctx": config.context_tokens,
            "num_predict": config.max_tokens,
            "timeout_seconds": config.timeout_seconds,
        },
        "case_digests": {case["case_id"]: _canonical_digest(case) for case in normalized_cases},
        "condition_mapping_sha256": mapping_digest,
        "response_count": len(rows),
        "raw_outputs_publication": "not_reviewed",
    }
    _write_json_lines(output_dir / "blind-responses.jsonl", rows)
    _write_json(output_dir / "condition-mapping.json", mapping_payload)
    _write_json(output_dir / "run-manifest.json", manifest)
    return PilotExecutionResult(output_dir=output_dir, rows=tuple(rows), manifest=manifest)


def _validate_cases_and_annotation_commitments(
    cases: Sequence[Mapping[str, Any]], repository_root: Path
) -> None:
    known_case_ids: set[str] = set()
    annotation_key_path: Path | None = None
    annotation_key_digest_value: str | None = None
    for case in cases:
        issues = validate_case(case)
        if issues:
            rendered = "; ".join(f"{issue.path}: {issue.message}" for issue in issues)
            raise ValueError(f"invalid synthetic case: {rendered}")
        case_id = case["case_id"]
        if case_id in known_case_ids:
            raise ValueError(f"duplicate case id in run: {case_id}")
        known_case_ids.add(case_id)
        reference = case["annotation_key"]
        candidate_path = (repository_root / reference["locator"]).resolve()
        _ensure_path_inside_repository(candidate_path, repository_root)
        candidate_digest = annotation_key_digest(candidate_path)
        if candidate_digest != reference["sha256"]:
            raise ValueError("annotation-key digest does not match the fixture commitment")
        if annotation_key_path is None:
            annotation_key_path = candidate_path
            annotation_key_digest_value = candidate_digest
        elif candidate_path != annotation_key_path or candidate_digest != annotation_key_digest_value:
            raise ValueError("all cases in a pilot run must commit to the same annotation key")

    if annotation_key_path is None:
        raise ValueError("pilot run needs an annotation key")
    key = load_annotation_key(annotation_key_path)
    issues = validate_annotation_key(key)
    if issues:
        rendered = "; ".join(f"{issue.path}: {issue.message}" for issue in issues)
        raise ValueError(f"invalid annotation key: {rendered}")
    label_case_ids = {item["case_id"] for item in key["case_expectations"]}
    missing = known_case_ids - label_case_ids
    if missing:
        raise ValueError(f"annotation key has no expectation for: {', '.join(sorted(missing))}")


def _build_condition_mappings(
    cases: Sequence[Mapping[str, Any]], rng: random.Random
) -> dict[str, dict[str, str]]:
    mappings: dict[str, dict[str, str]] = {}
    for case in cases:
        if rng.randrange(2) == 0:
            mappings[case["case_id"]] = {"A": "B0_baseline", "B": "I1_structured_context"}
        else:
            mappings[case["case_id"]] = {"A": "I1_structured_context", "B": "B0_baseline"}
    return mappings


def _mechanical_response_status(raw_response: str, material_ids: Sequence[str], case: Mapping[str, Any]) -> str:
    try:
        response = json.loads(raw_response)
    except json.JSONDecodeError:
        return "invalid_json"
    if not isinstance(response, Mapping):
        return "invalid_response_object"
    if set(response) != set(RESPONSE_FIELDS):
        return "invalid_response_contract"
    for field in RESPONSE_FIELDS:
        if field == "evidence_refs":
            continue
        if not isinstance(response.get(field), str) or not response[field].strip():
            return "invalid_response_contract"
    evidence_refs = response.get("evidence_refs")
    if not isinstance(evidence_refs, list) or any(not isinstance(item, str) for item in evidence_refs):
        return "invalid_evidence_refs"
    material_kinds = {item["id"]: item["kind"] for item in case["materials"]}
    permitted_evidence_ids = {
        material_id
        for material_id in material_ids
        if material_kinds[material_id] in {"source_excerpt", "test_result", "policy", "role_statement", "audit_record"}
    }
    if any(reference not in permitted_evidence_ids for reference in evidence_refs):
        return "invalid_evidence_ref"
    return "valid"


def _ensure_output_is_outside_repository(output_dir: Path, repository_root: Path) -> None:
    resolved_output = output_dir.resolve()
    _ensure_path_outside_repository(resolved_output, repository_root)


def _ensure_path_outside_repository(path: Path, repository_root: Path) -> None:
    try:
        path.relative_to(repository_root.resolve())
    except ValueError:
        return
    raise ValueError("pilot raw output directory must stay outside the repository")


def _ensure_path_inside_repository(path: Path, repository_root: Path) -> None:
    try:
        path.relative_to(repository_root.resolve())
    except ValueError as error:
        raise ValueError("annotation-key locator escapes the repository") from error


def _canonical_digest(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _write_json_lines(path: Path, rows: Sequence[Mapping[str, object]]) -> None:
    content = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows)
    path.write_text(content, encoding="utf-8")


def _write_json(path: Path, value: Mapping[str, object]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
