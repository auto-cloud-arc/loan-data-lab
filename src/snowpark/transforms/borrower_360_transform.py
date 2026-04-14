"""
Snowpark transformation: borrower_360

Produces a 360-degree view of each borrower by joining cleaned application data
with branch reference data, standardizing branch codes, and computing a basic
risk tier based on loan-to-value ratio.
"""

from __future__ import annotations
import logging

logger = logging.getLogger(__name__)


def standardize_branch_code(branch_code: str) -> str:
    """Normalize branch code to uppercase stripped format, e.g. 'br-01' -> 'BR-01'."""
    if branch_code is None:
        return "UNKNOWN"
    return branch_code.strip().upper()


def compute_risk_tier(loan_amount: float, collateral_value: float | None, loan_type: str) -> str:
    """
    Compute a simple risk tier based on loan-to-value (LTV) ratio.

    Secured loans (MORTGAGE, AUTO, HELOC):
        LTV < 80%  → LOW
        80–90%     → MEDIUM
        > 90%      → HIGH
    Unsecured loans: always HIGH (no collateral to offset risk).
    """
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


def transform(session):
    """
    Build borrower_360 DataFrame.
    Reads from RAW_ZONE.LOAN_APPLICATION_CLEANED and REFERENCE.BRANCH_REF.

    Returns a Snowpark DataFrame — does not write to a table.
    Call run() to execute end-to-end.
    """
    from snowflake.snowpark import functions as F
    from snowflake.snowpark.types import StringType

    logger.info("Starting borrower_360 transformation.")

    applications = session.table("RAW_ZONE.LOAN_APPLICATION_CLEANED")
    branches = session.table("REFERENCE.BRANCH_REF")

    standardize_branch_udf = F.udf(
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
            standardize_branch_udf(applications["BRANCH_CODE"]).alias("BRANCH_CODE_NORMALIZED"),
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

    logger.info("borrower_360 transformation complete.")
    return joined


def run(session, target_table: str = "CURATED_ZONE.BORROWER_360") -> None:
    """Execute the transformation and write to the target table."""
    df = transform(session)
    row_count = df.count()
    df.write.mode("overwrite").save_as_table(target_table)
    logger.info("Written %d rows to %s.", row_count, target_table)
