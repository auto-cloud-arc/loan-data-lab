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

## Embedded PRD template guidance

Use this section when the user asks to create, refine, or extend a product requirements document. Treat it as a reusable template that should be adapted to the product, workflow, or feature under discussion.

### PRD purpose

- Define the problem being solved, the intended users, and the expected outcomes.
- Make scope, constraints, and success criteria explicit before implementation starts.
- Produce a document that is specific enough to guide design, engineering, testing, and review.

### Recommended PRD structure

Include these sections unless the user asks for a shorter format:

1. Document information
2. Executive summary
3. Problem statement
4. Goals and objectives
5. Scope
6. User stories or use cases
7. Functional requirements
8. Non-functional requirements
9. Assumptions and dependencies
10. Success criteria or KPIs
11. Milestones or implementation phases
12. Implementation guidance
13. Testing and validation approach
14. Risks, constraints, or troubleshooting notes

### Content expectations

- Write requirements in concrete, testable language.
- Separate in-scope and out-of-scope items clearly.
- Distinguish user-facing behavior from implementation guidance.
- Prefer concise tables for structured requirements, dependencies, or package constraints.
- Include IDs for functional requirements when traceability matters.
- Add environment, framework, or package version constraints only when they materially affect delivery.

### Functional requirement guidance

- Express each requirement as an observable behavior.
- Prefer statements like “The application shall...” or similarly testable wording.
- Cover normal flows, validation rules, error handling, and repeat or continuation flows where applicable.
- Include data inputs, outputs, and integration points when the system interacts with external services or files.

### Non-functional requirement guidance

- Cover performance, usability, reliability, security, maintainability, and compatibility as relevant.
- Keep non-functional requirements measurable where possible.
- Only include categories that materially affect the product or delivery risk.

### Implementation guidance rules

- Keep implementation guidance aligned with the target stack and repository conventions.
- Separate hard constraints from optional recommendations.
- Avoid prescribing architecture or tooling that the user did not ask for.
- If language-specific constraints are important, reference the conventions in this instructions file.

### Testing guidance rules

- Include the required test levels for the task: unit, integration, end-to-end, validation, or manual acceptance.
- Map tests to the core requirements and edge cases.
- Call out compatibility or tooling constraints only when they are known and relevant.

### Generic PRD authoring checklist

- Identify the user, system, and core workflow.
- Define the primary problem and the intended business or technical outcome.
- State the boundaries of the work clearly.
- Capture functional and non-functional requirements in testable language.
- Document dependencies, assumptions, and risks.
- Define what counts as success.
- Add implementation and testing guidance only to the level needed by the user.

### Instruction priority for PRD tasks

- Use this template as the default structure for new PRD creation.
- Tailor the content to the user’s requested domain rather than copying examples verbatim.
- Reuse relevant repository conventions from this file when the PRD targets code in this repo.
- If a source PRD is being generalized, preserve useful structure and constraints while removing product-specific assumptions that do not generalize.

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
