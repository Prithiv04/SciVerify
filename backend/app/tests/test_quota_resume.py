import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.evaluation.run import _run_live_evaluation
from app.evaluation.checkpoint import load_checkpoint
from app.schemas.verification import LiveFailureCategory, Verdict
from app.evaluation.dataset_loader import BenchmarkCase

# Helper to create a dummy BenchmarkCase
def make_case(case_id: str) -> BenchmarkCase:
    return BenchmarkCase(
        id=case_id,
        claim="Test claim",
        doi=f"10.1000/dummy.{case_id}",
        expected_verdict=Verdict.SUPPORTS,
        description="Generated for quota test",
        live_evaluable=True,
    )

# Mock LiveCaseResult similar to what evaluate_live_case returns
class DummyLiveResult:
    def __init__(self, case_id, status, failure_category=None, failure_reason=None):
        self.case_id = case_id
        self.status = status  # "evaluated", "failed", or "skipped"
        self.expected_verdict = Verdict.SUPPORTS
        self.actual_verdict = Verdict.SUPPORTS if status == "evaluated" else None
        self.confidence = 0.9 if status == "evaluated" else None
        self.failure_category = failure_category
        self.failure_reason = failure_reason
        self.retrieval_attempts = 1
        self.elapsed_seconds = 0.1

# ---------------------------------------------------------------------------
# Test 1 – quota error is detected and classified correctly
# ---------------------------------------------------------------------------
def test_quota_error_is_detected_and_classified(tmp_path: Path):
    # Prepare three cases – the third will trigger quota exhausted
    cases = [make_case(f"case_{i}") for i in range(1, 4)]

    # Side‑effect sequence for evaluate_live_case:
    #   1. Successful evaluation
    #   2. Successful evaluation
    #   3. Quota exhausted failure
    side_effects = [
        (DummyLiveResult(cases[0].id, "evaluated"), MagicMock()),
        (DummyLiveResult(cases[1].id, "evaluated"), MagicMock()),
        (
            DummyLiveResult(
                cases[2].id,
                "failed",
                failure_category=LiveFailureCategory.LLM_QUOTA_EXCEEDED,
                failure_reason="LLM quota exhausted",
            ),
            None,
        ),
    ]

    checkpoint_dir = tmp_path / "checkpoints"
    checkpoint_dir.mkdir()

    dummy_dataset = type("DummyDataset", (), {"cases": cases})
    with patch("app.evaluation.run.load_dataset", return_value=dummy_dataset), \
         patch("app.evaluation.live_diagnostics.evaluate_live_case", side_effect=side_effects):
        # Run live evaluation – it should abort with exit code 1
        exit_code = _run_live_evaluation(
            dataset_path=Path("/dev/null"),  # dummy, not used because we patch evaluate_live_case
            skip_unhealthy=False,
            checkpoint_dir=checkpoint_dir,
            resume=False,
            quota_pause_seconds=0,
        )

    assert exit_code == 1, "Runner should abort when quota is exceeded"

    # Verify checkpoint contents
    checkpoint_path = checkpoint_dir / "live_checkpoint.json"
    assert checkpoint_path.exists(), "Checkpoint file should be written"
    data = load_checkpoint(checkpoint_path)

    # Completed cases should contain the first two IDs only
    assert set(data["completed_case_ids"]) == {cases[0].id, cases[1].id}
    # Failed cases should contain the quota‑failed case with correct category
    assert cases[2].id in data["failed_cases"]
    assert data["failed_cases"][cases[2].id]["category"] == LiveFailureCategory.LLM_QUOTA_EXCEEDED.value

# ---------------------------------------------------------------------------
# Test 2 – resume skips already completed cases and processes remaining ones
# ---------------------------------------------------------------------------
def test_resume_behaviour_skips_completed_cases(tmp_path: Path):
    # Create five cases – first two succeed, third hits quota, fourth & fifth are fresh
    cases = [make_case(f"case_{i}") for i in range(1, 6)]

    # First run side‑effects (same as previous test, but we also provide a fourth case result)
    first_run_side_effects = [
        (DummyLiveResult(cases[0].id, "evaluated"), MagicMock()),
        (DummyLiveResult(cases[1].id, "evaluated"), MagicMock()),
        (
            DummyLiveResult(
                cases[2].id,
                "failed",
                failure_category=LiveFailureCategory.LLM_QUOTA_EXCEEDED,
                failure_reason="LLM quota exhausted",
            ),
            None,
        ),
    ]

    checkpoint_dir = tmp_path / "checkpoints"
    checkpoint_dir.mkdir()

    # ---------- First run – abort on quota ----------
    dummy_dataset = type("DummyDataset", (), {"cases": cases})
    with patch("app.evaluation.run.load_dataset", return_value=dummy_dataset), \
         patch("app.evaluation.live_diagnostics.evaluate_live_case", side_effect=first_run_side_effects):
        exit_code = _run_live_evaluation(
            dataset_path=Path("/dev/null"),
            skip_unhealthy=False,
            checkpoint_dir=checkpoint_dir,
            resume=False,
            quota_pause_seconds=0,
        )
    assert exit_code == 1

    # ---------- Second run – resume and finish remaining cases ----------
    # After resume, the first three cases should be skipped. We provide results for case 4 & 5.
    second_run_side_effects = [
        (DummyLiveResult(cases[3].id, "evaluated"), MagicMock()),
        (DummyLiveResult(cases[4].id, "evaluated"), MagicMock()),
    ]

    with patch("app.evaluation.run.load_dataset", return_value=dummy_dataset), \
         patch("app.evaluation.live_diagnostics.evaluate_live_case", side_effect=second_run_side_effects):
        exit_code = _run_live_evaluation(
            dataset_path=Path("/dev/null"),
            skip_unhealthy=False,
            checkpoint_dir=checkpoint_dir,
            resume=True,
            quota_pause_seconds=0,
        )
    # No quota error on resume, so the runner should finish successfully (exit code 0)
    assert exit_code == 0

    # Verify final checkpoint reflects all processed cases
    final_data = load_checkpoint(checkpoint_dir / "live_checkpoint.json")
    expected_completed = {c.id for c in cases[:2]} | {c.id for c in cases[3:5]}
    assert set(final_data["completed_case_ids"]) == expected_completed
    # The quota‑failed case remains recorded under failed_cases
    assert cases[2].id in final_data["failed_cases"]
    assert final_data["failed_cases"][cases[2].id]["category"] == LiveFailureCategory.LLM_QUOTA_EXCEEDED.value
