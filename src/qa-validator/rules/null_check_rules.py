"""Null check validation rules for the Contoso Bank loan pipeline."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

import pandas as pd


@dataclass
class ValidationFailure:
    row_index: int
    field: str
    rule_name: str
    actual_value: Any
    message: str
    severity: str = "critical"


def check_not_null(
    df: pd.DataFrame,
    field_name: str,
    severity: str = "critical",
) -> list[ValidationFailure]:
    """Flag rows where the specified field is null or empty string."""
    failures: list[ValidationFailure] = []
    if field_name not in df.columns:
        return failures
    for idx, value in df[field_name].items():
        if pd.isna(value) or (isinstance(value, str) and value.strip() == ""):
            failures.append(ValidationFailure(
                row_index=int(idx),
                field=field_name,
                rule_name="not_null",
                actual_value=None,
                message=f"Field '{field_name}' must not be null or empty.",
                severity=severity,
            ))
    return failures


def check_required_business_keys(df: pd.DataFrame) -> list[ValidationFailure]:
    """Check that all required business key fields are present and non-null."""
    required_fields = ["application_id", "customer_id", "branch_code"]
    failures: list[ValidationFailure] = []
    for required_field in required_fields:
        failures.extend(check_not_null(df, required_field, severity="critical"))
    return failures
