import pytest
from reconciliation.source_target_reconciliation import reconcile_counts


def test_reconcile_counts_exact_match():
    result = reconcile_counts("loan_application_raw", 100, 100)
    assert result.passed is True


def test_reconcile_counts_within_tolerance():
    # 1 row difference on 1000 = 0.1% diff — within 1% tolerance
    result = reconcile_counts("loan_application_raw", 1000, 999)
    assert result.passed is True


def test_reconcile_counts_exceeds_tolerance():
    # 20 row difference on 1000 = 2% diff — exceeds 1% tolerance
    result = reconcile_counts("loan_application_raw", 1000, 980)
    assert result.passed is False


def test_reconcile_counts_source_empty_target_empty():
    result = reconcile_counts("empty_table", 0, 0)
    assert result.passed is True


def test_reconcile_counts_source_empty_target_not_empty():
    result = reconcile_counts("empty_table", 0, 5)
    assert result.passed is False


def test_reconcile_counts_custom_tolerance():
    # 5% diff with 10% tolerance should pass
    result = reconcile_counts("test_table", 100, 95, tolerance_pct=0.10)
    assert result.passed is True


def test_reconcile_counts_result_contains_table_name():
    result = reconcile_counts("my_table", 50, 50)
    assert result.table_name == "my_table"


def test_reconcile_counts_message_contains_diff():
    result = reconcile_counts("my_table", 1000, 980)
    assert "FAIL" in result.message


def test_reconcile_counts_pass_message():
    result = reconcile_counts("my_table", 100, 100)
    assert "PASS" in result.message


def test_is_secured_loan_transform():
    from transforms.loan_application_curated_transform import is_secured_loan, normalize_loan_type
    assert is_secured_loan("MORTGAGE") is True
    assert is_secured_loan("PERSONAL") is False
    assert normalize_loan_type("  mortgage  ") == "MORTGAGE"
    assert normalize_loan_type(None) == "UNKNOWN"
