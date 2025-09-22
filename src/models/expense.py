from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from .installment import Installment

@dataclass
class Expense:
    """Represents an expense in the Splitwise application."""
    id: str
    amount: float
    description: str
    paid_by: str  # user_id who paid
    split_among: List[str]  # List of user_ids
    created_by: Optional[str] = None  # user_id who created this expense
    split_type: str = 'EQUAL'  # 'EQUAL', 'EXACT', or 'PERCENTAGE'
    split_values: Dict[str, float] = field(default_factory=dict)  # user_id -> amount/percentage
    created_at: datetime = field(default_factory=datetime.now)
    # Installments support
    installments: List[Installment] = field(default_factory=list)
    installments_count: int = 1
    first_due_date: Optional[datetime] = None

    def validate_split(self):
        """Validate that the split values are correct based on split type."""
        if self.split_type == 'EQUAL':
            if self.split_values:
                raise ValueError("EQUAL split should not have split_values")
            return True
            
        elif self.split_type == 'EXACT':
            total = sum(self.split_values.values())
            if abs(total - self.amount) > 0.01:  # Allow for floating point errors
                raise ValueError(f"Sum of exact splits ({total}) does not match expense amount ({self.amount})")
            
        elif self.split_type == 'PERCENTAGE':
            total_percentage = sum(self.split_values.values())
            if abs(total_percentage - 100.0) > 0.01:  # Allow for floating point errors
                raise ValueError(f"Sum of percentages ({total_percentage}) does not equal 100%")
        
        return True
