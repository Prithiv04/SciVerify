from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.evaluation.dataset_loader import (
    DatasetValidationError,
    default_dataset_path,
    default_fixtures_dir,
    load_dataset,
    validate_dataset_payload,
)
from app.evaluation.evaluator import evaluate_offline_dataset, load_and_evaluate_offline
from app.evaluation.io_paths import load_case_fixture
from app.evaluation.report import build_report_payload, render_markdown_report
from app.schemas.verification import Verdict


class TestDatasetLoader:
    def test_default_dataset_loads(self) -> None:
        dataset = load_dataset()
        assert len(dataset.cases) == 30
        assert dataset.cases[0].id == "cas9_supports_001"

    def test_invalid_root_rejected(self) -> None:
        with pytest.raises(DatasetValidationError, match="JSON object"):
            validate_dataset_payload([])

    def test_missing_cases_array_rejected(self) -> None:
        with pytest.raises(DatasetValidationError, match="cases"):
            validate_dataset_payload({"items": []})

    def test_empty_dataset_rejected(self) -> None:
        with pytest.raises(DatasetValidationError, match="at least one case"):
            validate_dataset_payload({"cases": []})

    def test_duplicate_case_ids_rejected(self) -> None:
        payload = {
            "cases": [
                {
                    "id": "dup",
                    "claim": "Claim one.",
                    "doi": "10.1000/example.1",
                    "expected_verdict": "SUPPORTS",
                    "description": "First.",
                },
                {
                    "id": "dup",
                    "claim": "Claim two.",
                    "doi": "10.1000/example.2",
                    "expected_verdict": "SUPPORTS",
                    "description": "Second.",
                },
            ]
        }
        with pytest.raises(DatasetValidationError, match="Duplicate benchmark case id"):
            validate_dataset_payload(payload)

    def test_invalid_expected_verdict_rejected(self) -> None:
        payload = {
            "cases": [
                {
                    "id": "bad_verdict",
                    "claim": "Claim.",
                    "doi": "10.1000/example.1",
                    "expected_verdict": "MAYBE",
                    "description": "Invalid verdict.",
                }
            ]
        }
        with pytest.raises(DatasetValidationError, match="Invalid benchmark case"):
            validate_dataset_payload(payload)

    def test_empty_id_rejected(self) -> None:
        payload = {
            "cases": [
                {
                    "id": "   ",
                    "claim": "Claim.",
                    "doi": "10.1000/example.1",
                    "expected_verdict": "SUPPORTS",
                    "description": "Empty id.",
                }
            ]
        }
        with pytest.raises(DatasetValidationError, match="Invalid benchmark case"):
            validate_dataset_payload(payload)

    def test_invalid_doi_rejected(self) -> None:
        payload = {
            "cases": [
                {
                    "id": "bad_doi",
                    "claim": "Claim.",
                    "doi": "not-a-doi",
                    "expected_verdict": "SUPPORTS",
                    "description": "Bad doi.",
                }
            ]
        }
        with pytest.raises(DatasetValidationError, match="Invalid benchmark case"):
            validate_dataset_payload(payload)

    def test_invalid_json_rejected(self, tmp_path: Path) -> None:
        bad_path = tmp_path / "bad.json"
        bad_path.write_text("{not json", encoding="utf-8")
        with pytest.raises(DatasetValidationError, match="Invalid JSON"):
            load_dataset(bad_path)


class TestOfflineEvaluation:
    def test_all_fixtures_present(self) -> None:
        dataset = load_dataset()
        fixtures_dir = default_fixtures_dir()
        for case in dataset.cases:
            response = load_case_fixture(fixtures_dir, case.id)
            assert response.verdict == case.expected_verdict

    def test_offline_evaluation_matches_expected_verdicts(self) -> None:
        result = load_and_evaluate_offline()
        assert result.aggregate.case_count == 30
        assert result.aggregate.verdict_accuracy == 1.0
        assert result.skipped_case_ids == []

    def test_missing_fixture_is_skipped(self, tmp_path: Path) -> None:
        dataset = load_dataset()
        fixtures_dir = tmp_path / "fixtures"
        fixtures_dir.mkdir()
        first = load_case_fixture(default_fixtures_dir(), dataset.cases[0].id)
        (fixtures_dir / f"{dataset.cases[0].id}.json").write_text(
            json.dumps(first.model_dump(mode="json")),
            encoding="utf-8",
        )
        result = evaluate_offline_dataset(dataset, fixtures_dir=fixtures_dir)
        assert len(result.cases) == 1
        assert len(result.skipped_case_ids) == 29

    def test_report_generation(self) -> None:
        result = load_and_evaluate_offline()
        payload = build_report_payload(result)
        markdown = render_markdown_report(result)

        assert payload["cases_evaluated"] == 30
        assert payload["verdict_accuracy"] == 1.0
        assert "SciVerify Evaluation" in markdown
        assert "Verdict Accuracy" in markdown
        assert payload["confidence"]["note"].startswith("Confidence error")

    def test_expected_verdict_enum_values(self) -> None:
        dataset = load_dataset()
        allowed = {verdict.value for verdict in Verdict}
        assert all(case.expected_verdict.value in allowed for case in dataset.cases)
        assert default_dataset_path().exists()
