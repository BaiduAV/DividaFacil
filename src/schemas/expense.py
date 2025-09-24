from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, validator

from src.models.expense import Expense
from src.models.installment import Installment


class SplitType(str, Enum):
    EQUAL = "EQUAL"
    EXACT = "EXACT"
    PERCENTAGE = "PERCENTAGE"


class ExpenseCreate(BaseModel):
    description: str
    amount: float
    paid_by: str
    split_among: List[str]
    split_type: SplitType = SplitType.EQUAL
    split_values: Dict[str, float] = {}
    installments_count: int = 1
    first_due_date: Optional[datetime] = None

    @validator("amount")
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v

    @validator("installments_count")
    def installments_must_be_positive(cls, v):
        if v < 1:
            raise ValueError("Installments count must be at least 1")
        return v


class InstallmentResponse(BaseModel):
    number: int
    amount: float
    due_date: datetime
    paid: bool
    paid_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_installment(cls, installment: Installment) -> "InstallmentResponse":
        """Create InstallmentResponse from Installment model."""
        return cls(
            number=installment.number,
            amount=installment.amount,
            due_date=installment.due_date,
            paid=installment.paid,
            paid_at=installment.paid_at,
        )


class ExpenseResponse(BaseModel):
    id: str
    description: str
    amount: float
    paid_by: str
    created_by: Optional[str]
    split_among: List[str]
    split_type: SplitType
    split_values: Dict[str, float]
    created_at: datetime
    installments_count: int
    first_due_date: Optional[datetime]
    installments: List[InstallmentResponse] = []

    class Config:
        from_attributes = True

    @classmethod
    def from_expense(cls, expense: Expense) -> "ExpenseResponse":
        """Create ExpenseResponse from Expense model."""
        return cls(
            id=expense.id,
            description=expense.description,
            amount=expense.amount,
            paid_by=expense.paid_by,
            split_among=expense.split_among,
            split_type=SplitType(expense.split_type),
            split_values=expense.split_values,
            created_at=expense.created_at,
            installments_count=expense.installments_count,
            first_due_date=expense.first_due_date,
            installments=[
                InstallmentResponse.from_installment(inst) for inst in expense.installments
            ],
        )
