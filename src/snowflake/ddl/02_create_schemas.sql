-- ============================================================
-- Create schemas in CONTOSO_LOAN_DB
-- ============================================================

USE DATABASE CONTOSO_LOAN_DB;

-- Holds cleaned data loaded from the C# data cleaner output
CREATE SCHEMA IF NOT EXISTS RAW_ZONE
    COMMENT = 'Cleaned records from the C# data cleaner — ready for transformation';

-- Holds curated, enriched tables produced by Snowpark jobs
CREATE SCHEMA IF NOT EXISTS CURATED_ZONE
    COMMENT = 'Snowpark-transformed curated tables for analytics and reporting';

-- Holds data quality exception records and QA reports
CREATE SCHEMA IF NOT EXISTS QA_ZONE
    COMMENT = 'DQ exception records and validation reports';

-- Holds reference data (branches, loan types, state codes)
CREATE SCHEMA IF NOT EXISTS REFERENCE
    COMMENT = 'Reference and lookup tables used for enrichment';
