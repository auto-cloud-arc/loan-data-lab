-- ============================================================
-- Stored Procedure: usp_flag_duplicate_customers
-- Identifies customers appearing more than once in customer_raw
-- based on ssn_hash, indicating duplicate intake records.
-- ============================================================

USE loan_db;
GO

CREATE OR ALTER PROCEDURE dbo.usp_flag_duplicate_customers
AS
BEGIN
    SET NOCOUNT ON;

    WITH duplicate_customers AS (
        SELECT
            ssn_hash,
            COUNT(DISTINCT customer_id) AS distinct_customer_id_count,
            COUNT(*)                    AS total_record_count,
            MIN(customer_id)            AS first_customer_id,
            MAX(customer_id)            AS last_customer_id,
            MIN(load_timestamp)         AS first_load_timestamp,
            MAX(load_timestamp)         AS last_load_timestamp
        FROM dbo.customer_raw
        WHERE ssn_hash IS NOT NULL
        GROUP BY ssn_hash
        HAVING COUNT(*) > 1
    )
    SELECT
        dc.ssn_hash,
        dc.distinct_customer_id_count,
        dc.total_record_count,
        dc.first_customer_id,
        dc.last_customer_id,
        dc.first_load_timestamp,
        dc.last_load_timestamp,
        -- List all customer_ids sharing this SSN hash
        STRING_AGG(cr.customer_id, ', ') WITHIN GROUP (ORDER BY cr.customer_id) AS all_customer_ids
    FROM duplicate_customers AS dc
    INNER JOIN dbo.customer_raw AS cr
        ON dc.ssn_hash = cr.ssn_hash
    GROUP BY
        dc.ssn_hash,
        dc.distinct_customer_id_count,
        dc.total_record_count,
        dc.first_customer_id,
        dc.last_customer_id,
        dc.first_load_timestamp,
        dc.last_load_timestamp
    ORDER BY dc.total_record_count DESC;
END;
GO
