from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from app.evaluation.dataset_loader import default_dataset_path, default_fixtures_dir, load_dataset
from app.evaluation.evaluator import evaluate_offline_dataset, load_and_evaluate_offline
from app.evaluation.io_paths import default_baseline_path, default_results_dir, write_json
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
    from app.services.verification_service import analyze_verification

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

    for case in live_eligible_cases:
        try:
            response = analyze_verification(case.claim, case.doi)
            responses_by_id[case.id] = response
            cases.append(evaluate_case(case.id, case.expected_verdict, response))
        except Exception as exc:
            reason = str(exc).split(":")[0] if ":" in str(exc) else "unknown"
            skip_reasons[reason] = skip_reasons.get(reason, 0) + 1
            print(f"Skipped live case {case.id}: {exc}", file=sys.stderr)
            skipped.append(case.id)
    
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
    
    print(f"Evaluated:           {len(cases)}", file=sys.stderr)
    print(f"Skipped:             {len(skipped)}", file=sys.stderr)
    if skip_reasons:
        print(f"Skip reasons:", file=sys.stderr)
        for reason, count in skip_reasons.items():
            print(f"  - {reason}: {count}", file=sys.stderr)
    print("", file=sys.stderr)
    
    return EvaluationResult(
        dataset_path=dataset_path,
        cases=cases,
        aggregate=aggregate,
        skipped_case_ids=skipped,
        responses_by_id=responses_by_id,
    )


if __name__ == "__main__":
    raise SystemExit(main())
