from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipeline_service import dataframe_from_csv_bytes, latest_report_path, sanitize_file_name


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
