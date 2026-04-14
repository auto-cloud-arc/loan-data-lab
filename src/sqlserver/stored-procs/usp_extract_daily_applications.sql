-- ============================================================
-- Stored Procedure: usp_extract_daily_applications
-- Extracts loan applications submitted in the last N days
-- for delivery to the C# data cleaner as a daily CSV extract.
-- ============================================================

USE loan_db;
GO

CREATE OR ALTER PROCEDURE dbo.usp_extract_daily_applications
    @lookback_days INT = 1,
    @as_of_date    DATE = NULL
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @cutoff_date DATE = ISNULL(@as_of_date, CAST(GETUTCDATE() AS DATE));

    SELECT
        la.application_id,
        la.customer_id,
        la.branch_code,
        la.loan_amount,
        la.loan_type,
        la.application_date,
        la.first_name,
        la.last_name,
        la.ssn_hash,
        la.phone_number,
        la.address_line1,
        la.city,
        la.state_code,
        la.zip_code,
        la.email_hash,
        la.collateral_value,
        la.source_system,
        la.load_timestamp
    FROM dbo.loan_application_raw AS la
    WHERE
        la.load_timestamp >= DATEADD(DAY, -@lookback_days, @cutoff_date)
        AND la.load_timestamp < DATEADD(DAY, 1, @cutoff_date)
    ORDER BY la.load_timestamp ASC, la.application_id ASC;

    -- Return row count metadata for reconciliation
    SELECT
        @lookback_days      AS lookback_days,
        @cutoff_date        AS cutoff_date,
        COUNT(*)            AS extracted_row_count
    FROM dbo.loan_application_raw AS la
    WHERE
        la.load_timestamp >= DATEADD(DAY, -@lookback_days, @cutoff_date)
        AND la.load_timestamp < DATEADD(DAY, 1, @cutoff_date);
END;
GO
