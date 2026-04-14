-- ============================================================
-- Contoso Bank Loan Database — Schema Creation
-- Target: Azure SQL Server (loan_db)
-- ============================================================

USE loan_db;
GO

-- Raw loan applications arriving from branch intake systems
CREATE TABLE dbo.loan_application_raw (
    application_id      NVARCHAR(20)    NOT NULL,
    customer_id         NVARCHAR(20)    NULL,
    branch_code         NVARCHAR(10)    NOT NULL,
    loan_amount         DECIMAL(18,2)   NOT NULL,
    loan_type           NVARCHAR(20)    NOT NULL,
    application_date    DATE            NULL,
    first_name          NVARCHAR(100)   NULL,
    last_name           NVARCHAR(100)   NULL,
    ssn_hash            NVARCHAR(64)    NULL,
    phone_number        NVARCHAR(20)    NULL,
    address_line1       NVARCHAR(200)   NULL,
    city                NVARCHAR(100)   NULL,
    state_code          NCHAR(2)        NULL,
    zip_code            NVARCHAR(10)    NULL,
    email_hash          NVARCHAR(64)    NULL,
    collateral_value    DECIMAL(18,2)   NULL,
    source_system       NVARCHAR(50)    NULL,
    load_timestamp      DATETIME2       NOT NULL DEFAULT GETUTCDATE(),
    CONSTRAINT PK_loan_application_raw PRIMARY KEY (application_id)
);
GO

-- Raw customer records — may contain duplicates across loads
CREATE TABLE dbo.customer_raw (
    customer_id         NVARCHAR(20)    NOT NULL,
    first_name          NVARCHAR(100)   NULL,
    last_name           NVARCHAR(100)   NULL,
    date_of_birth       DATE            NULL,
    ssn_hash            NVARCHAR(64)    NULL,
    email_hash          NVARCHAR(64)    NULL,
    phone_number        NVARCHAR(20)    NULL,
    address_line1       NVARCHAR(200)   NULL,
    city                NVARCHAR(100)   NULL,
    state_code          NCHAR(2)        NULL,
    zip_code            NVARCHAR(10)    NULL,
    credit_score        SMALLINT        NULL,
    load_timestamp      DATETIME2       NOT NULL DEFAULT GETUTCDATE(),
    CONSTRAINT PK_customer_raw PRIMARY KEY (customer_id, load_timestamp)
);
GO

-- Collateral details linked to loan applications
CREATE TABLE dbo.collateral_raw (
    collateral_id       NVARCHAR(20)    NOT NULL,
    application_id      NVARCHAR(20)    NOT NULL,
    collateral_type     NVARCHAR(50)    NULL,
    collateral_value    DECIMAL(18,2)   NULL,
    appraisal_date      DATE            NULL,
    appraisal_company   NVARCHAR(200)   NULL,
    load_timestamp      DATETIME2       NOT NULL DEFAULT GETUTCDATE(),
    CONSTRAINT PK_collateral_raw PRIMARY KEY (collateral_id)
);
GO

-- Branch reference data — used for validation and enrichment
CREATE TABLE dbo.branch_reference (
    branch_code         NVARCHAR(10)    NOT NULL,
    branch_name         NVARCHAR(200)   NOT NULL,
    region              NVARCHAR(100)   NOT NULL,
    state_code          NCHAR(2)        NOT NULL,
    is_active           BIT             NOT NULL DEFAULT 1,
    CONSTRAINT PK_branch_reference PRIMARY KEY (branch_code)
);
GO
