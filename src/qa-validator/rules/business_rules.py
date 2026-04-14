"""Business validation rules for the Contoso Bank loan pipeline."""
from __future__ import annotations
from typing import Any

import pandas as pd

from rules.null_check_rules import ValidationFailure

SECURED_LOAN_TYPES = {"MORTGAGE", "AUTO", "HELOC"}


def check_positive_loan_amount(
    df: pd.DataFrame,
    field: str = "loan_amount",
) -> list[ValidationFailure]:
    """Loan amount must be greater than zero."""
    failures: list[ValidationFailure] = []
    if field not in df.columns:
        return failures
    for idx, value in df[field].items():
        if pd.isna(value):
            continue
        try:
            if float(value) <= 0:
                failures.append(ValidationFailure(
                    row_index=int(idx),
                    field=field,
                    rule_name="positive_loan_amount",
                    actual_value=str(value),
                    message=f"Loan amount must be greater than zero. Got: {value}",
                    severity="critical",
                ))
        except (ValueError, TypeError):
            failures.append(ValidationFailure(
                row_index=int(idx),
                field=field,
                rule_name="numeric_loan_amount",
                actual_value=str(value),
                message=f"Loan amount must be numeric. Got: {value}",
                severity="critical",
            ))
    return failures


def check_collateral_for_secured_loans(
    df: pd.DataFrame,
    loan_type_field: str = "loan_type",
    collateral_field: str = "collateral_value",
) -> list[ValidationFailure]:
    """Secured loan types (MORTGAGE, AUTO, HELOC) must have a positive collateral value."""
    failures: list[ValidationFailure] = []
    if loan_type_field not in df.columns or collateral_field not in df.columns:
        return failures
    for idx, row in df.iterrows():
        loan_type = str(row.get(loan_type_field, "")).upper()
        collateral = row.get(collateral_field)
        if loan_type in SECURED_LOAN_TYPES:
            if pd.isna(collateral) or float(collateral) <= 0:
                failures.append(ValidationFailure(
                    row_index=int(idx),
                    field=collateral_field,
                    rule_name="collateral_required_for_secured_loan",
                    actual_value=str(collateral),
                    message=f"Collateral value is required for secured loan type '{loan_type}'.",
                    severity="critical",
                ))
    return failures


def check_valid_branch_code(
    df: pd.DataFrame,
    branch_field: str = "branch_code",
    valid_branches: set[str] | None = None,
) -> list[ValidationFailure]:
    """Branch code must exist in the reference set (if provided)."""
    if valid_branches is None:
        return []
    failures: list[ValidationFailure] = []
    if branch_field not in df.columns:
        return failures
    for idx, value in df[branch_field].items():
        code = str(value).strip().upper() if pd.notna(value) else ""
        if code not in valid_branches:
            failures.append(ValidationFailure(
                row_index=int(idx),
                field=branch_field,
                rule_name="valid_branch_code",
                actual_value=str(value),
                message=f"Branch code '{value}' not found in reference data.",
                severity="error",
            ))
    return failures
