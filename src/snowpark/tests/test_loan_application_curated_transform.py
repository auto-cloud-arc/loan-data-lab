"""
Tests for source_target_reconciliation module and loan_application_curated_transform helpers.
Both are covered here as lightweight integration tests for the snowpark pipeline logic.
"""
import pytest
import sys
import types
from reconciliation.source_target_reconciliation import reconcile_counts
from transforms.loan_application_curated_transform import (
    is_secured_loan,
    normalize_loan_type,
    normalize_state_code,
    normalize_zip_code,
    standardize_branch_code,
)


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
    assert is_secured_loan("MORTGAGE") is True
    assert is_secured_loan("PERSONAL") is False
    assert normalize_loan_type("  mortgage  ") == "MORTGAGE"
    assert normalize_loan_type(None) == "UNKNOWN"


def test_standardize_branch_code_transform():
    assert standardize_branch_code(" br-01 ") == "BR-01"
    assert standardize_branch_code("BR-99") == "BR-99"
    assert standardize_branch_code(None) == "UNKNOWN"
    assert standardize_branch_code("   ") == "UNKNOWN"


def test_normalize_state_code_transform():
    assert normalize_state_code(" ca ") == "CA"
    assert normalize_state_code("NY") == "NY"
    assert normalize_state_code("CAL") is None
    assert normalize_state_code(None) is None


def test_normalize_zip_code_transform():
    assert normalize_zip_code("90210") == "90210"
    assert normalize_zip_code("90210-1234") == "90210"
    assert normalize_zip_code(" 90-210 ") == "90210"
    assert normalize_zip_code("123") is None
    assert normalize_zip_code(None) is None


def test_transform_with_mocked_snowpark_session_validates_join_shape_and_column_order(monkeypatch):
    class FakeExpr:
        def __init__(self, name):
            self.name = name

        def alias(self, alias_name):
            return FakeExpr(alias_name)

        def __eq__(self, other):
            return ("eq", self, other)

    class FakeUdf:
        def __init__(self, name):
            self.name = name

        def __call__(self, *args):
            arg_names = [getattr(a, "name", str(a)) for a in args]
            return FakeExpr(f"{self.name}({','.join(arg_names)})")

    class FakeFunctionsModule:
        @staticmethod
        def col(name):
            return FakeExpr(name)

        @staticmethod
        def lit(value):
            return FakeExpr(f"lit({value})")

        @staticmethod
        def coalesce(*args):
            names = [getattr(a, "name", str(a)) for a in args]
            return FakeExpr(f"coalesce({','.join(names)})")

        @staticmethod
        def current_timestamp():
            return FakeExpr("current_timestamp")

        @staticmethod
        def udf(fn, return_type=None, input_types=None):
            return FakeUdf(fn.__name__)

    class FakeType:
        pass

    class FakeTypesModule:
        StringType = FakeType
        BooleanType = FakeType

    class FakeDataFrame:
        def __init__(self, session, name):
            self.session = session
            self.name = name
            self.selected_columns = []

        def __getitem__(self, item):
            return FakeExpr(item)

        def alias(self, alias_name):
            self.name = alias_name
            return self

        def select(self, *cols):
            selected = FakeDataFrame(self.session, self.name)
            selected.selected_columns = [getattr(c, "name", str(c)) for c in cols]
            return selected

        def filter(self, condition):
            return self

        def join(self, other, condition, join_type="inner"):
            self.session.joins.append((self.name, other.name, join_type))
            return FakeDataFrame(self.session, f"join({self.name},{other.name})")

        def with_column(self, name, value):
            return self

    class FakeSession:
        def __init__(self):
            self.table_names = []
            self.joins = []

        def table(self, name):
            self.table_names.append(name)
            return FakeDataFrame(self, name)

    fake_functions = FakeFunctionsModule()
    fake_types = FakeTypesModule()

    snowflake_module = types.ModuleType("snowflake")
    snowpark_module = types.ModuleType("snowflake.snowpark")
    snowpark_module.functions = fake_functions
    snowpark_module.types = fake_types

    monkeypatch.setitem(sys.modules, "snowflake", snowflake_module)
    monkeypatch.setitem(sys.modules, "snowflake.snowpark", snowpark_module)
    monkeypatch.setitem(sys.modules, "snowflake.snowpark.functions", fake_functions)
    monkeypatch.setitem(sys.modules, "snowflake.snowpark.types", fake_types)

    from transforms.loan_application_curated_transform import transform

    session = FakeSession()
    curated_df = transform(session)

    assert session.table_names == [
        "RAW_ZONE.LOAN_APPLICATION_CLEANED",
        "CURATED_ZONE.BORROWER_360",
        "REFERENCE.BRANCH_REF",
    ]

    assert session.joins == [
        ("app", "borrower", "left"),
        ("join(app,borrower)", "branch", "left"),
    ]

    assert curated_df.selected_columns == [
        "APPLICATION_ID",
        "CUSTOMER_ID",
        "BRANCH_CODE",
        "BRANCH_NAME",
        "REGION",
        "LOAN_AMOUNT",
        "LOAN_TYPE",
        "APPLICATION_DATE",
        "STATE_CODE",
        "ZIP_CODE",
        "COLLATERAL_VALUE",
        "IS_SECURED",
        "CURATED_AT",
    ]
