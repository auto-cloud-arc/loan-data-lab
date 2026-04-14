"""Source-to-target reconciliation rules for the Contoso Bank loan pipeline."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class ReconciliationCheck:
    table_name: str
    source_count: int
    target_count: int
    tolerance_pct: float
    passed: bool
    diff_pct: float
    message: str


def check_row_count_reconciliation(
    table_name: str,
    source_count: int,
    target_count: int,
    tolerance_pct: float = 0.01,
) -> ReconciliationCheck:
    """
    Compare source and target row counts within tolerance.

    A 1% default tolerance accommodates minor filtering differences
    between the raw Azure SQL extract and the cleaned Snowflake target.
    """
    if source_count == 0:
        passed = target_count == 0
        diff_pct = 0.0
        message = (
            "PASS: both empty."
            if passed
            else f"FAIL: source empty, target={target_count}."
        )
    else:
        diff_pct = abs(source_count - target_count) / source_count
        passed = diff_pct <= tolerance_pct
        message = (
            f"PASS: source={source_count}, target={target_count} ({diff_pct:.2%} diff)."
            if passed
            else (
                f"FAIL: source={source_count}, target={target_count} "
                f"({diff_pct:.2%} exceeds {tolerance_pct:.2%})."
            )
        )
    return ReconciliationCheck(
        table_name, source_count, target_count, tolerance_pct, passed, diff_pct, message
    )
