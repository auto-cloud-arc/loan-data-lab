import sys
import os
import pytest

# Add repo root and snowpark source directory to Python path
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
_SNOWPARK_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, _REPO_ROOT)
sys.path.insert(0, _SNOWPARK_DIR)


@pytest.fixture
def sample_applications():
    return [
        {
            "APPLICATION_ID": "APP-001",
            "CUSTOMER_ID": "CUST-001",
            "LOAN_AMOUNT": 250000.0,
            "LOAN_TYPE": "MORTGAGE",
            "BRANCH_CODE": "br-01",
            "COLLATERAL_VALUE": 300000.0,
            "APPLICATION_DATE": "2024-01-15",
        },
        {
            "APPLICATION_ID": "APP-002",
            "CUSTOMER_ID": "CUST-002",
            "LOAN_AMOUNT": 15000.0,
            "LOAN_TYPE": "AUTO",
            "BRANCH_CODE": "BR-02",
            "COLLATERAL_VALUE": 18000.0,
            "APPLICATION_DATE": "2024-02-10",
        },
        {
            "APPLICATION_ID": "APP-003",
            "CUSTOMER_ID": "CUST-003",
            "LOAN_AMOUNT": 5000.0,
            "LOAN_TYPE": "PERSONAL",
            "BRANCH_CODE": "BR-03",
            "COLLATERAL_VALUE": None,
            "APPLICATION_DATE": "2024-03-01",
        },
    ]
