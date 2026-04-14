import sys
import os
import pandas as pd
import pytest

# Add repo root and qa-validator directory to Python path
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
_QA_VALIDATOR_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, _REPO_ROOT)
sys.path.insert(0, _QA_VALIDATOR_DIR)


@pytest.fixture
def valid_loan_df():
    return pd.DataFrame([
        {
            "application_id": "APP-001",
            "customer_id": "CUST-001",
            "branch_code": "BR-01",
            "loan_amount": 250000.0,
            "loan_type": "MORTGAGE",
            "application_date": "2024-01-15",
            "collateral_value": 300000.0,
        },
        {
            "application_id": "APP-002",
            "customer_id": "CUST-002",
            "branch_code": "BR-02",
            "loan_amount": 15000.0,
            "loan_type": "AUTO",
            "application_date": "2024-02-10",
            "collateral_value": 18000.0,
        },
    ])


@pytest.fixture
def invalid_loan_df():
    return pd.DataFrame([
        {
            "application_id": None,
            "customer_id": "CUST-001",
            "branch_code": "BR-01",
            "loan_amount": -500.0,
            "loan_type": "MORTGAGE",
            "application_date": "2099-01-01",
            "collateral_value": None,
        },
        {
            "application_id": "APP-002",
            "customer_id": None,
            "branch_code": "BR-02",
            "loan_amount": 15000.0,
            "loan_type": "AUTO",
            "application_date": "2024-02-10",
            "collateral_value": 18000.0,
        },
    ])
