from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.evaluation.dataset_loader import BenchmarkCase
from app.evaluation.evaluator import EvaluationResult, LiveCaseResult
from app.evaluation.live_diagnostics import (
    classify_exception,
    evaluate_live_case,
    MAX_RETRIES,
)
from app.schemas.verification import LiveFailureCategory, Verdict
from app.services.paper_retriever import PaperNotFoundError


class TestEvaluateLiveCase:
    def test_successful_evaluation(self) -> None:
        """Test that a successful evaluation returns correct status and metrics."""
        case = BenchmarkCase(
            id="test-001",
            claim="Test claim",
            doi="10.1000/test.2024.001",
            expected_verdict=Verdict.SUPPORTS,
            description="Test case",
            live_evaluable=True,
        )

        mock_response = MagicMock()
        mock_response.status = "success"
        mock_response.verdict = Verdict.SUPPORTS
        mock_response.confidence = 0.95
        mock_response.evidence = []
        mock_response.paper = MagicMock()
        mock_response.paper.paper_id = "test-doi"
        mock_response.claim_traceability = MagicMock()
        mock_response.claim_traceability.segments = []
        mock_response.claim_traceability.overall_coverage = 0.0
        mock_response.validation_warnings = None
        mock_response.agent_agreement = True

        with patch("app.evaluation.live_diagnostics.analyze_verification", return_value=mock_response):
            live_result, response = evaluate_live_case(case, max_retries=MAX_RETRIES)

        assert live_result.status == "evaluated"
        assert live_result.case_id == "test-001"
        assert live_result.expected_verdict == Verdict.SUPPORTS
        assert live_result.actual_verdict == Verdict.SUPPORTS
        assert live_result.confidence == 0.95
        assert live_result.failure_category is None
        assert live_result.failure_reason is None
        assert live_result.retrieval_attempts == 1
        assert live_result.elapsed_seconds >= 0
        assert response is not None

    def test_retrieval_failure_classification(self) -> None:
        """Test that retrieval failures are correctly classified and tracked."""
        case = BenchmarkCase(
            id="test-002",
            claim="Test claim",
            doi="10.1000/nonexistent.2024.001",
            expected_verdict=Verdict.SUPPORTS,
            description="Test case with bad DOI",
            live_evaluable=True,
        )

        with patch("app.evaluation.live_diagnostics.analyze_verification", side_effect=PaperNotFoundError("Paper not found")):
            live_result, response = evaluate_live_case(case, max_retries=MAX_RETRIES)

        assert live_result.status == "failed"
        assert live_result.case_id == "test-002"
        assert live_result.failure_category == LiveFailureCategory.DOI_NOT_FOUND
        assert live_result.failure_reason == "Paper not found"
        assert live_result.retrieval_attempts == MAX_RETRIES + 1
        assert response is None

    def test_llm_failure_classification(self) -> None:
        """Test that LLM failures are correctly classified."""
        from app.services.llm.provider import LLMProviderError

        case = BenchmarkCase(
            id="test-003",
            claim="Test claim",
            doi="10.1000/test.2024.002",
            expected_verdict=Verdict.SUPPORTS,
            description="Test case",
            live_evaluable=True,
        )

        with patch("app.evaluation.live_diagnostics.analyze_verification", side_effect=LLMProviderError("LLM provider error")):
            live_result, response = evaluate_live_case(case, max_retries=MAX_RETRIES)

        assert live_result.status == "failed"
        assert live_result.failure_category == LiveFailureCategory.LLM_FAILURE
        assert live_result.failure_reason == "LLM provider error"
        assert response is None

    def test_infrastructure_vs_verification_failure_separation(self) -> None:
        """Test that infrastructure failures are separated from verification failures."""
        # Infrastructure failure (DOI not found)
        case1 = BenchmarkCase(
            id="test-004",
            claim="Test claim",
            doi="10.1000/nonexistent.2024.001",
            expected_verdict=Verdict.SUPPORTS,
            description="Infrastructure failure case",
            live_evaluable=True,
        )

        with patch("app.evaluation.live_diagnostics.analyze_verification", side_effect=PaperNotFoundError("Paper not found")):
            live_result1, _ = evaluate_live_case(case1, max_retries=MAX_RETRIES)

        # This should be classified as an infrastructure failure (DOI_NOT_FOUND)
        assert live_result1.failure_category == LiveFailureCategory.DOI_NOT_FOUND
        assert live_result1.failure_category != LiveFailureCategory.LLM_FAILURE

    def test_retry_logic_with_retryable_error(self) -> None:
        """Test that retryable errors trigger retries."""
        from app.services.paper_retriever import PaperProviderError

        case = BenchmarkCase(
            id="test-005",
            claim="Test claim",
            doi="10.1000/test.2024.003",
            expected_verdict=Verdict.SUPPORTS,
            description="Test case",
            live_evaluable=True,
        )

        # First two attempts fail, third succeeds
        mock_response = MagicMock()
        mock_response.status = "success"
        mock_response.verdict = Verdict.SUPPORTS
        mock_response.confidence = 0.95
        mock_response.evidence = []
        mock_response.paper = MagicMock()
        mock_response.paper.paper_id = "test-doi"
        mock_response.claim_traceability = MagicMock()
        mock_response.claim_traceability.segments = []
        mock_response.claim_traceability.overall_coverage = 0.0
        mock_response.validation_warnings = None
        mock_response.agent_agreement = True

        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise PaperProviderError("Rate limit exceeded")
            return mock_response

        with patch("app.evaluation.live_diagnostics.analyze_verification", side_effect=side_effect):
            live_result, response = evaluate_live_case(case, max_retries=MAX_RETRIES)

        # Should have retried and succeeded
        assert live_result.status == "evaluated"
        assert live_result.retrieval_attempts == 2
        assert response is not None

    def test_retry_logic_with_non_retryable_error(self) -> None:
        """Test that non-retryable errors do not trigger retries."""
        case = BenchmarkCase(
            id="test-006",
            claim="Test claim",
            doi="10.1000/nonexistent.2024.001",
            expected_verdict=Verdict.SUPPORTS,
            description="Test case",
            live_evaluable=True,
        )

        with patch("app.evaluation.live_diagnostics.analyze_verification", side_effect=PaperNotFoundError("Paper not found")):
            live_result, response = evaluate_live_case(case, max_retries=MAX_RETRIES)

        # DOI_NOT_FOUND is non-retryable, should fail immediately
        assert live_result.status == "failed"
        assert live_result.retrieval_attempts == MAX_RETRIES + 1
        assert response is None


class TestLiveCaseResult:
    def test_live_case_result_structure(self) -> None:
        """Test that LiveCaseResult has all required fields."""
        result = LiveCaseResult(
            case_id="test-001",
            status="evaluated",
            expected_verdict=Verdict.SUPPORTS,
            actual_verdict=Verdict.SUPPORTS,
            confidence=0.95,
            failure_category=None,
            failure_reason=None,
            retrieval_attempts=1,
            elapsed_seconds=1.5,
        )

        assert result.case_id == "test-001"
        assert result.status == "evaluated"
        assert result.expected_verdict == Verdict.SUPPORTS
        assert result.actual_verdict == Verdict.SUPPORTS
        assert result.confidence == 0.95
        assert result.failure_category is None
        assert result.failure_reason is None
        assert result.retrieval_attempts == 1
        assert result.elapsed_seconds == 1.5

    def test_live_case_result_with_failure(self) -> None:
        """Test LiveCaseResult with failure information."""
        result = LiveCaseResult(
            case_id="test-002",
            status="failed",
            expected_verdict=Verdict.SUPPORTS,
            actual_verdict=None,
            confidence=None,
            failure_category=LiveFailureCategory.DOI_NOT_FOUND,
            failure_reason="Paper not found",
            retrieval_attempts=4,
            elapsed_seconds=2.5,
        )

        assert result.status == "failed"
        assert result.failure_category == LiveFailureCategory.DOI_NOT_FOUND
        assert result.failure_reason == "Paper not found"
        assert result.retrieval_attempts == 4


class TestEvaluationResultWithLiveResults:
    def test_evaluation_result_with_live_case_results(self) -> None:
        """Test that EvaluationResult can contain live case results."""
        live_results = [
            LiveCaseResult(
                case_id="test-001",
                status="evaluated",
                expected_verdict=Verdict.SUPPORTS,
                actual_verdict=Verdict.SUPPORTS,
                confidence=0.95,
                failure_category=None,
                failure_reason=None,
                retrieval_attempts=1,
                elapsed_seconds=1.5,
            ),
            LiveCaseResult(
                case_id="test-002",
                status="failed",
                expected_verdict=Verdict.SUPPORTS,
                actual_verdict=None,
                confidence=None,
                failure_category=LiveFailureCategory.DOI_NOT_FOUND,
                failure_reason="Paper not found",
                retrieval_attempts=4,
                elapsed_seconds=2.5,
            ),
        ]

        result = EvaluationResult(
            dataset_path=MagicMock(),
            cases=[],
            aggregate=MagicMock(),
            skipped_case_ids=["test-002"],
            responses_by_id={},
            live_case_results=live_results,
        )

        assert len(result.live_case_results) == 2
        assert result.live_case_results[0].case_id == "test-001"
        assert result.live_case_results[1].case_id == "test-002"

    def test_evaluation_result_without_live_case_results(self) -> None:
        """Test that EvaluationResult works without live case results (offline evaluation)."""
        result = EvaluationResult(
            dataset_path=MagicMock(),
            cases=[],
            aggregate=MagicMock(),
            skipped_case_ids=[],
            responses_by_id={},
        )

        assert result.live_case_results == []
