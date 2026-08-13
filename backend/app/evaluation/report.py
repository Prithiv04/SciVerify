from __future__ import annotations

from pathlib import Path
from typing import Any

from app.evaluation.evaluator import EvaluationResult
from app.evaluation.metrics import AggregateMetrics, CaseMetrics
from app.evaluation.regression import RegressionComparison, aggregate_to_baseline_payload


def build_report_payload(
    result: EvaluationResult,
    *,
    regression: RegressionComparison | None = None,
) -> dict[str, Any]:
    aggregate = result.aggregate
    return {
        "dataset_path": str(result.dataset_path) if result.dataset_path else None,
        "cases_evaluated": aggregate.case_count,
        "skipped_case_ids": result.skipped_case_ids,
        "verdict_accuracy": aggregate.verdict_accuracy,
        "confusion_matrix": aggregate.confusion_matrix,
        "incorrect_case_ids": aggregate.incorrect_case_ids,
        "evidence": {
            "average_count": aggregate.average_evidence_count,
            "average_relevance": aggregate.average_relevance,
            "average_claim_overlap": aggregate.average_claim_overlap,
            "average_duplicate_rate": aggregate.average_duplicate_rate,
        },
        "traceability": {
            "completeness": aggregate.traceability_completeness,
            "average_overall_coverage": aggregate.average_overall_coverage,
            "supported_segment_rate": aggregate.segment_percentage("SUPPORTED"),
            "partial_segment_rate": aggregate.segment_percentage("PARTIALLY_SUPPORTED"),
            "unsupported_segment_rate": aggregate.segment_percentage("UNSUPPORTED"),
            "contradicted_segment_rate": aggregate.segment_percentage("CONTRADICTED"),
        },
        "validation": {
            "override_rate": aggregate.validation_override_rate,
            "warning_rate": aggregate.validation_warning_rate,
        },
        "agent_agreement": {
            "agreement_rate": aggregate.agent_agreement_rate,
            "true_count": aggregate.agent_agreement_true_count,
            "false_count": aggregate.agent_agreement_false_count,
            "missing_count": aggregate.agent_agreement_missing_count,
        },
        "confidence": {
            "average": aggregate.average_confidence,
            "correct_average": aggregate.average_correct_confidence,
            "incorrect_average": aggregate.average_incorrect_confidence,
            "minimum": aggregate.minimum_confidence,
            "maximum": aggregate.maximum_confidence,
            "average_error": aggregate.average_confidence_error,
            "note": "Confidence error is a simple diagnostic, not formal calibration.",
        },
        "regression": {
            "passed": regression.passed if regression else None,
            "findings": [
                {
                    "metric": finding.metric,
                    "baseline": finding.baseline,
                    "current": finding.current,
                    "tolerance": finding.tolerance,
                    "message": finding.message,
                }
                for finding in (regression.findings if regression else [])
            ],
        },
        "cases": [_case_payload(case) for case in result.cases],
    }


def render_markdown_report(
    result: EvaluationResult,
    *,
    regression: RegressionComparison | None = None,
) -> str:
    aggregate = result.aggregate
    lines = [
        "SciVerify Evaluation",
        "====================",
        "",
        f"Cases: {aggregate.case_count}",
        f"Verdict Accuracy: {aggregate.verdict_accuracy:.1%}",
        "",
        "Evidence:",
        f"- Average evidence count: {aggregate.average_evidence_count:.1f}",
        f"- Average relevance: {aggregate.average_relevance:.2f}",
        f"- Average claim overlap: {aggregate.average_claim_overlap:.2f}",
        f"- Duplicate rate: {aggregate.average_duplicate_rate:.1%}",
        "",
        "Traceability:",
        f"- Completeness: {aggregate.traceability_completeness:.1%}",
        f"- Coverage: {aggregate.average_overall_coverage:.1%}",
        f"- Supported segments: {aggregate.segment_percentage('SUPPORTED'):.1%}",
        f"- Partial segments: {aggregate.segment_percentage('PARTIALLY_SUPPORTED'):.1%}",
        f"- Unsupported segments: {aggregate.segment_percentage('UNSUPPORTED'):.1%}",
        f"- Contradicted segments: {aggregate.segment_percentage('CONTRADICTED'):.1%}",
        "",
        "Validation:",
        f"- Override rate: {aggregate.validation_override_rate:.1%}",
        f"- Warning rate: {aggregate.validation_warning_rate:.1%}",
        "",
        "Agent Agreement:",
    ]

    agreement_rate = aggregate.agent_agreement_rate
    lines.append(
        f"- Agreement: {agreement_rate:.1%}" if agreement_rate is not None else "- Agreement: n/a"
    )

    lines.extend(
        [
            "",
            "Confidence:",
            f"- Correct verdict avg: {_fmt(aggregate.average_correct_confidence)}",
            f"- Incorrect verdict avg: {_fmt(aggregate.average_incorrect_confidence)}",
            f"- Average confidence error: {_fmt(aggregate.average_confidence_error)}",
            "",
            "Regression:",
            "PASS" if regression is None or regression.passed else "FAIL",
            "",
        ]
    )

    if regression and regression.findings:
        lines.append("Regression findings:")
        for finding in regression.findings:
            lines.append(
                f"- {finding.message}: baseline={finding.baseline:.3f}, "
                f"current={finding.current:.3f}, tolerance={finding.tolerance:.3f}"
            )
        lines.append("")

    if aggregate.incorrect_case_ids:
        lines.append("Incorrect verdict cases:")
        for case_id in aggregate.incorrect_case_ids:
            lines.append(f"- {case_id}")
        lines.append("")

    if result.skipped_case_ids:
        lines.append("Skipped cases (missing fixtures/responses):")
        for case_id in result.skipped_case_ids:
            lines.append(f"- {case_id}")
        lines.append("")

    lines.append("Confusion matrix:")
    for expected, actuals in aggregate.confusion_matrix.items():
        for actual, count in actuals.items():
            lines.append(f"- {expected} -> {actual}: {count}")

    return "\n".join(lines)


def write_reports(
    result: EvaluationResult,
    *,
    output_dir: Path,
    regression: RegressionComparison | None = None,
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = build_report_payload(result, regression=regression)
    json_path = output_dir / "latest.json"
    md_path = output_dir / "latest.md"
    json_path.write_text(
        __import__("json").dumps(payload, indent=2),
        encoding="utf-8",
    )
    md_path.write_text(render_markdown_report(result, regression=regression), encoding="utf-8")
    return json_path, md_path


def _case_payload(case: CaseMetrics) -> dict[str, Any]:
    return {
        "case_id": case.case_id,
        "expected_verdict": case.expected_verdict.value,
        "actual_verdict": case.actual_verdict.value if case.actual_verdict else None,
        "verdict_correct": case.verdict_correct,
        "evidence_count": case.evidence_count,
        "duplicate_rate": case.duplicate_rate,
        "average_relevance": case.average_relevance,
        "average_claim_overlap": case.average_claim_overlap,
        "overall_coverage": case.overall_coverage,
        "validation_warning_count": case.validation_warning_count,
        "verdict_changed": case.verdict_changed,
        "agent_agreement": case.agent_agreement,
        "confidence": case.confidence,
        "confidence_error": case.confidence_error,
    }


def _fmt(value: float | None) -> str:
    return f"{value:.2f}" if value is not None else "n/a"
