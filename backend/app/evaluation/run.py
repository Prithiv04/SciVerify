from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from app.evaluation.dataset_loader import default_dataset_path, default_fixtures_dir, load_dataset
from app.evaluation.evaluator import evaluate_offline_dataset, load_and_evaluate_offline
from app.evaluation.io_paths import default_baseline_path, default_results_dir, write_json
from app.evaluation.live_diagnostics import (
    DETERMINISTIC_FAILURE_CATEGORIES,
    LiveCaseResult,
    LiveEvaluationMetrics,
)
from app.evaluation.regression import (
    aggregate_to_baseline_payload,
    compare_to_baseline,
    load_baseline,
    load_thresholds,
)
from app.evaluation.report import render_markdown_report, write_reports


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run SciVerify offline evaluation against benchmark fixtures.",
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=default_dataset_path(),
        help="Path to benchmark dataset JSON.",
    )
    parser.add_argument(
        "--fixtures-dir",
        type=Path,
        default=default_fixtures_dir(),
        help="Directory containing offline VerificationResponse fixtures.",
    )
    parser.add_argument(
        "--compare-baseline",
        action="store_true",
        help="Compare results against evaluation/baseline.json.",
    )
    parser.add_argument(
        "--update-baseline",
        action="store_true",
        help="Explicitly overwrite evaluation/baseline.json with current metrics.",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        default=default_baseline_path(),
        help="Path to baseline metrics JSON.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=default_results_dir(),
        help="Directory for latest evaluation reports.",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help=(
            "Run live verification for each dataset case. "
            "WARNING: may call external APIs and consume LLM quota."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.live:
        print(
            "WARNING: Live evaluation may retrieve papers and call configured LLM providers.",
            file=sys.stderr,
        )
        result = _run_live_evaluation(args.dataset)
    else:
        result = load_and_evaluate_offline(args.dataset, args.fixtures_dir)
        result = type(result)(
            dataset_path=args.dataset,
            cases=result.cases,
            aggregate=result.aggregate,
            skipped_case_ids=result.skipped_case_ids,
            responses_by_id=result.responses_by_id,
        )

        # Report offline evaluation statistics
        dataset = load_dataset(args.dataset)
        print(f"Offline evaluation", file=sys.stderr)
        print(f"------------------", file=sys.stderr)
        print(f"Dataset cases:       {len(dataset.cases)}", file=sys.stderr)
        print(f"Evaluated:           {len(result.cases)}", file=sys.stderr)
        print(f"Skipped:             {len(result.skipped_case_ids)}", file=sys.stderr)
        print("", file=sys.stderr)

    regression = None
    if args.compare_baseline:
        baseline = load_baseline(args.baseline)
        regression = compare_to_baseline(result.aggregate, baseline, thresholds=load_thresholds())

    json_path, md_path = write_reports(result, output_dir=args.output_dir, regression=regression)
    print(render_markdown_report(result, regression=regression))
    print("")
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")

    if args.update_baseline:
        payload = aggregate_to_baseline_payload(result.aggregate)
        write_json(args.baseline, payload)
        print(f"Updated baseline: {args.baseline}")
    elif args.compare_baseline and regression and not regression.passed:
        return 1

    return 0


def _run_live_evaluation(dataset_path: Path):
    from app.evaluation.dataset_loader import is_placeholder_doi, validate_live_eligibility
    from app.evaluation.evaluator import EvaluationResult, evaluate_case
    from app.evaluation.live_diagnostics import evaluate_live_case, LiveCaseResult, LiveEvaluationMetrics, MAX_RETRIES

    dataset = load_dataset(dataset_path)

    # Validate live eligibility and report placeholder DOIs
    eligibility_warnings = validate_live_eligibility(dataset)
    if eligibility_warnings:
        print("Live evaluation eligibility warnings:", file=sys.stderr)
        for warning in eligibility_warnings:
            print(f"  {warning}", file=sys.stderr)
        print("", file=sys.stderr)

    # Filter to live-eligible cases only
    live_eligible_cases = [case for case in dataset.cases if case.live_evaluable]
    total_cases = len(dataset.cases)
    live_eligible_count = len(live_eligible_cases)

    print(f"Live evaluation", file=sys.stderr)
    print(f"----------------", file=sys.stderr)
    print(f"Dataset cases:       {total_cases}", file=sys.stderr)
    print(f"Live eligible:       {live_eligible_count}", file=sys.stderr)
    print(f"Not live eligible:   {total_cases - live_eligible_count}", file=sys.stderr)
    print("", file=sys.stderr)

    cases = []
    skipped: list[str] = []
    skip_reasons: dict[str, int] = {}
    responses_by_id: dict = {}
    live_case_results: list[LiveCaseResult] = []
    failure_category_counts: dict[str, int] = {}

    # Initialize live metrics
    live_metrics = LiveEvaluationMetrics()
    live_metrics.live_eligible_count = live_eligible_count

    for case in live_eligible_cases:
        live_result, response = evaluate_live_case(case, max_retries=MAX_RETRIES)
        live_case_results.append(live_result)
        live_metrics.total_retrieval_attempts += live_result.retrieval_attempts
        live_metrics.total_elapsed_seconds += live_result.elapsed_seconds

        if live_result.status == "evaluated" and response is not None:
            # Successfully evaluated - use the response
            responses_by_id[case.id] = response
            cases.append(evaluate_case(case.id, case.expected_verdict, response))
            live_metrics.successfully_evaluated_count += 1
        else:
            # Failed or skipped - determine if it's a retrieval failure
            skipped.append(case.id)
            if live_result.failure_category:
                category_name = live_result.failure_category.value
                failure_category_counts[category_name] = failure_category_counts.get(category_name, 0) + 1
                live_metrics.failure_category_counts[category_name] += 1

                # Check if this is a retrieval/infrastructure failure
                if live_result.failure_category in DETERMINISTIC_FAILURE_CATEGORIES:
                    live_metrics.retrieval_failure_count += 1
                    skip_reasons[f"retrieval_{category_name}"] = skip_reasons.get(f"retrieval_{category_name}", 0) + 1
                else:
                    # Verification failure (LLM failure, etc.)
                    live_metrics.verification_failure_count += 1
                    skip_reasons[f"verification_{category_name}"] = skip_reasons.get(f"verification_{category_name}", 0) + 1

                print(f"Skipped live case {case.id}: {live_result.failure_category.value} - {live_result.failure_reason}", file=sys.stderr)
            else:
                skip_reasons["unknown"] = skip_reasons.get("unknown", 0) + 1
                print(f"Skipped live case {case.id}: unknown reason", file=sys.stderr)

    # Also add non-live-eligible cases to skipped
    for case in dataset.cases:
        if not case.live_evaluable:
            skipped.append(case.id)
            if is_placeholder_doi(case.doi):
                skip_reasons["Placeholder DOI"] = skip_reasons.get("Placeholder DOI", 0) + 1
            else:
                skip_reasons["Not live eligible"] = skip_reasons.get("Not live eligible", 0) + 1

    from app.evaluation.metrics import aggregate_case_metrics

    aggregate = aggregate_case_metrics(cases)

    # Print improved CLI output
    print(f"Successfully evaluated: {live_metrics.successfully_evaluated_count}", file=sys.stderr)
    print(f"Retrieval/infrastructure failures: {live_metrics.retrieval_failure_count}", file=sys.stderr)
    print(f"Verification failures: {live_metrics.verification_failure_count}", file=sys.stderr)
    print(f"Skipped:             {len(skipped)}", file=sys.stderr)

    if skip_reasons:
        print(f"Skip reasons:", file=sys.stderr)
        for reason, count in sorted(skip_reasons.items()):
            print(f"  - {reason}: {count}", file=sys.stderr)

    if failure_category_counts:
        print(f"", file=sys.stderr)
        print(f"Failure categories:", file=sys.stderr)
        for category, count in sorted(failure_category_counts.items()):
            print(f"  - {category}: {count}", file=sys.stderr)

    if live_case_results:
        print(f"", file=sys.stderr)
        print(f"Retrieval diagnostics:", file=sys.stderr)
        print(f"  - Total retrieval attempts: {live_metrics.total_retrieval_attempts}", file=sys.stderr)
        print(f"  - Average attempts per case: {live_metrics.average_attempts_per_case:.1f}", file=sys.stderr)
        print(f"  - Total elapsed time: {live_metrics.total_elapsed_seconds:.1f}s", file=sys.stderr)
        print(f"", file=sys.stderr)
        print(f"Live verification metrics:", file=sys.stderr)
        print(f"  - Retrieval success rate: {live_metrics.retrieval_success_rate:.1%}", file=sys.stderr)
        print(f"  - Retrieval failure rate: {live_metrics.retrieval_failure_rate:.1%}", file=sys.stderr)

    print("", file=sys.stderr)

    return EvaluationResult(
        dataset_path=dataset_path,
        cases=cases,
        aggregate=aggregate,
        skipped_case_ids=skipped,
        responses_by_id=responses_by_id,
        live_case_results=live_case_results,
        live_metrics=live_metrics,
    )


if __name__ == "__main__":
    raise SystemExit(main())
