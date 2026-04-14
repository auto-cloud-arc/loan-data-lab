# Data Contracts — Contoso Bank Loan Data Pipeline

This document defines the canonical schemas for all data entities flowing through the pipeline.
All downstream consumers must treat these as the authoritative contracts.

---

## 1. `loan_application_raw` (Azure SQL Server — source)

Table: `dbo.loan_application_raw`

| Field | SQL Type | Nullable | Description |
|-------|----------|----------|-------------|
| `application_id` | `NVARCHAR(20)` | NO | Unique application identifier. Format: `APP-NNN`. Primary key. |
| `customer_id` | `NVARCHAR(20)` | YES | Customer identifier. Format: `CUST-NNN`. Nullable in legacy data. |
| `branch_code` | `NVARCHAR(10)` | NO | Originating branch code. Format: `BR-NN`. |
| `loan_amount` | `DECIMAL(18,2)` | NO | Requested loan amount in USD. Must be positive after cleaning. |
| `loan_type` | `NVARCHAR(20)` | NO | One of: `MORTGAGE`, `AUTO`, `PERSONAL`, `HELOC`, `BUSINESS`. |
| `application_date` | `DATE` | YES | Date the application was submitted. Cannot be future-dated. |
| `first_name` | `NVARCHAR(100)` | YES | Applicant first name. PII — hashed before Snowflake load. |
| `last_name` | `NVARCHAR(100)` | YES | Applicant last name. PII — hashed before Snowflake load. |
| `ssn_hash` | `NVARCHAR(64)` | YES | SHA-256 hash of the SSN. Never store raw SSN. |
| `phone_number` | `NVARCHAR(20)` | YES | Raw phone number. Normalized to `(NNN) NNN-NNNN` by cleaner. |
| `address_line1` | `NVARCHAR(200)` | YES | Street address line 1. |
| `city` | `NVARCHAR(100)` | YES | City name. |
| `state_code` | `NCHAR(2)` | YES | Two-letter US state code. Normalized to uppercase. |
| `zip_code` | `NVARCHAR(10)` | YES | ZIP code. Normalized to 5-digit format. |
| `email_hash` | `NVARCHAR(64)` | YES | SHA-256 hash of the email address. Never store raw email. |
| `collateral_value` | `DECIMAL(18,2)` | YES | Appraised collateral value in USD. Required for secured loan types. |
| `source_system` | `NVARCHAR(50)` | YES | Originating system name, e.g. `BRANCH_INTAKE_v2`. |
| `load_timestamp` | `DATETIME2` | NO | UTC timestamp when the record was loaded. Default: `GETUTCDATE()`. |

---

## 2. `borrower_360` (Snowflake — `CURATED_ZONE`)

Table: `CONTOSO_LOAN_DB.CURATED_ZONE.BORROWER_360`

| Field | Snowflake Type | Nullable | Description |
|-------|---------------|----------|-------------|
| `application_id` | `VARCHAR(20)` | NO | Unique application identifier. |
| `customer_id` | `VARCHAR(20)` | YES | Customer identifier. |
| `first_name` | `VARCHAR(100)` | YES | Applicant first name (hashed/redacted in QA reports). |
| `last_name` | `VARCHAR(100)` | YES | Applicant last name (hashed/redacted in QA reports). |
| `loan_amount` | `NUMBER(18,2)` | NO | Requested loan amount in USD. |
| `loan_type` | `VARCHAR(20)` | NO | Normalized loan type (uppercase). |
| `collateral_value` | `NUMBER(18,2)` | YES | Collateral value in USD. |
| `application_date` | `DATE` | YES | Application submission date (ISO 8601). |
| `branch_code_normalized` | `VARCHAR(10)` | YES | Branch code standardized to uppercase (e.g. `BR-01`). |
| `branch_name` | `VARCHAR(200)` | YES | Human-readable branch name from `REFERENCE.BRANCH_REF`. |
| `region` | `VARCHAR(100)` | YES | Geographic region of the originating branch. |
| `risk_tier` | `VARCHAR(10)` | YES | Computed risk tier: `LOW`, `MEDIUM`, or `HIGH`. |
| `transformed_at` | `TIMESTAMP_NTZ` | NO | UTC timestamp when the Snowpark transform ran. |

**Business rules**:
- `risk_tier` is computed as: `loan_amount / collateral_value` (LTV). LTV < 0.80 → LOW, 0.80–0.90 → MEDIUM, > 0.90 → HIGH. Unsecured loans always HIGH.
- `branch_code_normalized` is always uppercase, trimmed.

---

## 3. `loan_application_curated` (Snowflake — `CURATED_ZONE`)

Table: `CONTOSO_LOAN_DB.CURATED_ZONE.LOAN_APPLICATION_CURATED`

| Field | Snowflake Type | Nullable | Description |
|-------|---------------|----------|-------------|
| `application_id` | `VARCHAR(20)` | NO | Unique application identifier. |
| `customer_id` | `VARCHAR(20)` | YES | Customer identifier. |
| `branch_code` | `VARCHAR(10)` | NO | Normalized branch code. |
| `branch_name` | `VARCHAR(200)` | YES | Branch display name. |
| `region` | `VARCHAR(100)` | YES | Branch region. |
| `loan_amount` | `NUMBER(18,2)` | NO | Loan amount in USD. |
| `loan_type` | `VARCHAR(20)` | NO | Loan type (normalized). |
| `application_date` | `DATE` | YES | Application date. |
| `state_code` | `CHAR(2)` | YES | Applicant state code (uppercase). |
| `zip_code` | `VARCHAR(5)` | YES | 5-digit ZIP code. |
| `collateral_value` | `NUMBER(18,2)` | YES | Collateral value in USD. |
| `is_secured` | `BOOLEAN` | NO | True if loan type is MORTGAGE, AUTO, or HELOC. |
| `curated_at` | `TIMESTAMP_NTZ` | NO | UTC timestamp of Snowpark transform execution. |

---

## 4. `collateral_summary` (Snowflake — `CURATED_ZONE`)

Table: `CONTOSO_LOAN_DB.CURATED_ZONE.COLLATERAL_SUMMARY`

| Field | Snowflake Type | Nullable | Description |
|-------|---------------|----------|-------------|
| `loan_type` | `VARCHAR(20)` | NO | Loan type group. |
| `region` | `VARCHAR(100)` | YES | Geographic region. |
| `application_count` | `NUMBER(10,0)` | NO | Number of applications in the group. |
| `total_loan_amount` | `NUMBER(18,2)` | NO | Sum of loan amounts in USD. |
| `total_collateral_value` | `NUMBER(18,2)` | YES | Sum of collateral values in USD. |
| `avg_ltv` | `NUMBER(8,4)` | YES | Average LTV ratio for the group. |
| `summary_date` | `DATE` | NO | The processing date for this summary row. |
| `summarized_at` | `TIMESTAMP_NTZ` | NO | UTC timestamp of Snowpark transform execution. |

---

## 5. `dq_exception_report` (Schema — JSON report output)

Produced by `src/qa-validator/runners/run_validations.py` and stored as a JSON artifact.

```json
{
  "generated_at": "2024-04-15T08:30:00.000000",
  "input_file": "sample-data/cleaned/loan_applications_cleaned.csv",
  "total_records": 100,
  "total_failures": 3,
  "pass_rate": "97.0%",
  "failures": [
    {
      "row_index": 4,
      "field": "application_date",
      "rule_name": "application_date_not_future",
      "actual_value": "2099-04-01",
      "message": "Application date '2099-04-01' is in the future.",
      "severity": "error"
    },
    {
      "row_index": 6,
      "field": "loan_amount",
      "rule_name": "positive_loan_amount",
      "actual_value": "-500.0",
      "message": "Loan amount must be greater than zero. Got: -500.0",
      "severity": "critical"
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `generated_at` | ISO 8601 string | UTC timestamp of report generation |
| `input_file` | string | Path to the input CSV file |
| `total_records` | integer | Total number of rows evaluated |
| `total_failures` | integer | Total number of `ValidationFailure` objects |
| `pass_rate` | string | Percentage of records with no failures |
| `failures[].row_index` | integer | Zero-based row index in the DataFrame |
| `failures[].field` | string | Column name that failed validation |
| `failures[].rule_name` | string | Identifier of the rule that was violated |
| `failures[].actual_value` | string | The actual field value (PII-safe) |
| `failures[].message` | string | Human-readable failure description |
| `failures[].severity` | string | `critical`, `error`, `warning`, or `info` |
