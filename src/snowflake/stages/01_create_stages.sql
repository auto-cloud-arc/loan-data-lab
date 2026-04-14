-- ============================================================
-- Create Snowflake stages for Contoso Bank loan pipeline
-- ============================================================

USE DATABASE CONTOSO_LOAN_DB;

-- Internal stage for cleaned CSV files from C# data cleaner
CREATE STAGE IF NOT EXISTS RAW_ZONE.LOAN_CLEANED_STAGE
    FILE_FORMAT = (
        TYPE = CSV
        FIELD_OPTIONALLY_ENCLOSED_BY = '"'
        SKIP_HEADER = 1
        NULL_IF = ('', 'NULL', 'null')
        EMPTY_FIELD_AS_NULL = TRUE
    )
    COMMENT = 'Internal stage for cleaned loan CSV files';

-- Internal stage for QA exception reports (JSON)
CREATE STAGE IF NOT EXISTS QA_ZONE.QA_REPORT_STAGE
    FILE_FORMAT = (
        TYPE = JSON
        STRIP_OUTER_ARRAY = FALSE
    )
    COMMENT = 'Internal stage for JSON QA exception reports';

-- Internal stage for reference data loads
CREATE STAGE IF NOT EXISTS REFERENCE.REFERENCE_DATA_STAGE
    FILE_FORMAT = (
        TYPE = CSV
        FIELD_OPTIONALLY_ENCLOSED_BY = '"'
        SKIP_HEADER = 1
        NULL_IF = ('', 'NULL', 'null')
        EMPTY_FIELD_AS_NULL = TRUE
    )
    COMMENT = 'Internal stage for reference data CSV files';
