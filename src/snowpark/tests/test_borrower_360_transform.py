import pytest
from transforms.borrower_360_transform import compute_risk_tier, standardize_branch_code


def test_standardize_branch_code_lowercase():
    assert standardize_branch_code("br-01") == "BR-01"


def test_standardize_branch_code_already_upper():
    assert standardize_branch_code("BR-01") == "BR-01"


def test_standardize_branch_code_none_returns_unknown():
    assert standardize_branch_code(None) == "UNKNOWN"


def test_standardize_branch_code_strips_whitespace():
    assert standardize_branch_code("  BR-01  ") == "BR-01"


def test_compute_risk_tier_low_ltv_mortgage():
    # LTV = 200000 / 300000 = 0.667 → LOW
    assert compute_risk_tier(200000.0, 300000.0, "MORTGAGE") == "LOW"


def test_compute_risk_tier_medium_ltv_mortgage():
    # LTV = 250000 / 290000 = 0.862 → MEDIUM
    assert compute_risk_tier(250000.0, 290000.0, "MORTGAGE") == "MEDIUM"


def test_compute_risk_tier_high_ltv_mortgage():
    # LTV = 280000 / 300000 = 0.933 → HIGH
    assert compute_risk_tier(280000.0, 300000.0, "MORTGAGE") == "HIGH"


def test_compute_risk_tier_unsecured_personal_is_high():
    assert compute_risk_tier(5000.0, None, "PERSONAL") == "HIGH"


def test_compute_risk_tier_unsecured_business_is_high():
    assert compute_risk_tier(100000.0, 200000.0, "BUSINESS") == "HIGH"


def test_compute_risk_tier_no_collateral_on_secured_is_high():
    assert compute_risk_tier(250000.0, None, "MORTGAGE") == "HIGH"


def test_compute_risk_tier_zero_collateral_is_high():
    assert compute_risk_tier(250000.0, 0.0, "AUTO") == "HIGH"


def test_compute_risk_tier_heloc_low():
    # LTV = 70000 / 150000 = 0.467 → LOW
    assert compute_risk_tier(70000.0, 150000.0, "HELOC") == "LOW"
