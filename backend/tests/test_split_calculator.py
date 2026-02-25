from datetime import datetime
import pytest

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


def test_percentage_split_remainder():
    """Test that percentage splits with rounding errors are handled correctly."""
    expense = make_base_expense(
        amount=10.00,
        split_type="PERCENTAGE",
        split_among=["u1", "u2", "u3"],
        split_values={"u1": 33.33, "u2": 33.33, "u3": 33.34},
    )

    portions = calculate_portions(expense)
    assert sum(portions.values()) == expense.amount


def test_equal_split_no_remainder():
    """Test a simple equal split where the amount is perfectly divisible."""
    expense = make_base_expense(
        amount=10.00,
        split_type="EQUAL",
        split_among=["u1", "u2"],
    )
    portions = calculate_portions(expense)
    assert portions == {"u1": 5.0, "u2": 5.0}


def test_equal_split_with_remainder_to_non_payer():
    """Test equal split with rounding remainder assigned to a non-payer."""
    expense = make_base_expense(
        amount=10.00,
        split_type="EQUAL",
        paid_by="u1",
        split_among=["u1", "u2", "u3"],
    )
    # 10 / 3 = 3.3333... -> 3.33 each, remainder 0.01.
    # Non-payers are u2, u3. Last one is u3.
    portions = calculate_portions(expense)
    assert portions == {"u1": 3.33, "u2": 3.33, "u3": 3.34}
    assert sum(portions.values()) == 10.00


def test_equal_split_with_remainder_to_payer():
    """Test equal split with remainder assigned to payer if they are the only participant."""
    expense = make_base_expense(
        amount=10.00,
        split_type="EQUAL",
        paid_by="u1",
        split_among=["u1"],
    )
    portions = calculate_portions(expense)
    assert portions == {"u1": 10.00}


def test_equal_split_empty_users():
    """Test that equal split raises ValueError if no users are specified."""
    expense = make_base_expense(
        amount=10.00,
        split_type="EQUAL",
        split_among=[],
    )
    with pytest.raises(ValueError, match="No users to split among"):
        calculate_portions(expense)


def test_exact_split_success():
    """Test standard exact split."""
    expense = make_base_expense(
        amount=10.00,
        split_type="EXACT",
        split_values={"u1": 4.50, "u2": 5.50},
    )
    portions = calculate_portions(expense)
    assert portions == {"u1": 4.5, "u2": 5.5}


def test_exact_split_empty_values():
    """Test that exact split raises ValueError if no split values are provided."""
    expense = make_base_expense(
        amount=10.00,
        split_type="EXACT",
        split_values={},
    )
    with pytest.raises(ValueError, match="No split values provided"):
        calculate_portions(expense)


def test_invalid_split_type():
    """Test that an invalid split type raises a ValueError."""
    expense = make_base_expense(
        amount=10.00,
        split_type="INVALID",
    )
    with pytest.raises(ValueError, match="Invalid split type"):
        calculate_portions(expense)


def test_percentage_split_simple():
    """Test standard percentage split with no rounding issues."""
    expense = make_base_expense(
        amount=10.00,
        split_type="PERCENTAGE",
        split_values={"u1": 50.0, "u2": 50.0},
    )
    portions = calculate_portions(expense)
    assert portions == {"u1": 5.0, "u2": 5.0}


def test_percentage_split_empty_values():
    """Test that percentage split raises ValueError if no split values are provided."""
    expense = make_base_expense(
        amount=10.00,
        split_type="PERCENTAGE",
        split_values={},
    )
    with pytest.raises(ValueError, match="No split values provided"):
        calculate_portions(expense)
