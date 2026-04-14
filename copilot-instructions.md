# Contoso Bank Loan Data Modernization Lab — Copilot Instructions

You are assisting engineers working on the **Contoso Bank Loan Data Modernization Lab**, a banking data pipeline that moves loan application data from Azure SQL Server through a C# data cleaner into Snowflake, where Snowpark transforms produce curated analytical tables validated by QA rules.

## Repository overview

| Directory | Purpose |
|-----------|---------|
| `src/data-cleaner-csharp/` | .NET 8 C# console app that cleans raw CSV loan extracts |
| `src/sqlserver/` | Azure SQL Server schema, seed data, stored procedures |
| `src/snowflake/` | Snowflake DDL, stages, procedures, RBAC roles |
| `src/snowpark/` | Python Snowpark transforms and reconciliation |
| `src/qa-validator/` | Python QA validation rules, runners, reports |
| `infra/bicep/` | Azure Bicep IaC for SQL Server, Key Vault, Storage |
| `sample-data/` | Raw, cleaned, and expected data for testing |
| `docs/` | Architecture, data contracts, onboarding, domain story |
| `.copilot/` | Prompt files and agent definitions for this repo |

## Coding conventions

### C# (.NET 8)
- Use `nullable enable` and `ImplicitUsings`
- Prefer records for immutable models, classes for services
- Use interfaces for all services and parsers (`ILoanApplicationParser`, etc.)
- Log using `ILogger<T>` — never log raw SSN, full name, DOB, or email
- Use structured logging: `_logger.LogInformation("Processing {AppId}", app.ApplicationId)`
- Validate inputs at the service boundary; return `ValidationResult` objects, do not throw

### Python
- Python 3.11+, type hints on all function signatures
- Use `from __future__ import annotations` for forward references
- Snowpark: never hard-code credentials — use environment variables or `Session.builder.configs()`
- Use `@dataclass` for value objects
- Keep Snowpark-specific code isolated from pure Python logic (testability)
- Run `pytest` from the relevant `tests/` directory

### SQL
- Use explicit `JOIN` (no implicit comma joins)
- Use CTEs for readability
- Snake_case for all SQL object names
- Hash PII at the source; do not load raw SSNs, emails, or DOBs into Snowflake

## Security rules

- **Never commit** connection strings, passwords, API keys, or SAS tokens
- Azure credentials → Azure Key Vault (reference via `@Microsoft.KeyVault(...)` in Bicep)
- Snowflake credentials → environment variables (`SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, etc.)
- Log masking: PII fields (SSN, name, email, DOB) must be redacted before writing to any log
- Input validation required for all CSV parsing entry points

## Data domain glossary

| Term | Definition |
|------|-----------|
| `application_id` | Unique identifier for a loan application (format: `APP-NNN`) |
| `customer_id` | Unique customer identifier (format: `CUST-NNN`) |
| `branch_code` | Branch originating the loan (format: `BR-NN`) |
| `loan_type` | One of: MORTGAGE, AUTO, PERSONAL, HELOC, BUSINESS |
| `secured loan` | MORTGAGE, AUTO, HELOC — requires collateral |
| `ltv` | Loan-to-Value ratio = loan_amount / collateral_value |
| `risk_tier` | LOW / MEDIUM / HIGH based on LTV and loan type |
| `dq_exception` | A data quality rule violation recorded in the QA report |
| `borrower_360` | Curated Snowflake table joining application, borrower, and branch data |

## When generating new code

1. Check existing patterns in the relevant `src/` directory first
2. Match the naming conventions for the language (PascalCase C#, snake_case Python/SQL)
3. Add tests alongside any new logic
4. Update `docs/data-contracts.md` if you add new fields or tables
5. Never introduce new external dependencies without reviewing security
