-- ============================================================
-- Snowflake Stored Procedure: sp_load_loan_application_curated
-- Enriches cleaned loan applications with branch reference data
-- and computes derived fields (is_secured flag).
-- ============================================================

USE DATABASE CONTOSO_LOAN_DB;

CREATE OR REPLACE PROCEDURE CURATED_ZONE.sp_load_loan_application_curated()
RETURNS VARIANT
LANGUAGE PYTHON
RUNTIME_VERSION = '3.11'
PACKAGES = ('snowflake-snowpark-python')
HANDLER = 'main'
COMMENT = 'Loads LOAN_APPLICATION_CURATED by enriching cleaned applications with branch metadata'
AS
$$
import json
from datetime import datetime
from snowflake.snowpark import Session
from snowflake.snowpark import functions as F
from snowflake.snowpark.types import BooleanType, StringType


SECURED_LOAN_TYPES = {"MORTGAGE", "AUTO", "HELOC"}


def is_secured_loan(loan_type: str) -> bool:
    """Return True if the loan type requires collateral."""
    return str(loan_type).upper() in SECURED_LOAN_TYPES


def main(session: Session) -> str:
    start_time = datetime.utcnow()

    applications = session.table("RAW_ZONE.LOAN_APPLICATION_CLEANED")
    branches = session.table("REFERENCE.BRANCH_REF")

    is_secured_udf = F.udf(
        is_secured_loan,
        return_type=BooleanType(),
        input_types=[StringType()]
    )

    curated = (
        applications.join(
            branches,
            applications["BRANCH_CODE"] == branches["BRANCH_CODE"],
            join_type="left"
        )
        .select(
            applications["APPLICATION_ID"],
            applications["CUSTOMER_ID"],
            applications["BRANCH_CODE"],
            branches["BRANCH_NAME"],
            branches["REGION"],
            applications["LOAN_AMOUNT"],
            applications["LOAN_TYPE"],
            applications["APPLICATION_DATE"],
            applications["STATE_CODE"],
            applications["ZIP_CODE"],
            applications["COLLATERAL_VALUE"],
            is_secured_udf(applications["LOAN_TYPE"]).alias("IS_SECURED"),
            F.current_timestamp().alias("CURATED_AT")
        )
    )

    row_count = curated.count()
    curated.write.mode("overwrite").save_as_table("CURATED_ZONE.LOAN_APPLICATION_CURATED")

    return json.dumps({
        "status": "success",
        "rows_written": row_count,
        "duration_seconds": (datetime.utcnow() - start_time).total_seconds()
    })
$$;
