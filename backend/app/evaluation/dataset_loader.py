from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, ValidationError, field_validator

from app.schemas.verification import Verdict
from app.utils.doi import InvalidDOIError, normalize_doi

VALID_VERDICTS = {verdict.value for verdict in Verdict}


class BenchmarkCase(BaseModel):
    id: str
    claim: str
    doi: str
    expected_verdict: Verdict
    description: str
    expected_traceability_statuses: list[str] | None = None
    expected_min_evidence_count: int | None = None

    @field_validator("id", "claim", "description")
    @classmethod
    def require_non_empty_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Field must not be empty.")
        return value.strip()

    @field_validator("doi")
    @classmethod
    def validate_doi(cls, value: str) -> str:
        try:
            return normalize_doi(value)
        except InvalidDOIError as exc:
            raise ValueError(str(exc)) from exc


class BenchmarkDataset(BaseModel):
    cases: list[BenchmarkCase] = Field(default_factory=list)


class DatasetValidationError(ValueError):
    """Raised when a benchmark dataset fails validation."""


def default_dataset_path() -> Path:
    return Path(__file__).resolve().parents[2] / "evaluation" / "dataset.json"


def default_fixtures_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "evaluation" / "fixtures"


def load_dataset(path: Path | None = None) -> BenchmarkDataset:
    dataset_path = path or default_dataset_path()
    if not dataset_path.exists():
        raise DatasetValidationError(f"Dataset not found: {dataset_path}")

    try:
        payload = json.loads(dataset_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DatasetValidationError(f"Invalid JSON in dataset: {dataset_path}") from exc

    return validate_dataset_payload(payload)


def validate_dataset_payload(payload: Any) -> BenchmarkDataset:
    if not isinstance(payload, dict):
        raise DatasetValidationError("Dataset root must be a JSON object.")

    raw_cases = payload.get("cases")
    if not isinstance(raw_cases, list):
        raise DatasetValidationError("Dataset must contain a 'cases' array.")

    cases: list[BenchmarkCase] = []
    seen_ids: set[str] = set()

    for index, raw_case in enumerate(raw_cases):
        try:
            case = BenchmarkCase.model_validate(raw_case)
        except ValidationError as exc:
            raise DatasetValidationError(
                f"Invalid benchmark case at index {index}: {exc}"
            ) from exc

        if case.id in seen_ids:
            raise DatasetValidationError(f"Duplicate benchmark case id: {case.id}")
        seen_ids.add(case.id)
        cases.append(case)

    if not cases:
        raise DatasetValidationError("Dataset must contain at least one case.")

    return BenchmarkDataset(cases=cases)
