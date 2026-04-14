"""
Source-to-target reconciliation for the Contoso Bank loan pipeline.

Compares row counts and key metrics between Azure SQL Server source
and Snowflake target tables, flagging discrepancies beyond tolerance.
"""

from __future__ import annotations
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

TOLERANCE_PCT = 0.01  # 1% default tolerance


@dataclass
class ReconciliationResult:
    table_name: str
    source_count: int
    target_count: int
    tolerance_pct: float
    passed: bool
    message: str


def reconcile_counts(
    table_name: str,
    source_count: int,
    target_count: int,
    tolerance_pct: float = TOLERANCE_PCT,
) -> ReconciliationResult:
    """
    Compare source and target counts with a configurable tolerance.

    A 1% default tolerance accommodates minor filtering differences
    between the raw source extract and the cleaned Snowflake target.

    Returns a ReconciliationResult indicating pass/fail.
    """
    if source_count == 0:
        passed = target_count == 0
        message = (
            "PASS: both source and target are empty."
            if passed
            else f"FAIL: source is empty but target has {target_count} rows."
        )
        return ReconciliationResult(
            table_name, source_count, target_count, tolerance_pct, passed, message
        )

    diff_pct = abs(source_count - target_count) / source_count
    passed = diff_pct <= tolerance_pct
    message = (
        f"PASS: source={source_count}, target={target_count} ({diff_pct:.2%} diff)."
        if passed
        else (
            f"FAIL: source={source_count}, target={target_count} "
            f"({diff_pct:.2%} diff exceeds {tolerance_pct:.2%} tolerance)."
        )
    )
    logger.info("[%s] %s", table_name, message)
    return ReconciliationResult(
        table_name, source_count, target_count, tolerance_pct, passed, message
    )
