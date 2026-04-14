---
description: Generate a Python QA validation rule for the loan data pipeline
mode: ask
---

You are a QA engineer at Contoso Bank. Generate a Python validation rule function that:

1. Accepts a pandas DataFrame as input.
2. Returns a list of `ValidationFailure` objects (each with `row_index`, `field`, `rule_name`, `actual_value`, `message`).
3. Raises no exceptions on empty DataFrames — return an empty list instead.
4. Is covered by a pytest unit test with at least one passing case and one failing case.
5. Is registered in `src/qa-validator/rules/` following the existing rule module pattern.

**Rule to implement:**
<!-- Describe the rule, e.g.: "Loan amount must be greater than zero for all loan types." -->

**Field(s) involved:**
**Severity:** critical / warning / info
**Reference data needed (if any):**
