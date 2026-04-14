# Demo Script — Contoso Bank Loan Data Modernization Lab

**Duration**: 90–120 minutes  
**Audience**: Developers, data engineers, and technical leads evaluating GitHub Copilot  
**Prerequisites**: VS Code + GitHub Copilot extension, .NET 8 SDK, Python 3.11, Git

---

## Step 1 — Orientation: Ask Copilot to Explain the Architecture

**Goal**: Show how Copilot Chat helps new team members onboard quickly.

1. Open the repository in VS Code.
2. Open Copilot Chat and type:
   > "Explain the overall architecture of this repository. What does each folder do, and how does data flow from Azure SQL Server to Snowflake?"
3. Follow up with:
   > "What is a `borrower_360` and why does it join application and branch data?"

**Key talking point**: Copilot reads `docs/architecture.md`, `copilot-instructions.md`, and the source tree to give a grounded answer — not a generic one.

---

## Step 2 — Plan Mode: Design the Borrower Intake Workflow

**Goal**: Demonstrate Copilot Plan Mode for architecture planning before writing code.

1. Switch Copilot Chat to **Plan Mode**.
2. Ask:
   > "I need to add a new field `annual_income` to the loan application pipeline. Walk me through every file I'd need to change, from the C# model through to the Snowflake curated table and QA validator."
3. Review the plan Copilot produces. Notice it references:
   - `LoanApplication.cs` (model)
   - `LoanApplicationValidator.cs` (validation rule)
   - `01_create_tables.sql` (SQL schema)
   - `03_create_tables.sql` (Snowflake DDL)
   - `data-contracts.md` (documentation)

**Key talking point**: Plan Mode prevents "surprise" code changes. Copilot acts as a senior engineer reviewing the blast radius before coding.

---

## Step 3 — C# Code Generation: Generate the Data Cleaner

**Goal**: Show Copilot generating production-quality C# code from a description.

1. Open `src/data-cleaner-csharp/ContosoLoanCleaner/Normalizers/PhoneNormalizer.cs`.
2. Ask Copilot:
   > "Add a method `MaskForLogging` that returns only the last 4 digits of the phone number for safe logging, e.g. '***-***-1234'."
3. Accept the suggestion and verify the output format.
4. Then ask:
   > "Write a unit test in `PhoneNormalizerTests.cs` for the new `MaskForLogging` method."

**Key talking point**: Copilot follows the existing `IFieldNormalizer<T>` pattern and Serilog structured logging conventions established in `copilot-instructions.md`.

---

## Step 4 — Refactor: Improve Generated Code Quality

**Goal**: Demonstrate Copilot's refactoring capabilities on existing code.

1. Open `src/data-cleaner-csharp/ContosoLoanCleaner/Validators/LoanApplicationValidator.cs`.
2. Select the entire `Validate` method and ask:
   > "Refactor this method to use a list of validation rule delegates so new rules can be registered without modifying this class."
3. Observe how Copilot introduces a strategy/plugin pattern.

**Key talking point**: Copilot understands design patterns and can suggest improvements beyond simple autocomplete.

---

## Step 5 — Unit Testing: Generate xUnit and pytest Test Suites

**Goal**: Show test generation for both C# and Python components.

1. Open `src/data-cleaner-csharp/ContosoLoanCleaner/Normalizers/DateNormalizer.cs`.
2. Ask Copilot:
   > "Generate xUnit tests covering: valid ISO date, MM/DD/YYYY format, invalid string, empty string, future date, and boundary date of today."
3. Switch to Python. Open `src/qa-validator/rules/business_rules.py`.
4. Ask Copilot:
   > "Write pytest tests for `check_collateral_for_secured_loans` covering: MORTGAGE with collateral (pass), AUTO without collateral (fail), PERSONAL without collateral (pass), zero collateral for HELOC (fail)."

**Key talking point**: Copilot generates tests that match the existing `[Theory]`/`[InlineData]` xUnit pattern and pytest fixture style.

---

## Step 6 — Azure SQL: Seed and Query the Legacy Source Tables

**Goal**: Show Copilot assistance with SQL modernization.

1. Open `src/sqlserver/stored-procs/usp_extract_daily_applications.sql`.
2. Ask Copilot (using the `.copilot/prompts/explain-legacy-sql-to-modern-sql.prompt.md` prompt):
   > "Paste the stored procedure content. Explain what it does and rewrite it with CTEs."
3. Then open `src/sqlserver/seed/02_seed_loan_application_raw.sql` and ask:
   > "One of these seed rows has a future application date. Which one, and what C# validation rule catches it?"

**Key talking point**: The Data Engineer Agent in `.copilot/agents/data-engineer.agent.md` knows the full schema context.

---

## Step 7 — Snowpark: Write and Run Transformation Jobs

**Goal**: Show Snowpark code generation with the custom prompt template.

1. Open the prompt file `.copilot/prompts/create-snowpark-transform.prompt.md`.
2. Fill in:
   - **Transformation**: "Add a `days_since_application` computed column to `borrower_360`"
   - **Source**: `CURATED_ZONE.BORROWER_360`
   - **Target**: `CURATED_ZONE.BORROWER_360`
3. Submit the prompt and review the generated Snowpark code.
4. Ask Copilot to add a unit test for the helper function.

**Key talking point**: Separating pure Python helpers from Snowpark API calls makes the logic testable without a live Snowflake connection.

---

## Step 8 — QA Validator: Create and Run Validation Rules

**Goal**: Demonstrate the generate-validator-rule prompt and rule registration flow.

1. Open `.copilot/prompts/generate-validator-rule.prompt.md`.
2. Fill in:
   - **Rule**: "Credit score must be between 300 and 850 inclusive"
   - **Field**: `credit_score`
   - **Severity**: `error`
3. Ask Copilot to implement the rule following the existing pattern in `business_rules.py`.
4. Register it in `run_validations.py` and run:
   ```bash
   pytest src/qa-validator/tests/ -v
   ```

**Key talking point**: The QA Validator Agent knows to follow the `ValidationFailure` dataclass pattern and register rules in the runner.

---

## Step 9 — Debug: Trace a Failing Pipeline Stage

**Goal**: Show Copilot as a debugging partner.

1. Examine `sample-data/expected/dq_exception_report_expected.json`.
2. Ask Copilot:
   > "The QA report shows APP-007 failing `positive_loan_amount`. Trace backwards: which seed SQL file introduced this row, which C# rule should have caught it before Snowflake, and which QA rule catches it now?"
3. Then ask:
   > "Show me the exact line in `LoanApplicationValidator.cs` that validates loan amount, and explain why APP-007 with loan_amount = -500 passes through if this check exists."

**Key talking point**: Copilot can do cross-language root-cause analysis across C#, SQL, and Python when given good repo context.

---

## Step 10 — Agents: Use Custom Agents from `.copilot/`

**Goal**: Demonstrate the power of specialized agents with domain knowledge.

1. Open the **Secure Code Reviewer Agent** (`secure-code-reviewer.agent.md`) in a Copilot Chat session.
2. Ask:
   > "Review the entire `src/data-cleaner-csharp/ContosoLoanCleaner/Program.cs` for PII leakage risks."
3. Switch to the **QA Validator Agent** and ask:
   > "Explain the difference between a `critical` and an `error` severity failure in our QA reports, and give examples of each from the existing rules."
4. Switch to the **Data Engineer Agent** and ask:
   > "What Snowflake role should run the `sp_load_borrower_360` procedure and why?"

**Key talking point**: Custom agents with domain-specific system prompts and codebase tool access dramatically outperform generic Copilot Chat for specialized tasks.

---

## Wrap-Up

Key capabilities demonstrated:
- **Grounded answers** — Copilot reads repo context, not just the internet
- **Plan Mode** — blast-radius analysis before writing code
- **Multi-language fluency** — C#, Python, SQL, Bicep in one session
- **Custom prompts and agents** — reusable, domain-tuned AI workflows
- **Security awareness** — PII detection, credential scanning, logging safety
