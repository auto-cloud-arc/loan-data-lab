-- ============================================================
-- Snowflake Stored Procedure: sp_load_collateral_summary
-- Aggregates collateral and loan data by loan type and region
-- for risk reporting in CURATED_ZONE.COLLATERAL_SUMMARY.
-- ============================================================

USE DATABASE CONTOSO_LOAN_DB;

CREATE OR REPLACE PROCEDURE CURATED_ZONE.sp_load_collateral_summary()
RETURNS VARIANT
LANGUAGE PYTHON
RUNTIME_VERSION = '3.11'
PACKAGES = ('snowflake-snowpark-python')
HANDLER = 'main'
COMMENT = 'Aggregates collateral data by loan type and region for risk reporting'
AS
$$
import json
from datetime import datetime, date
from snowflake.snowpark import Session
from snowflake.snowpark import functions as F


def main(session: Session) -> str:
    start_time = datetime.utcnow()
    today = date.today().isoformat()

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
        .with_column("SUMMARY_DATE", F.to_date(F.lit(today)))
        .with_column("SUMMARIZED_AT", F.current_timestamp())
    )

    row_count = summary.count()
    summary.write.mode("overwrite").save_as_table("CURATED_ZONE.COLLATERAL_SUMMARY")

    return json.dumps({
        "status": "success",
        "rows_written": row_count,
        "summary_date": today,
        "duration_seconds": (datetime.utcnow() - start_time).total_seconds()
    })
$$;
