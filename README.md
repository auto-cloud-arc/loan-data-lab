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
dotnet run --project ContosoLoanCleaner -- \
  ../../sample-data/raw/loan_applications_raw.csv \
  ../../sample-data/cleaned/loan_applications_cleaned.csv
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
