"""Centralized calculation of per-user portions for expenses.

All logic for EQUAL / EXACT / PERCENTAGE distribution lives here so that
other modules (services, database helpers) rely on a single source of truth.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict

from src.constants import (
    ERROR_INVALID_SPLIT_TYPE,
    ERROR_NO_SPLIT_VALUES,
    ERROR_NO_USERS_TO_SPLIT,
    PERCENTAGE_BASE,
    SPLIT_EQUAL,
    SPLIT_EXACT,
    SPLIT_PERCENTAGE,
)
from src.models.expense import Expense


def _round(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_portions(expense: Expense) -> Dict[str, float]:
    """Return mapping user_id -> portion amount (float, rounded to 2 decimals).

    Remainders from rounding are assigned deterministically to the last
    non-payer user (or payer if all participants) to preserve sum equality.
    """
    amount = Decimal(str(expense.amount))

    if expense.split_type == SPLIT_EQUAL:
        if not expense.split_among:
            raise ValueError(ERROR_NO_USERS_TO_SPLIT)
        per = amount / len(expense.split_among)
        portions = {uid: _round(per) for uid in expense.split_among}
        diff = amount - sum(portions.values())
        if abs(diff) > Decimal("0"):
            candidates = [u for u in expense.split_among if u != expense.paid_by] or [
                expense.paid_by
            ]
            last = candidates[-1]
            portions[last] = _round(portions[last] + diff)
        return {uid: float(v) for uid, v in portions.items()}

    if expense.split_type == SPLIT_EXACT:
        if not expense.split_values:
            raise ValueError(ERROR_NO_SPLIT_VALUES)
        return {uid: float(_round(Decimal(str(val)))) for uid, val in expense.split_values.items()}

    if expense.split_type == SPLIT_PERCENTAGE:
        if not expense.split_values:
            raise ValueError(ERROR_NO_SPLIT_VALUES)
        result: Dict[str, float] = {}
        for uid, pct in expense.split_values.items():
            portion = (amount * Decimal(str(pct))) / PERCENTAGE_BASE
            result[uid] = float(_round(portion))
        return result

    raise ValueError(f"{ERROR_INVALID_SPLIT_TYPE}: {expense.split_type}")


__all__ = ["calculate_portions"]
