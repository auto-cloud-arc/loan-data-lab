import json
from pathlib import Path

from reports.report_generator import generate_json_report, generate_markdown_report
from rules.reconciliation_rules import check_row_count_reconciliation


def test_generate_json_report_contains_expected_structure(tmp_path):
    failures = [
        {
            "row_index": 0,
            "field": "application_id",
            "rule_name": "not_null",
            "actual_value": None,
            "message": "Field 'application_id' must not be null or empty.",
            "severity": "critical",
        }
    ]
    reconciliation = check_row_count_reconciliation(
        table_name="loan_application_curated",
        source_count=100,
        target_count=99,
        tolerance_pct=0.01,
    )

    report_path = generate_json_report(
        failures=failures,
        total_records=100,
        input_file="sample-data/cleaned/loan_applications_cleaned.csv",
        report_dir=str(tmp_path),
        reconciliation=reconciliation,
    )

    payload = json.loads(Path(report_path).read_text())
    assert payload["total_records"] == 100
    assert payload["total_failures"] == 1
    assert payload["failures"][0]["rule_name"] == "not_null"
    assert payload["reconciliation"]["table_name"] == "loan_application_curated"


def test_generate_markdown_report_includes_reconciliation_summary(tmp_path):
    reconciliation = check_row_count_reconciliation(
        table_name="loan_application_curated",
        source_count=100,
        target_count=120,
        tolerance_pct=0.01,
    )

    report_path = generate_markdown_report(
        failures=[],
        total_records=100,
        input_file="sample-data/cleaned/loan_applications_cleaned.csv",
        report_dir=str(tmp_path),
        reconciliation=reconciliation,
    )

    content = Path(report_path).read_text()
    assert "# QA Validation Report" in content
    assert "## Reconciliation" in content
    assert "Status: FAIL" in content
