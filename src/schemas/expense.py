from pydantic import BaseModel, validator
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


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

    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v

    @validator('installments_count')
    def installments_must_be_positive(cls, v):
        if v < 1:
            raise ValueError('Installments count must be at least 1')
        return v


class InstallmentResponse(BaseModel):
    number: int
    amount: float
    due_date: datetime
    paid: bool
    paid_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ExpenseResponse(BaseModel):
    id: str
    description: str
    amount: float
    paid_by: str
    split_among: List[str]
    split_type: SplitType
    split_values: Dict[str, float]
    created_at: datetime
    installments_count: int
    first_due_date: Optional[datetime]
    installments: List[InstallmentResponse] = []

    class Config:
        from_attributes = True
