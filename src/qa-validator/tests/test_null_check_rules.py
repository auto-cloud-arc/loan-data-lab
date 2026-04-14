import pandas as pd
import pytest
from rules.null_check_rules import check_not_null, check_required_business_keys


def test_check_not_null_no_failures(valid_loan_df):
    failures = check_not_null(valid_loan_df, "application_id")
    assert len(failures) == 0


def test_check_not_null_with_null(invalid_loan_df):
    failures = check_not_null(invalid_loan_df, "application_id")
    assert len(failures) == 1
    assert failures[0].field == "application_id"
    assert failures[0].rule_name == "not_null"


def test_check_not_null_missing_column_returns_empty(valid_loan_df):
    failures = check_not_null(valid_loan_df, "nonexistent_field")
    assert len(failures) == 0


def test_check_not_null_empty_dataframe():
    df = pd.DataFrame(columns=["application_id"])
    failures = check_not_null(df, "application_id")
    assert len(failures) == 0


def test_check_not_null_empty_string_is_flagged():
    df = pd.DataFrame([{"application_id": ""}])
    failures = check_not_null(df, "application_id")
    assert len(failures) == 1


def test_check_required_business_keys_valid(valid_loan_df):
    failures = check_required_business_keys(valid_loan_df)
    assert len(failures) == 0


def test_check_required_business_keys_invalid(invalid_loan_df):
    failures = check_required_business_keys(invalid_loan_df)
    # application_id is null in row 0, customer_id is null in row 1
    assert len(failures) >= 2
