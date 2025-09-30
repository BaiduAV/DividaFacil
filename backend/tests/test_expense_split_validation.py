from datetime import datetime
import pytest

from src.models.expense import Expense


def make_base_expense(**overrides):
    data = dict(
        id="e1",
        amount=100.0,
        description="Test",
        paid_by="u1",
        split_among=["u1", "u2"],
        created_by="u1",
        split_type="EQUAL",
        split_values={},
        created_at=datetime.now(),
        installments_count=1,
    )
    data.update(overrides)
    return Expense(**data)


def test_percentage_split_must_total_100():
    exp = make_base_expense(
        split_type="PERCENTAGE",
        split_values={"u1": 40.0, "u2": 50.0},  # 90 total
    )
    with pytest.raises(ValueError):
        exp.validate_split()


def test_exact_split_must_match_amount():
    exp = make_base_expense(
        split_type="EXACT",
        split_values={"u1": 30.0, "u2": 50.0},  # 80 vs 100
    )
    with pytest.raises(ValueError):
        exp.validate_split()


def test_equal_split_rejects_manual_values():
    exp = make_base_expense(
        split_type="EQUAL",
        split_values={"u1": 10.0},
    )
    with pytest.raises(ValueError):
        exp.validate_split()


def test_valid_percentage():
    exp = make_base_expense(
        split_type="PERCENTAGE",
        split_values={"u1": 40.0, "u2": 60.0},
    )
    assert exp.validate_split() is True


def test_valid_exact():
    exp = make_base_expense(
        split_type="EXACT",
        split_values={"u1": 30.0, "u2": 70.0},
    )
    assert exp.validate_split() is True
