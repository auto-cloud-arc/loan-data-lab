from datetime import datetime
import pandas as pd
import pytest
from rules.date_validation_rules import check_application_date_not_future


def test_past_dates_pass(valid_loan_df):
    failures = check_application_date_not_future(valid_loan_df)
    assert len(failures) == 0


def test_future_date_fails(invalid_loan_df):
    failures = check_application_date_not_future(invalid_loan_df)
    assert any(f.rule_name == "application_date_not_future" for f in failures)


def test_today_passes():
    df = pd.DataFrame([{"application_date": datetime.utcnow().strftime("%Y-%m-%d")}])
    failures = check_application_date_not_future(df)
    assert len(failures) == 0


def test_missing_column_returns_empty():
    df = pd.DataFrame([{"loan_amount": 1000}])
    failures = check_application_date_not_future(df)
    assert len(failures) == 0


def test_null_date_is_skipped():
    df = pd.DataFrame([{"application_date": None}])
    failures = check_application_date_not_future(df)
    assert len(failures) == 0


def test_empty_dataframe_returns_no_failures():
    df = pd.DataFrame(columns=["application_date"])
    failures = check_application_date_not_future(df)
    assert len(failures) == 0
