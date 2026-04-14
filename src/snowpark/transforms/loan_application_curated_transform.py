"""
Snowpark transformation: loan_application_curated

Builds CURATED_ZONE.LOAN_APPLICATION_CURATED by combining cleaned loan
applications with borrower enrichment data and branch reference metadata.

Banking assumptions encoded here:
1. Branch code is a critical business key for downstream portfolio rollups.
   Legacy systems can send mixed case / padded values, so we canonicalize
   to uppercase trimmed code before joining.
2. Only MORTGAGE, AUTO, and HELOC are secured products that should carry
   collateral expectations in risk reporting.
3. Inactive branch reference rows should not be used for enrichment, but
   applications are still preserved with left joins to avoid data loss.
"""

from __future__ import annotations
import logging
import re

logger = logging.getLogger(__name__)

SECURED_LOAN_TYPES = {"MORTGAGE", "AUTO", "HELOC"}


def is_secured_loan(loan_type: str) -> bool:
    """Return True if the product is secured per Contoso lending policy."""
    return normalize_loan_type(loan_type) in SECURED_LOAN_TYPES


def normalize_loan_type(loan_type: str) -> str:
    """Ensure loan type is uppercase and trimmed."""
    if loan_type is None:
        return "UNKNOWN"
    return loan_type.strip().upper()


def standardize_branch_code(branch_code: str | None) -> str:
    """
    Canonical branch key used across joins.

    Assumption: branch code is mandatory for operational reporting, so when
    missing we emit UNKNOWN as an explicit placeholder rather than null.
    """
    if branch_code is None:
        return "UNKNOWN"
    cleaned = branch_code.strip().upper()
    return cleaned or "UNKNOWN"


def normalize_state_code(state_code: str | None) -> str | None:
    """Normalize state code to uppercase two-character value."""
    if state_code is None:
        return None
    cleaned = state_code.strip().upper()
    if len(cleaned) != 2:
        return None
    return cleaned


def normalize_zip_code(zip_code: str | None) -> str | None:
    """
    Normalize ZIP to five digits for regional analytics consistency.

    Assumption: for US lending reports, five-digit ZIP granularity is sufficient
    for branch performance and risk segmentation.
    """
    if zip_code is None:
        return None
    digits = re.sub(r"\D", "", zip_code)
    if len(digits) < 5:
        return None
    return digits[:5]


def transform(
    session,
    application_table: str = "RAW_ZONE.LOAN_APPLICATION_CLEANED",
    borrower_table: str = "CURATED_ZONE.BORROWER_360",
    branch_reference_table: str = "REFERENCE.BRANCH_REF",
):
    """
    Build loan_application_curated DataFrame.
    Reads cleaned applications, borrower enrichment data, and branch reference.

    Returns a Snowpark DataFrame — does not write to a table.
    """
    from snowflake.snowpark import functions as F
    from snowflake.snowpark.types import BooleanType, StringType

    logger.info("Starting loan_application_curated transformation.")

    applications = session.table(application_table)
    borrowers = session.table(borrower_table)
    branches = session.table(branch_reference_table)

    standardize_branch_udf = F.udf(
        standardize_branch_code,
        return_type=StringType(),
        input_types=[StringType()]
    )

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

    normalize_state_udf = F.udf(
        normalize_state_code,
        return_type=StringType(),
        input_types=[StringType()]
    )

    normalize_zip_udf = F.udf(
        normalize_zip_code,
        return_type=StringType(),
        input_types=[StringType()]
    )

    app = (
        applications
        .select(
            F.col("APPLICATION_ID"),
            F.col("CUSTOMER_ID"),
            standardize_branch_udf(F.col("BRANCH_CODE")).alias("APP_BRANCH_CODE"),
            F.col("LOAN_AMOUNT"),
            normalize_loan_type_udf(F.col("LOAN_TYPE")).alias("LOAN_TYPE"),
            F.col("APPLICATION_DATE"),
            normalize_state_udf(F.col("STATE_CODE")).alias("STATE_CODE"),
            normalize_zip_udf(F.col("ZIP_CODE")).alias("ZIP_CODE"),
            F.col("COLLATERAL_VALUE"),
        )
        .alias("app")
    )

    borrower = (
        borrowers
        .select(
            F.col("APPLICATION_ID").alias("BORROWER_APPLICATION_ID"),
            standardize_branch_udf(F.col("BRANCH_CODE_NORMALIZED")).alias("BORROWER_BRANCH_CODE"),
            F.col("BRANCH_NAME").alias("BORROWER_BRANCH_NAME"),
            F.col("REGION").alias("BORROWER_REGION"),
        )
        .alias("borrower")
    )

    branch_ref = (
        branches
        .filter(F.col("IS_ACTIVE") == F.lit(True))
        .select(
            standardize_branch_udf(F.col("BRANCH_CODE")).alias("REF_BRANCH_CODE"),
            F.col("BRANCH_NAME").alias("REF_BRANCH_NAME"),
            F.col("REGION").alias("REF_REGION"),
        )
        .alias("branch")
    )

    app_with_borrower = (
        app
        .join(
            borrower,
            app["APPLICATION_ID"] == borrower["BORROWER_APPLICATION_ID"],
            join_type="left"
        )
        .with_column(
            "ENRICHED_BRANCH_CODE",
            F.coalesce(F.col("APP_BRANCH_CODE"), F.col("BORROWER_BRANCH_CODE"), F.lit("UNKNOWN"))
        )
    )

    curated = (
        app_with_borrower.join(
            branch_ref,
            app_with_borrower["ENRICHED_BRANCH_CODE"] == branch_ref["REF_BRANCH_CODE"],
            join_type="left"
        )
        .select(
            F.col("APPLICATION_ID"),
            F.col("CUSTOMER_ID"),
            F.col("ENRICHED_BRANCH_CODE").alias("BRANCH_CODE"),
            F.coalesce(F.col("REF_BRANCH_NAME"), F.col("BORROWER_BRANCH_NAME")).alias("BRANCH_NAME"),
            F.coalesce(F.col("REF_REGION"), F.col("BORROWER_REGION")).alias("REGION"),
            F.col("LOAN_AMOUNT"),
            F.col("LOAN_TYPE"),
            F.col("APPLICATION_DATE"),
            F.col("STATE_CODE"),
            F.col("ZIP_CODE"),
            F.col("COLLATERAL_VALUE"),
            is_secured_udf(F.col("LOAN_TYPE")).alias("IS_SECURED"),
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
