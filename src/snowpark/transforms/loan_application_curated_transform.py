"""
Snowpark transformation: loan_application_curated

Enriches cleaned loan applications with branch reference metadata
and computes the is_secured derived flag.
"""

from __future__ import annotations
import logging

logger = logging.getLogger(__name__)

SECURED_LOAN_TYPES = {"MORTGAGE", "AUTO", "HELOC"}


def is_secured_loan(loan_type: str) -> bool:
    """Return True if the loan type requires collateral (secured loan)."""
    return str(loan_type).upper() in SECURED_LOAN_TYPES


def normalize_loan_type(loan_type: str) -> str:
    """Ensure loan type is uppercase and trimmed."""
    if loan_type is None:
        return "UNKNOWN"
    return loan_type.strip().upper()


def transform(session):
    """
    Build loan_application_curated DataFrame.
    Reads from RAW_ZONE.LOAN_APPLICATION_CLEANED and REFERENCE.BRANCH_REF.

    Returns a Snowpark DataFrame — does not write to a table.
    """
    from snowflake.snowpark import functions as F
    from snowflake.snowpark.types import BooleanType, StringType

    logger.info("Starting loan_application_curated transformation.")

    applications = session.table("RAW_ZONE.LOAN_APPLICATION_CLEANED")
    branches = session.table("REFERENCE.BRANCH_REF")

    is_secured_udf = F.udf(
        is_secured_loan,
        return_type=BooleanType(),
        input_types=[StringType()]
    )

    normalize_loan_type_udf = F.udf(
        normalize_loan_type,
        return_type=StringType(),
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
            normalize_loan_type_udf(applications["LOAN_TYPE"]).alias("LOAN_TYPE"),
            applications["APPLICATION_DATE"],
            applications["STATE_CODE"],
            applications["ZIP_CODE"],
            applications["COLLATERAL_VALUE"],
            is_secured_udf(applications["LOAN_TYPE"]).alias("IS_SECURED"),
            F.current_timestamp().alias("CURATED_AT")
        )
    )

    logger.info("loan_application_curated transformation complete.")
    return curated


def run(session, target_table: str = "CURATED_ZONE.LOAN_APPLICATION_CURATED") -> None:
    """Execute the transformation and write to the target table."""
    df = transform(session)
    row_count = df.count()
    df.write.mode("overwrite").save_as_table(target_table)
    logger.info("Written %d rows to %s.", row_count, target_table)
