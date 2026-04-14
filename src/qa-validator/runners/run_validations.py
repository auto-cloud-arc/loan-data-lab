"""
QA Validation runner for the Contoso Bank loan pipeline.

Usage:
    python run_validations.py --input <cleaned-csv> --report-dir <output-dir>
"""
from __future__ import annotations
import argparse
import json
import logging
import os
import sys
from datetime import datetime
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


def generate_report(df: pd.DataFrame, failures: list[dict], report_dir: str, input_file: str) -> str:
    """Write JSON and Markdown QA reports and return the JSON report path."""
    Path(report_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    report = {
        "generated_at": datetime.utcnow().isoformat(),
        "input_file": input_file,
        "total_records": len(df),
        "total_failures": len(failures),
        "pass_rate": f"{(1 - len(failures) / max(len(df), 1)) * 100:.1f}%",
        "failures": failures,
    }

    json_path = os.path.join(report_dir, f"qa_report_{timestamp}.json")
    with open(json_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    logger.info("QA report written to %s", json_path)

    md_path = os.path.join(report_dir, f"qa_report_{timestamp}.md")
    with open(md_path, "w") as f:
        f.write("# QA Validation Report\n\n")
        f.write(f"**Generated:** {report['generated_at']}  \n")
        f.write(f"**Input:** {input_file}  \n")
        f.write(f"**Total records:** {report['total_records']}  \n")
        f.write(f"**Total failures:** {report['total_failures']}  \n")
        f.write(f"**Pass rate:** {report['pass_rate']}  \n\n")
        if failures:
            f.write("## Failures\n\n")
            f.write("| Row | Field | Rule | Value | Message | Severity |\n")
            f.write("|-----|-------|------|-------|---------|----------|\n")
            for fail in failures:
                f.write(
                    f"| {fail['row_index']} | {fail['field']} | {fail['rule_name']} | "
                    f"{fail['actual_value']} | {fail['message']} | {fail['severity']} |\n"
                )
        else:
            f.write("## ✅ All validations passed!\n")
    logger.info("Markdown report written to %s", md_path)
    return json_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Contoso Bank QA Validator")
    parser.add_argument("--input", required=True, help="Path to cleaned loan CSV file")
    parser.add_argument("--report-dir", default="reports", help="Output directory for QA reports")
    args = parser.parse_args()

    logger.info("Loading data from %s", args.input)
    df = pd.read_csv(args.input)
    logger.info("Loaded %d records.", len(df))

    failures = run_all_validations(df)
    generate_report(df, failures, args.report_dir, args.input)

    if failures:
        critical = [f for f in failures if f.get("severity") == "critical"]
        logger.warning("%d total failures (%d critical).", len(failures), len(critical))
        return 1 if critical else 0

    logger.info("All validations passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
