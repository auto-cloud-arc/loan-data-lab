-- ============================================================
-- Create Contoso Bank Snowflake database and warehouses
-- ============================================================

CREATE DATABASE IF NOT EXISTS CONTOSO_LOAN_DB
    DATA_RETENTION_TIME_IN_DAYS = 7
    COMMENT = 'Contoso Bank Loan Data Platform';

CREATE WAREHOUSE IF NOT EXISTS CONTOSO_TRANSFORM_WH
    WAREHOUSE_SIZE = 'X-SMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    COMMENT = 'Warehouse for Snowpark transformation jobs';

CREATE WAREHOUSE IF NOT EXISTS CONTOSO_REPORTING_WH
    WAREHOUSE_SIZE = 'X-SMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    COMMENT = 'Warehouse for analytics and reporting';

USE DATABASE CONTOSO_LOAN_DB;
