"""Date validation rules for the Contoso Bank loan pipeline."""
from __future__ import annotations
from datetime import datetime
from typing import Any

import pandas as pd

from rules.null_check_rules import ValidationFailure


def check_application_date_not_future(
    df: pd.DataFrame,
    date_field: str = "application_date",
    reference_date: datetime | None = None,
) -> list[ValidationFailure]:
    """Flag rows where application_date is in the future."""
    reference = reference_date or datetime.utcnow()
    failures: list[ValidationFailure] = []
    if date_field not in df.columns:
        return failures
    for idx, value in df[date_field].items():
        if pd.isna(value):
            continue
        try:
            parsed = pd.to_datetime(value)
            if parsed.date() > reference.date():
                failures.append(ValidationFailure(
                    row_index=int(idx),
                    field=date_field,
                    rule_name="application_date_not_future",
                    actual_value=str(value),
                    message=f"Application date '{value}' is in the future.",
                    severity="error",
                ))
        except (ValueError, TypeError):
            failures.append(ValidationFailure(
                row_index=int(idx),
                field=date_field,
                rule_name="valid_date_format",
                actual_value=str(value),
                message=f"Cannot parse date value '{value}'.",
                severity="error",
            ))
    return failures
