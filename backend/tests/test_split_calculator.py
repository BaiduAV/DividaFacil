import unittest
from datetime import datetime
from decimal import Decimal

from src.models.expense import Expense
from src.services.split_calculator import calculate_portions


def make_base_expense(**overrides):
    """Helper to create a default expense for testing."""
    data = dict(
        id="e1",
        amount=10.0,
        description="Test Expense",
        paid_by="u1",
        split_among=["u1", "u2", "u3"],
        created_by="u1",
        split_type="EQUAL",
        split_values={},
        created_at=datetime.now(),
        installments_count=1,
    )
    data.update(overrides)
    return Expense(**data)


class TestSplitCalculator(unittest.TestCase):
    def test_percentage_split_remainder(self):
        """Test that percentage splits with rounding errors are handled correctly."""
        expense = make_base_expense(
            amount=10.00,
            split_type="PERCENTAGE",
            split_among=["u1", "u2", "u3"],
            split_values={"u1": 33.33, "u2": 33.33, "u3": 33.34},
        )

        portions = calculate_portions(expense)
        self.assertEqual(sum(portions.values()), expense.amount)

if __name__ == "__main__":
    unittest.main()