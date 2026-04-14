-- ============================================================
-- Snowflake Stored Procedure: sp_load_borrower_360
-- Loads the CURATED_ZONE.BORROWER_360 table by joining
-- cleaned application data with branch reference data and
-- computing risk tiers based on loan-to-value ratio.
-- ============================================================

USE DATABASE CONTOSO_LOAN_DB;

CREATE OR REPLACE PROCEDURE CURATED_ZONE.sp_load_borrower_360()
RETURNS VARIANT
LANGUAGE PYTHON
RUNTIME_VERSION = '3.11'
PACKAGES = ('snowflake-snowpark-python')
HANDLER = 'main'
COMMENT = 'Loads BORROWER_360 from cleaned applications joined with branch reference data'
AS
$$
import json
from datetime import datetime
from snowflake.snowpark import Session
from snowflake.snowpark import functions as F
from snowflake.snowpark.types import StringType


def standardize_branch_code(branch_code: str) -> str:
    """Normalize branch code to uppercase stripped format."""
    if branch_code is None:
        return "UNKNOWN"
    return branch_code.strip().upper()


def compute_risk_tier(loan_amount: float, collateral_value, loan_type: str) -> str:
    """Compute risk tier based on loan-to-value ratio."""
    secured_types = {"MORTGAGE", "AUTO", "HELOC"}
    if str(loan_type).upper() not in secured_types:
        return "HIGH"
    if collateral_value is None or float(collateral_value) <= 0:
        return "HIGH"
    ltv = float(loan_amount) / float(collateral_value)
    if ltv < 0.80:
        return "LOW"
    elif ltv <= 0.90:
        return "MEDIUM"
    return "HIGH"


def main(session: Session) -> str:
    start_time = datetime.utcnow()

    applications = session.table("RAW_ZONE.LOAN_APPLICATION_CLEANED")
    branches = session.table("REFERENCE.BRANCH_REF")

    standardize_udf = F.udf(
        standardize_branch_code,
        return_type=StringType(),
        input_types=[StringType()]
    )

    risk_tier_udf = F.udf(
        compute_risk_tier,
        return_type=StringType()
    )

    joined = (
        applications.join(
            branches,
            applications["BRANCH_CODE"] == branches["BRANCH_CODE"],
            join_type="left"
        )
        .select(
            applications["APPLICATION_ID"],
            applications["CUSTOMER_ID"],
            applications["FIRST_NAME"],
            applications["LAST_NAME"],
            applications["LOAN_AMOUNT"],
            applications["LOAN_TYPE"],
            applications["COLLATERAL_VALUE"],
            applications["APPLICATION_DATE"],
            standardize_udf(applications["BRANCH_CODE"]).alias("BRANCH_CODE_NORMALIZED"),
            branches["BRANCH_NAME"],
            branches["REGION"],
            risk_tier_udf(
                applications["LOAN_AMOUNT"],
                applications["COLLATERAL_VALUE"],
                applications["LOAN_TYPE"]
            ).alias("RISK_TIER"),
            F.current_timestamp().alias("TRANSFORMED_AT")
        )
    )

    row_count = joined.count()
    joined.write.mode("overwrite").save_as_table("CURATED_ZONE.BORROWER_360")

    return json.dumps({
        "status": "success",
        "rows_written": row_count,
        "duration_seconds": (datetime.utcnow() - start_time).total_seconds()
    })
$$;
