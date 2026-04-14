# Domain Story — Contoso Bank Loan Data Modernization

## The Business Context

Contoso Bank is a mid-sized regional bank with branches across the United States. Every day, hundreds of loan applications arrive from branch offices — mortgages, auto loans, personal loans, HELOCs, and small business loans. Each application carries sensitive customer data: names, social security numbers, addresses, and financial information.

For over a decade, these applications have been captured in a legacy Azure SQL Server database called `loan_db`. The system works — mostly — but the data quality problems have been piling up for years. Loan officers enter data by hand. Some branches use `MM/DD/YYYY` dates; others use `YYYY-MM-DD`. State codes arrive in lowercase. Phone numbers appear in six different formats. Occasionally, a future application date slips through. Every month, the data analytics team spends days cleaning data manually before they can run a single report.

The breaking point came when the risk management team discovered three separate customer records for the same borrower — each with a slightly different address and phone number — all flagged for different loan applications. The duplicate customer problem had been known for years, but nobody had automated a fix.

## The Four Conveyor Belts

To tell the story of this modernization, imagine the loan data moving along four conveyor belts, each one handing work to the next.

---

### Belt 1 — Legacy Intake

**The problem**: Raw loan application data arrives in Azure SQL Server in whatever format the branch system produces. Date formats vary. State codes are inconsistent. Required fields are sometimes blank. Duplicate customer entries accumulate over time.

**The actors**: Branch loan officers, legacy intake system, Azure SQL Server

**What happens here**: 
- The stored procedure `usp_extract_daily_applications` pulls the previous day's new applications into a staging extract
- The stored procedure `usp_flag_duplicate_customers` identifies customers who appear more than once with the same SSN hash
- The extract is written to a CSV file and placed in Azure Blob Storage

**The pain**: Nobody trusts the raw data. Before any analysis can happen, someone has to clean it.

---

### Belt 2 — Data Cleaning

**The solution**: The **C# Data Cleaner** (`ContosoLoanCleaner`) picks up the raw CSV extract and applies systematic normalization and validation rules.

**The actors**: `LoanApplicationParser`, `AddressNormalizer`, `PhoneNormalizer`, `DateNormalizer`, `LoanApplicationValidator`

**What happens here**:
1. The parser reads each row from the CSV into a `LoanApplication` model
2. The normalizers clean the data:
   - State codes → uppercase, validated against the 50 states + DC
   - ZIP codes → first 5 digits only
   - Phone numbers → `(NNN) NNN-NNNN` format
   - Dates → ISO 8601 `yyyy-MM-dd` format
3. The validator applies business rules:
   - Application ID and Customer ID must be present
   - Loan amount must be positive
   - Loan type must be a recognized value
   - Secured loans (MORTGAGE, AUTO, HELOC) must have a positive collateral value
   - Application date cannot be in the future
4. Clean records are written to `loan_applications_cleaned.csv`
5. Failed records are written to a JSON exception report — with SSN, name, and email **redacted** to protect PII

**The outcome**: A clean, validated CSV that the downstream Snowflake platform can trust.

---

### Belt 3 — Modern Transformation

**The solution**: Snowpark Python jobs read the cleaned data from Snowflake's `RAW_ZONE` and produce curated analytical tables in `CURATED_ZONE`.

**The actors**: Snowflake (`CONTOSO_LOAN_DB`), Snowpark Python transforms, `CONTOSO_DATA_ENGINEER` role

**What happens here**:
1. The cleaned CSV is loaded into `RAW_ZONE.LOAN_APPLICATION_CLEANED`
2. `borrower_360_transform.py` joins application data with branch reference data, standardizes branch codes (e.g. `br-01` → `BR-01`), and computes a risk tier based on loan-to-value ratio:
   - **LOW**: LTV < 80% (well-collateralized)
   - **MEDIUM**: LTV 80–90%
   - **HIGH**: LTV > 90% or unsecured loan type
3. `loan_application_curated_transform.py` enriches each application with branch metadata
4. `collateral_summary_transform.py` aggregates collateral values by loan type and region for risk reporting

**The outcome**: Three curated tables that analysts can query directly in Snowsight — without manual cleaning.

---

### Belt 4 — Quality and Trust

**The solution**: The **QA Validator** runs a suite of automated validation rules against the curated data and produces a DQ (data quality) exception report.

**The actors**: Python validation rule functions, pandas DataFrames, QA report generator, `CONTOSO_QA` role

**What happens here**:
1. The runner loads the cleaned CSV (or queries Snowflake directly)
2. Rule functions check for:
   - Missing required keys (`application_id`, `customer_id`, `branch_code`)
   - Future application dates
   - Non-positive loan amounts
   - Missing collateral on secured loan types
3. Any failures are recorded as `ValidationFailure` objects with row index, field name, rule name, and message
4. The report generator emits:
   - A JSON report (`qa_report_YYYYMMDD_HHMMSS.json`) for automated consumption
   - A Markdown report for human review in GitHub Actions artifacts

**The outcome**: A trusted, auditable data quality gate. If critical failures exist, the CI pipeline returns a non-zero exit code, blocking downstream consumption.

---

## Why This Matters

When all four belts work together, Contoso Bank's analysts get clean, curated, trusted loan data in Snowflake within hours of each branch closing — not days. Risk managers can see real-time LTV exposure by region. Compliance officers can audit the full lineage from raw SQL Server extract to curated Snowflake table. And the data engineering team can sleep through the night without being paged about a bad date format.

The workshop challenge: use GitHub Copilot to build, understand, extend, and debug every component of this pipeline.
