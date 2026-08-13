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
        )

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
    from app.evaluation.evaluator import EvaluationResult, evaluate_case
    from app.services.verification_service import analyze_verification

    dataset = load_dataset(dataset_path)
    cases = []
    skipped: list[str] = []

    for case in dataset.cases:
        try:
            response = analyze_verification(case.claim, case.doi)
            cases.append(evaluate_case(case.id, case.expected_verdict, response))
        except Exception as exc:
            print(f"Skipped live case {case.id}: {exc}", file=sys.stderr)
            skipped.append(case.id)

    from app.evaluation.metrics import aggregate_case_metrics

    aggregate = aggregate_case_metrics(cases)
    return EvaluationResult(
        dataset_path=dataset_path,
        cases=cases,
        aggregate=aggregate,
        skipped_case_ids=skipped,
    )


if __name__ == "__main__":
    raise SystemExit(main())
