"""
QA Validation runner for the Contoso Bank loan pipeline.

Usage:
    python run_validations.py --input <cleaned-csv> --report-dir <output-dir>
"""
from __future__ import annotations
import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

# Add the qa-validator root directory to sys.path so rules package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rules.null_check_rules import check_required_business_keys
from rules.date_validation_rules import check_application_date_not_future
from rules.business_rules import (
    check_positive_loan_amount,
    check_collateral_for_secured_loans,
)
from rules.reconciliation_rules import check_row_count_reconciliation
from reports.report_generator import generate_json_report, generate_markdown_report

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def run_all_validations(df: pd.DataFrame) -> list[dict]:
    """Run all registered validation rules against the DataFrame."""
    failures: list[dict] = []

    for f in check_required_business_keys(df):
        failures.append(f.__dict__)
    for f in check_application_date_not_future(df):
        failures.append(f.__dict__)
    for f in check_positive_loan_amount(df):
        failures.append(f.__dict__)
    for f in check_collateral_for_secured_loans(df):
        failures.append(f.__dict__)

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Contoso Bank QA Validator")
    parser.add_argument("--input", required=True, help="Path to cleaned loan CSV file")
    parser.add_argument("--report-dir", default="reports", help="Output directory for QA reports")
    parser.add_argument(
        "--source-count",
        type=int,
        default=None,
        help="Optional source system row count for reconciliation",
    )
    parser.add_argument(
        "--target-count",
        type=int,
        default=None,
        help="Optional curated target row count for reconciliation",
    )
    parser.add_argument(
        "--reconciliation-table",
        default="loan_application_curated",
        help="Logical table name for reconciliation summary",
    )
    parser.add_argument(
        "--reconciliation-tolerance",
        type=float,
        default=0.01,
        help="Allowed row-count difference ratio for reconciliation (default: 0.01)",
    )
    args = parser.parse_args()

    logger.info("Loading data from %s", args.input)
    df = pd.read_csv(args.input)
    logger.info("Loaded %d records.", len(df))

    failures = run_all_validations(df)

    source_count = args.source_count if args.source_count is not None else len(df)
    target_count = args.target_count if args.target_count is not None else len(df)
    reconciliation = check_row_count_reconciliation(
        table_name=args.reconciliation_table,
        source_count=source_count,
        target_count=target_count,
        tolerance_pct=args.reconciliation_tolerance,
    )

    json_path = generate_json_report(
        failures=failures,
        total_records=len(df),
        input_file=args.input,
        report_dir=args.report_dir,
        reconciliation=reconciliation,
    )
    md_path = generate_markdown_report(
        failures=failures,
        total_records=len(df),
        input_file=args.input,
        report_dir=args.report_dir,
        reconciliation=reconciliation,
    )

    logger.info("QA report written to %s", json_path)
    logger.info("Markdown report written to %s", md_path)

    if failures:
        critical = [f for f in failures if f.get("severity") == "critical"]
        logger.warning("%d total failures (%d critical).", len(failures), len(critical))
        return 1 if critical else 0

    if not reconciliation.passed:
        logger.warning("Reconciliation failed: %s", reconciliation.message)
        return 1

    logger.info("All validations passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
