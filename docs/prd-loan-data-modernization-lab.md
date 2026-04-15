# Product Requirements Document (PRD): Contoso Bank Loan Data Modernization Lab

## 1. Document information

| Field | Value |
| ----- | ----- |
| Document title | Contoso Bank Loan Data Modernization Lab PRD |
| Version | 1.0 |
| Status | Draft |
| Last updated | 2026-04-15 |
| Repository | `loan-data-lab` |
| Primary domain | Loan data modernization, data quality, analytics enablement |

## 2. Executive summary

The Contoso Bank Loan Data Modernization Lab is a reference implementation and workshop project that demonstrates how to modernize a legacy bank loan onboarding pipeline from Azure SQL Server to Snowflake. The system ingests raw loan application extracts, applies C#-based normalization and validation, transforms cleaned records with Snowpark Python into curated analytical tables, and enforces downstream quality gates through a Python QA validator that emits JSON and Markdown reports.

The product goal is twofold:

1. Provide a working end-to-end modernization example with realistic data quality problems, lineage, validation, and infrastructure.
2. Serve as a hands-on GitHub Copilot workshop repository for understanding, generating, testing, refactoring, and debugging each stage of the pipeline.

## 3. Problem statement

Contoso Bank's legacy loan intake data arrives with inconsistent formats, incomplete required fields, duplicate customer records, malformed values, and future-dated or invalid application data. These issues slow down analytics, reduce trust in downstream reporting, and create manual cleanup work for data engineering, analytics, and risk teams.

The current business problem is not simply moving data from one platform to another. It is establishing a repeatable, auditable, and secure data flow that:

- preserves lineage from legacy source to curated analytical outputs,
- normalizes and validates operational loan data early,
- blocks or flags poor-quality records before they reach downstream consumers,
- supports secure handling of PII,
- and provides a practical modernization lab for engineering and Copilot-assisted development.

## 4. Goals and objectives

### 4.1 Primary goals

- Modernize the loan data flow from Azure SQL Server to Snowflake.
- Reduce manual cleaning effort by codifying normalization and validation rules.
- Produce trusted curated datasets for analysis and downstream reporting.
- Make data quality outcomes visible through automated QA reporting.
- Provide an end-to-end workshop environment for GitHub Copilot-assisted engineering tasks.

### 4.2 Supporting objectives

- Preserve clear contracts for source, curated, and report outputs.
- Enable local execution and testing for the C# cleaner, QA validator, and Snowpark helper logic.
- Support Azure-based infrastructure deployment with Bicep and GitHub Actions.
- Demonstrate secure handling of sensitive financial and customer data.

## 5. Scope

### 5.1 In scope

- Legacy source schema and seed data in Azure SQL Server (`loan_db`)
- Daily extract-oriented source workflow represented by SQL scripts and stored procedures
- C# .NET 8 cleaner for CSV parsing, normalization, validation, and exception reporting
- Snowflake DDL, roles, stages, and stored procedure assets
- Snowpark Python transforms for curated tables and reconciliation logic
- Python QA validator for rule execution and machine/human-readable report generation
- Azure infrastructure provisioning using Bicep
- GitHub Actions workflows for CI, data quality validation, and Azure SQL deployment
- Workshop prompts, agents, documentation, and onboarding guidance

### 5.2 Out of scope

- Production-grade orchestration across enterprise schedulers or event buses
- Real-time or streaming ingestion
- Consumer-facing user interfaces
- Operational servicing workflows after loan origination
- Full banking compliance implementation beyond the patterns shown in the repo
- Direct production deployment to a real bank environment

## 6. Users and use cases

### 6.1 Primary users

| User type | Need |
| --------- | ---- |
| Data engineer | Build, validate, and evolve the ingestion, transformation, and reconciliation pipeline |
| QA engineer | Define and run data quality rules, inspect failures, and gate downstream outputs |
| Analytics engineer or analyst | Consume curated loan and collateral datasets with known quality guarantees |
| Platform or cloud engineer | Provision Azure resources and run infrastructure-backed workflows |
| Workshop participant | Learn architecture, generate code, refactor code, and debug data pipeline components using Copilot |

### 6.2 Core use cases

- Extract loan-related data from the legacy Azure SQL environment.
- Normalize raw loan application data into a clean CSV suitable for downstream ingestion.
- Reject or flag invalid records and produce an exception report with redacted PII.
- Transform cleaned data into curated Snowflake tables such as `BORROWER_360`, `LOAN_APPLICATION_CURATED`, and `COLLATERAL_SUMMARY`.
- Validate curated outputs with QA rules and source-to-target reconciliation.
- Review JSON and Markdown reports to determine pass or fail status.
- Use the repository as a guided modernization and Copilot workshop lab.

## 7. Functional requirements

| ID | Requirement |
| -- | ----------- |
| FR-1 | The system shall maintain a legacy source layer in Azure SQL Server for `loan_application_raw`, `customer_raw`, `collateral_raw`, and `branch_reference` data. |
| FR-2 | The system shall support extraction of daily application data from Azure SQL Server into a CSV-oriented handoff for the cleaner stage. |
| FR-3 | The C# cleaner shall parse raw loan application CSV data into typed application records. |
| FR-4 | The C# cleaner shall normalize state codes, ZIP codes, phone numbers, dates, and loan type values before final validation. |
| FR-5 | The C# cleaner shall validate required fields and business rules including application identifiers, customer identifiers, loan amount positivity, recognized loan type, secured-loan collateral requirements, and non-future application dates. |
| FR-6 | The C# cleaner shall write passing records to a cleaned CSV output. |
| FR-7 | The C# cleaner shall write failing records to a JSON exception report. |
| FR-8 | The exception report shall redact or mask sensitive PII fields before persistence. |
| FR-9 | The Snowflake layer shall support raw, curated, QA, and reference zones or equivalent schemas used by the repository assets. |
| FR-10 | Snowpark transforms shall join cleaned application data with branch reference data and produce curated analytical outputs. |
| FR-11 | The `borrower_360` transform shall normalize branch codes and compute a `risk_tier` using loan-to-value and secured-loan rules. |
| FR-12 | The `loan_application_curated` transform shall enrich applications with branch metadata and standardized fields. |
| FR-13 | The `collateral_summary` transform shall aggregate collateral and loan metrics by loan type and region. |
| FR-14 | The QA validator shall run rule-based validation against cleaned or curated data inputs. |
| FR-15 | The QA validator shall check for null business keys, invalid or future dates, invalid loan amounts, missing collateral for secured loans, and reconciliation mismatches. |
| FR-16 | The QA validator shall produce both JSON and Markdown reports for each validation run. |
| FR-17 | The QA validator shall return a non-zero exit code when critical validation failures or reconciliation failures are detected. |
| FR-18 | The repository shall provide local test workflows for .NET and Python components. |
| FR-19 | The repository shall provide infrastructure definitions for Azure SQL, Key Vault, and Storage. |
| FR-20 | The repository shall support GitHub Actions workflows for build, data quality validation, and Azure SQL deployment. |
| FR-21 | The repository shall document onboarding, architecture, contracts, and operational runbooks for workshop participants and maintainers. |

## 8. Non-functional requirements

| ID | Requirement |
| -- | ----------- |
| NFR-1 | The system shall handle malformed or invalid data without crashing the cleaner or validator processes. |
| NFR-2 | The system shall preserve clear separation of concerns across source extraction, cleaning, transformation, and validation stages. |
| NFR-3 | The system shall support local development on .NET 8 and Python 3.11+ environments. |
| NFR-4 | The system shall avoid logging raw SSN, email, date of birth, full name, or other sensitive PII. |
| NFR-5 | The system shall externalize infrastructure secrets and credentials through Azure Key Vault or environment variables rather than source control. |
| NFR-6 | The system shall remain testable without requiring live Snowflake connectivity for pure helper logic. |
| NFR-7 | The system shall provide traceable documentation and data contracts for the core tables and artifacts. |
| NFR-8 | The system shall use structured logging and readable validation outputs to support debugging and workshop learning. |
| NFR-9 | The system shall keep naming and implementation conventions consistent across C#, Python, SQL, and documentation assets. |

## 9. Assumptions and dependencies

### 9.1 Assumptions

- Azure SQL Server remains the modeled legacy source of truth for raw intake data.
- Cleaned CSV output is the handoff boundary between the C# cleaner and downstream analytical processing.
- Snowflake is the target analytical platform used for curated outputs.
- QA reporting is treated as a gating and trust-building step rather than optional documentation.
- The repository continues to serve both as a working sample system and as a Copilot workshop asset.

### 9.2 Dependencies

| Dependency | Purpose |
| ---------- | ------- |
| .NET 8 SDK | Build and run the C# cleaner and tests |
| Python 3.11+ | Run QA validation and Snowpark helper tests |
| Azure CLI | Authenticate and deploy Azure resources or execute SQL helper workflows |
| Snowflake account | Required for live Snowpark execution beyond local helper tests |
| GitHub Actions | CI, validation, and Azure deployment workflows |
| Azure Key Vault | Secret storage for deployed Azure infrastructure |
| Azure Storage | Staging area for raw and cleaned extract patterns |

## 10. Success criteria and KPIs

- Clean sample data can be generated reproducibly from raw sample input through the C# cleaner.
- Invalid sample records are captured in a JSON exception report with PII-safe output.
- Snowpark helper logic passes local tests and produces the expected field-level transformations.
- QA validation produces JSON and Markdown reports and correctly fails on critical issues.
- Core documentation remains sufficient for onboarding a new engineer or workshop participant.
- Azure SQL deployment workflow can provision the documented dev environment and apply schema plus seed data.
- The repository demonstrates end-to-end lineage from legacy source concepts to curated analytical outputs.

## 11. Milestones and implementation phases

### Phase 1: Legacy source and contracts

- Define Azure SQL schema and reference data
- Seed representative raw source data
- Document canonical contracts and domain glossary

### Phase 2: Data cleaning and exception handling

- Implement CSV parsing, normalization, and validation in the C# cleaner
- Produce cleaned CSV and exception JSON artifacts
- Add .NET unit tests and structured logging

### Phase 3: Modern transformation layer

- Define Snowflake database objects and roles
- Implement Snowpark transforms for borrower, application, and collateral outputs
- Add reconciliation helpers and local Python tests

### Phase 4: Data quality enforcement

- Implement Python QA rules and reporting pipeline
- Add report generators and exit-code gating behavior
- Integrate data quality validation into CI workflows

### Phase 5: Infrastructure, operations, and workshop enablement

- Provision Azure resources with Bicep
- Document onboarding and deployment runbooks
- Maintain Copilot prompts, agents, and demo scripts for workshop usage

## 12. Implementation guidance

### 12.1 C# cleaner

- Use .NET 8 conventions with explicit validation and structured logging.
- Keep normalization and validation logic separated into dedicated parser, normalizer, and validator components.
- Return validation failures as objects rather than relying on exception-driven control flow.
- Ensure output directories are created as needed before writing artifacts.

### 12.2 Snowpark transforms

- Keep pure Python helper logic isolated from Snowpark orchestration where possible.
- Use branch normalization and risk-tier computation that align with the documented data contracts.
- Write transforms to curated target tables with explicit, deterministic field selection.

### 12.3 QA validator

- Keep rules modular by concern: null checks, date checks, business checks, and reconciliation.
- Ensure all validation output is reportable in both machine-readable and human-readable formats.
- Use severity to distinguish informational findings from pipeline-blocking failures.

### 12.4 Infrastructure and operations

- Keep Azure infrastructure definitions declarative in Bicep.
- Use Microsoft Entra authentication for Azure SQL access in the documented environment.
- Store secrets outside source control and reference them via Key Vault or environment variables.

## 13. Testing and validation approach

| Layer | Validation approach |
| ----- | ------------------- |
| C# cleaner | `dotnet restore`, `dotnet build`, `dotnet test`, plus sample-data execution |
| QA validator | `pytest` for rules and report generation, CLI validation run against cleaned CSV |
| Snowpark helpers | `pytest` for pure-Python transform and reconciliation logic |
| Azure SQL | Schema and seed execution through helper scripts or deployment workflow |
| Documentation and onboarding | Manual walkthrough using onboarding and demo scripts |

The validation strategy shall cover:

- record-level normalization and parsing behavior,
- rule-level validation outcomes,
- edge cases such as future dates and non-positive loan amounts,
- reconciliation pass or fail scenarios,
- and expected output artifact generation.

## 14. Risks, constraints, and operational notes

### 14.1 Risks

- Divergence between documented contracts and transform implementations may reduce trust in curated outputs.
- Live Azure and Snowflake dependencies may be unavailable to some contributors, increasing reliance on local-only tests.
- PII handling mistakes in logs or reports would create security and compliance risk.
- Manual operational steps around environment setup can slow workshop onboarding if documentation drifts.

### 14.2 Constraints

- The documented Azure dev environment is region-constrained to `centralus` for the current subscription.
- Azure SQL access uses Microsoft Entra-only authentication in the documented environment.
- Some transforms and warehouse assets are modeled for learning and demonstration rather than full production orchestration.

### 14.3 Operational notes

- The Azure SQL deployment workflow applies schema and seed files in a documented order.
- The QA validator uses exit codes to signal critical failures and reconciliation issues.
- The repository intentionally includes prompts, agents, and workshop assets as part of the product experience.

## 15. Open questions

- Should future versions of the lab include direct Snowflake-backed QA validation as the default path rather than CSV-based validation?
- Should orchestration be formalized beyond the current script and workflow model?
- Should the lab evolve from a workshop reference into a more production-like blueprint with scheduling, observability, and lineage tooling?
