import pandas as pd
import pytest
from rules.business_rules import (
    check_positive_loan_amount,
    check_collateral_for_secured_loans,
    check_valid_branch_code,
)


def test_positive_loan_amounts_pass(valid_loan_df):
    failures = check_positive_loan_amount(valid_loan_df)
    assert len(failures) == 0


def test_negative_loan_amount_fails(invalid_loan_df):
    failures = check_positive_loan_amount(invalid_loan_df)
    assert any(f.rule_name == "positive_loan_amount" for f in failures)


def test_zero_loan_amount_fails():
    df = pd.DataFrame([{"loan_amount": 0.0}])
    failures = check_positive_loan_amount(df)
    assert len(failures) == 1


def test_missing_loan_amount_column_returns_empty():
    df = pd.DataFrame([{"application_id": "APP-001"}])
    failures = check_positive_loan_amount(df)
    assert len(failures) == 0


def test_collateral_present_for_secured_loans_passes(valid_loan_df):
    failures = check_collateral_for_secured_loans(valid_loan_df)
    assert len(failures) == 0


def test_missing_collateral_for_mortgage_fails(invalid_loan_df):
    failures = check_collateral_for_secured_loans(invalid_loan_df)
    assert any(f.rule_name == "collateral_required_for_secured_loan" for f in failures)


def test_personal_loan_without_collateral_passes():
    df = pd.DataFrame([{
        "loan_type": "PERSONAL",
        "loan_amount": 5000.0,
        "collateral_value": None,
    }])
    failures = check_collateral_for_secured_loans(df)
    assert len(failures) == 0


def test_heloc_without_collateral_fails():
    df = pd.DataFrame([{
        "loan_type": "HELOC",
        "loan_amount": 50000.0,
        "collateral_value": None,
    }])
    failures = check_collateral_for_secured_loans(df)
    assert len(failures) == 1


def test_valid_branch_code_no_reference_returns_empty(valid_loan_df):
    failures = check_valid_branch_code(valid_loan_df, valid_branches=None)
    assert len(failures) == 0


def test_valid_branch_code_passes_with_reference():
    df = pd.DataFrame([{"branch_code": "BR-01"}])
    failures = check_valid_branch_code(df, valid_branches={"BR-01", "BR-02"})
    assert len(failures) == 0


def test_invalid_branch_code_fails_with_reference():
    df = pd.DataFrame([{"branch_code": "BR-99"}])
    failures = check_valid_branch_code(df, valid_branches={"BR-01", "BR-02"})
    assert len(failures) == 1
    assert failures[0].rule_name == "valid_branch_code"
