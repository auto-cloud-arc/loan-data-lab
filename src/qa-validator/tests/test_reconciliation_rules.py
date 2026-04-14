from rules.reconciliation_rules import check_row_count_reconciliation


def test_row_count_reconciliation_exact_match_passes():
    result = check_row_count_reconciliation("loan_application_curated", 100, 100)
    assert result.passed is True
    assert result.diff_pct == 0.0


def test_row_count_reconciliation_within_tolerance_passes():
    result = check_row_count_reconciliation("loan_application_curated", 1000, 995, tolerance_pct=0.01)
    assert result.passed is True


def test_row_count_reconciliation_exceeds_tolerance_fails():
    result = check_row_count_reconciliation("loan_application_curated", 1000, 970, tolerance_pct=0.01)
    assert result.passed is False
    assert "FAIL" in result.message


def test_row_count_reconciliation_source_empty_nonempty_target_fails():
    result = check_row_count_reconciliation("loan_application_curated", 0, 5)
    assert result.passed is False
