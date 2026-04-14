# Contoso Bank Loan Data Modernization Lab

[![CI](https://github.com/auto-cloud-arc/loan-data-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/auto-cloud-arc/loan-data-lab/actions/workflows/ci.yml)
[![Data Quality](https://github.com/auto-cloud-arc/loan-data-lab/actions/workflows/validate-data-quality.yml/badge.svg)](https://github.com/auto-cloud-arc/loan-data-lab/actions/workflows/validate-data-quality.yml)

A GitHub Copilot workshop repository built around **modernizing Contoso Bank's loan onboarding and data quality pipeline** from Azure SQL Server to Snowflake.

## Business story

Contoso Bank processes daily loan application extracts with real-world data quality issues: nulls, malformed phone numbers, invalid state codes, duplicate customer IDs, and future application dates. This repo demonstrates the full journey:

```
Azure SQL Server (legacy)
        ↓
  C# Data Cleaner  (normalize, validate, report exceptions)
        ↓
   Snowflake / Snowpark  (transform into curated tables)
        ↓
   QA Validator  (enforce business rules, produce DQ report)
```

## Repository structure

```
.
├── .github/           # CI/CD workflows, issue templates, PR template
├── .copilot/          # Prompt files and agent definitions for workshop
├── docs/              # Architecture, domain story, data contracts, demo script
├── infra/bicep/       # Azure Bicep IaC (SQL Server, Key Vault, Storage)
├── src/
│   ├── data-cleaner-csharp/   # .NET 8 C# console app
│   ├── sqlserver/             # Azure SQL schema, seed, stored procs
│   ├── snowflake/             # Snowflake DDL, stages, procedures, roles
│   ├── snowpark/              # Python Snowpark transforms + tests
│   └── qa-validator/          # Python QA validation rules + tests
├── sample-data/       # Raw, cleaned, and expected data files
└── copilot-instructions.md
```

## Quick start

### C# Data Cleaner

```bash
cd src/data-cleaner-csharp
dotnet restore ContosoLoanCleaner.sln
dotnet build ContosoLoanCleaner.sln
dotnet run --project ContosoLoanCleaner -- ../../sample-data/raw/loan_applications_raw.csv ../../sample-data/cleaned/loan_applications_cleaned.csv
dotnet test ContosoLoanCleaner.sln
```

### QA Validator

```bash
pip install pandas pytest
pytest src/qa-validator/tests/ -v
python src/qa-validator/runners/run_validations.py \
  --input sample-data/cleaned/loan_applications_cleaned.csv \
  --report-dir reports/
```

#### QA Rule Coverage and Report Outputs

The QA validator enforces banking-focused rules for curated loan data quality:

- Null business keys: `application_id`, `customer_id`, `branch_code`
- Invalid/future application dates
- Negative or non-numeric loan amounts
- Missing collateral for secured products (`MORTGAGE`, `AUTO`, `HELOC`)
- Source-to-target row count reconciliation with configurable tolerance

Implementation sources:

- Null key checks: [src/qa-validator/rules/null_check_rules.py](src/qa-validator/rules/null_check_rules.py)
- Date checks: [src/qa-validator/rules/date_validation_rules.py](src/qa-validator/rules/date_validation_rules.py)
- Business checks: [src/qa-validator/rules/business_rules.py](src/qa-validator/rules/business_rules.py)
- Reconciliation checks: [src/qa-validator/rules/reconciliation_rules.py](src/qa-validator/rules/reconciliation_rules.py)
- Report writers (JSON + Markdown): [src/qa-validator/reports/report_generator.py](src/qa-validator/reports/report_generator.py)
- Validation runner orchestration and CLI args: [src/qa-validator/runners/run_validations.py](src/qa-validator/runners/run_validations.py)

Optional reconciliation arguments:

```bash
python src/qa-validator/runners/run_validations.py \
     --input sample-data/cleaned/loan_applications_cleaned.csv \
     --report-dir reports/ \
     --source-count 10 \
     --target-count 9 \
     --reconciliation-table loan_application_curated \
     --reconciliation-tolerance 0.01
```

Generated outputs:

- `qa_report_YYYYMMDD_HHMMSS.json`: structured machine-readable DQ report
- `qa_report_YYYYMMDD_HHMMSS.md`: human-readable validation summary

Exit behavior:

- Exit code `0`: no critical validation failures and reconciliation passed
- Exit code `1`: critical validation failures and/or reconciliation failure

### Snowpark Tests (local, no Snowflake required)

```bash
pip install pytest pytest-mock
pytest src/snowpark/tests/ -v
```

## Workshop demo steps

1. **Onboard** — Ask Copilot to explain the architecture and data flow
2. **Plan Mode** — Use Copilot Plan Mode to design the borrower intake workflow
3. **C# generation** — Generate the data cleaning console app
4. **Refactor** — Improve the generated code with Copilot suggestions
5. **Unit testing** — Generate xUnit and pytest test suites
6. **Azure SQL** — Seed and query the legacy source tables
7. **Snowpark** — Write and run transformation jobs
8. **QA Validator** — Create and run validation rules
9. **Debug** — Trace a failing pipeline stage with Copilot
10. **Agents** — Use custom agents and prompts from `.copilot/`

See [docs/demo-script.md](docs/demo-script.md) for the full step-by-step guide.

## Documentation

- [Architecture Overview](docs/architecture.md)
- [Domain Story](docs/domain-story.md)
- [Data Contracts](docs/data-contracts.md)
- [Onboarding Guide](docs/onboarding-guide.md)
- [Azure Deployment Runbook](docs/azure-deployment-runbook.md)
- [Demo Script](docs/demo-script.md)

## Technology stack

| Component | Technology |
|-----------|-----------|
| Data cleaning | C# .NET 8, CsvHelper, Serilog |
| Legacy source | Azure SQL Server |
| Modern target | Snowflake on Azure |
| Transformation | Snowpark Python |
| QA validation | Python, pandas |
| Infrastructure | Azure Bicep |
| CI/CD | GitHub Actions |
| Testing | xUnit (.NET), pytest (Python) |
