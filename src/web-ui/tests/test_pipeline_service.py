from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipeline_service import (
    dataframe_from_csv_bytes,
    latest_report_path,
    prepare_validator_input,
    sanitize_file_name,
    validate_input_dataframe,
)


def test_sanitize_file_name_removes_path_components() -> None:
    assert sanitize_file_name("../../loan applications.csv") == "loan_applications.csv"


def test_sanitize_file_name_rejects_non_csv_inputs() -> None:
    with pytest.raises(ValueError, match="Only CSV files are supported."):
        sanitize_file_name("loan-data.json")


def test_dataframe_from_csv_bytes_returns_empty_dataframe_for_empty_bytes() -> None:
    result = dataframe_from_csv_bytes(b"")

    assert isinstance(result, pd.DataFrame)
    assert result.empty


def test_latest_report_path_returns_newest_match(tmp_path: Path) -> None:
    older = tmp_path / "qa_report_1.json"
    newer = tmp_path / "qa_report_2.json"
    older.write_text("{}", encoding="utf-8")
    newer.write_text("{}", encoding="utf-8")
    now = time.time()
    os.utime(older, (now - 10, now - 10))
    os.utime(newer, (now, now))

    assert latest_report_path(tmp_path, "json") == newer


def test_validate_input_dataframe_rejects_missing_columns() -> None:
    with pytest.raises(ValueError, match="Input CSV is missing required columns"):
        validate_input_dataframe(pd.DataFrame([{"ApplicationId": "APP-001"}]))


def test_prepare_validator_input_renames_columns(tmp_path: Path) -> None:
    output_path = tmp_path / "validator.csv"

    prepare_validator_input(
        pd.DataFrame(
            [
                {
                    "ApplicationId": "APP-001",
                    "CustomerId": "CUST-001",
                    "BranchCode": "BR-01",
                    "LoanAmount": 1000,
                    "LoanType": "AUTO",
                    "ApplicationDate": "2024-01-01",
                    "FirstName": "Jane",
                    "LastName": "Doe",
                    "Ssn": "123-45-6789",
                    "PhoneNumber": "(555) 555-1234",
                    "AddressLine1": "1 Main St",
                    "City": "Seattle",
                    "StateCode": "WA",
                    "ZipCode": "98101",
                    "Email": "jane@example.com",
                    "CollateralValue": 1500,
                }
            ]
        ),
        output_path,
    )

    renamed_df = pd.read_csv(output_path)
    assert "application_id" in renamed_df.columns
    assert "ApplicationId" not in renamed_df.columns
