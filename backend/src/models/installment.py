from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class Installment:
    """Represents a single installment of an expense."""

    number: int
    due_date: date
    amount: float
    paid: bool = False
    paid_at: Optional[datetime] = None
