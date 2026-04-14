# Architecture Overview — Contoso Bank Loan Data Modernization Lab

## Overview

The Contoso Bank Loan Data Modernization Lab implements a four-stage data pipeline that moves loan application data from a legacy Azure SQL Server system into a modern Snowflake data platform, with data quality enforcement at every stage.

```
┌─────────────────────┐
│  Azure SQL Server   │  Legacy source: raw loan applications,
│  (loan_db)          │  customer data, collateral records,
│                     │  and branch reference tables
└────────┬────────────┘
         │  CSV extract (daily)
         ▼
┌─────────────────────┐
│  C# Data Cleaner    │  .NET 8 console app:
│  (ContosoLoan       │  • Parse CSV with CsvHelper
│   Cleaner)          │  • Normalize phone, address, dates
│                     │  • Validate business rules
│                     │  • Emit cleaned CSV + exception report
└────────┬────────────┘
         │  Cleaned CSV
         ▼
┌─────────────────────┐
│  Snowflake          │  Modern cloud data warehouse:
│  (CONTOSO_LOAN_DB)  │  • RAW_ZONE  → ingest cleaned records
│                     │  • CURATED_ZONE → Snowpark transforms
│                     │  • QA_ZONE  → exception records
│                     │  • REFERENCE → branch lookup tables
└────────┬────────────┘
         │  Snowpark DataFrame transforms
         ▼
┌─────────────────────┐
│  QA Validator       │  Python validation engine:
│  (pandas + rules)   │  • Null checks, date rules
│                     │  • Business rules (collateral, LTV)
│                     │  • Reconciliation (source vs target)
│                     │  • JSON + Markdown DQ reports
└─────────────────────┘
```

## Component Details

### Azure SQL Server (Legacy Source)

- **Purpose**: Holds raw loan intake data as it arrives from branch systems
- **Key tables**: `loan_application_raw`, `customer_raw`, `collateral_raw`, `branch_reference`
- **Known issues**: Inconsistent date formats, lowercase state codes, missing customer IDs, duplicate customers across loads
- **Stored procedures**: `usp_extract_daily_applications`, `usp_flag_duplicate_customers`

### C# Data Cleaner (`src/data-cleaner-csharp/`)

- **Language**: C# .NET 8 console application
- **Dependencies**: CsvHelper 33, Serilog, Microsoft.Extensions.Logging
- **Inputs**: Raw CSV extract from Azure SQL
- **Outputs**: Cleaned CSV (passing records), JSON exception report (failing records)
- **Key classes**:
  - `LoanApplicationParser` — reads CSV rows into `LoanApplication` model objects
  - `AddressNormalizer` — uppercases state codes, normalizes ZIP to 5 digits
  - `PhoneNormalizer` — standardizes phone to `(NNN) NNN-NNNN` format
  - `DateNormalizer` — parses multiple date formats into ISO 8601 (`yyyy-MM-dd`)
  - `LoanApplicationValidator` — applies business rules and returns `ValidationResult` objects
- **PII handling**: SSN, name, and email fields are redacted as `***REDACTED***` in exception reports

### Snowflake Data Warehouse (`src/snowflake/`)

- **Database**: `CONTOSO_LOAN_DB`
- **Schemas**:
  - `RAW_ZONE` — cleaned records loaded from C# cleaner output
  - `CURATED_ZONE` — transformed tables produced by Snowpark jobs
  - `QA_ZONE` — data quality exception records
  - `REFERENCE` — branch and lookup reference tables
- **Warehouses**: `CONTOSO_TRANSFORM_WH` (ETL), `CONTOSO_REPORTING_WH` (analytics)
- **RBAC roles**: `CONTOSO_ADMIN`, `CONTOSO_DATA_ENGINEER`, `CONTOSO_ANALYST`, `CONTOSO_QA`

### Snowpark Transforms (`src/snowpark/`)

- **Language**: Python 3.11 with `snowflake-snowpark-python`
- **Design pattern**: Pure helper functions (testable without Snowflake) + thin Snowpark orchestration layer
- **Key transforms**:
  - `borrower_360_transform.py` — joins application + branch data, standardizes branch codes, computes LTV risk tier
  - `loan_application_curated_transform.py` — enriches applications with reference data, standardizes fields
  - `collateral_summary_transform.py` — aggregates collateral by type and region
- **Reconciliation**: `source_target_reconciliation.py` compares source and target row counts with configurable tolerance

### QA Validator (`src/qa-validator/`)

- **Language**: Python 3.11, pandas
- **Rule categories**:
  - `null_check_rules.py` — required field presence checks
  - `date_validation_rules.py` — date format and future-date checks
  - `business_rules.py` — loan amount, collateral, branch code checks
  - `reconciliation_rules.py` — source-to-target row count reconciliation
- **Runner**: `run_validations.py` — CLI entry point, loads CSV, runs all rules, emits reports
- **Reports**: JSON (machine-readable) and Markdown (human-readable) in the specified output directory

## Infrastructure (`infra/bicep/`)

| Module | Resources |
|--------|-----------|
| `main.bicep` | Top-level orchestrator; wires all modules together |
| `sql.bicep` | Azure SQL Server + `loan_db` database; stores connection string in Key Vault |
| `keyvault.bicep` | Azure Key Vault for secrets management |
| `storage.bicep` | Azure Blob Storage for raw CSV extracts |

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Data cleaning | C# / .NET | 8.0 |
| CSV parsing | CsvHelper | 33.x |
| Logging (C#) | Serilog | 8.x |
| Legacy database | Azure SQL Server | 2022 |
| Cloud warehouse | Snowflake | Current |
| Transformation | Snowpark Python | 1.x |
| QA validation | Python / pandas | 3.11 / 2.x |
| Infrastructure | Azure Bicep | Current |
| CI/CD | GitHub Actions | Current |
| Unit testing (.NET) | xUnit | 2.7 |
| Unit testing (Python) | pytest | 8.x |

## Security Considerations

1. **PII Handling**: SSN, full name, date of birth, and email fields are hashed at the Azure SQL boundary. The C# cleaner further redacts these fields in exception reports.
2. **Secrets Management**: All connection strings and credentials are stored in Azure Key Vault. Bicep templates reference secrets via `@Microsoft.KeyVault(...)` annotations. Snowflake credentials use environment variables.
3. **Logging**: Structured logging in C# and Python never logs raw PII values. Phone numbers and emails are masked in warning messages.
4. **RBAC**: Snowflake RBAC enforces least-privilege access. Analysts cannot write to `RAW_ZONE`; QA engineers have read-only access to `QA_ZONE`.
5. **CI/CD**: GitHub Actions secrets (`AZURE_CREDENTIALS`, `AZURE_SQL_CONNECTION_STRING`) are scoped to environment-specific deployments.
