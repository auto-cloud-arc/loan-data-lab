"""
Snowpark transformation: collateral_summary

Aggregates collateral and loan data by loan type and region,
computing average LTV ratios for risk reporting.
"""

from __future__ import annotations
from datetime import date
import logging

logger = logging.getLogger(__name__)


def compute_ltv(loan_amount: float, collateral_value: float | None) -> float | None:
    """Compute loan-to-value ratio. Returns None if collateral is zero or missing."""
    if collateral_value is None or float(collateral_value) <= 0:
        return None
    return float(loan_amount) / float(collateral_value)


def transform(session, summary_date: date | None = None):
    """
    Build collateral_summary DataFrame.
    Reads from CURATED_ZONE.LOAN_APPLICATION_CURATED (secured loans only).
    Groups by LOAN_TYPE and REGION.

    Returns a Snowpark DataFrame — does not write to a table.
    """
    from snowflake.snowpark import functions as F

    today = summary_date or date.today()
    logger.info("Starting collateral_summary transformation for date %s.", today)

    curated = session.table("CURATED_ZONE.LOAN_APPLICATION_CURATED")

    summary = (
        curated
        .filter(F.col("IS_SECURED") == True)
        .group_by("LOAN_TYPE", "REGION")
        .agg(
            F.count("APPLICATION_ID").alias("APPLICATION_COUNT"),
            F.sum("LOAN_AMOUNT").alias("TOTAL_LOAN_AMOUNT"),
            F.sum("COLLATERAL_VALUE").alias("TOTAL_COLLATERAL_VALUE"),
            F.avg(
                F.iff(
                    F.col("COLLATERAL_VALUE") > 0,
                    F.col("LOAN_AMOUNT") / F.col("COLLATERAL_VALUE"),
                    F.lit(None)
                )
            ).alias("AVG_LTV")
        )
        .with_column("SUMMARY_DATE", F.to_date(F.lit(str(today))))
        .with_column("SUMMARIZED_AT", F.current_timestamp())
    )

    logger.info("collateral_summary transformation complete.")
    return summary


def run(session, target_table: str = "CURATED_ZONE.COLLATERAL_SUMMARY",
        summary_date: date | None = None) -> None:
    """Execute the transformation and write to the target table."""
    df = transform(session, summary_date=summary_date)
    row_count = df.count()
    df.write.mode("overwrite").save_as_table(target_table)
    logger.info("Written %d rows to %s.", row_count, target_table)
