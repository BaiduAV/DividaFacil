from datetime import datetime, date

from src.models.user import User
from src.models.group import Group
from src.models.expense import Expense
from src.services.expense_service import ExpenseService


def mk_users(n=3):
    users = {}
    for i in range(1, n + 1):
        u = User(id=str(i), name=f"U{i}", email=f"u{i}@x.com")
        users[u.id] = u
    return users


def test_equal_split_simple():
    users = mk_users(3)
    g = Group(id="g", name="G", members=users)
    e = Expense(
        id="e1",
        amount=100.0,
        description="d",
        paid_by="1",
        split_among=["1", "2", "3"],
        split_type="EQUAL",
        created_at=datetime(2025, 1, 10),
    )
    g.add_expense(e)
    ExpenseService.recompute_group_balances(g)

    vals = {
        round(users["1"].balance.get("2", 0), 2),
        round(users["1"].balance.get("3", 0), 2),
    }
    assert vals == {33.33, 33.34}
    # contrapartidas negativas
    neg_vals = {
        round(users["2"].balance.get("1", 0), 2),
        round(users["3"].balance.get("1", 0), 2),
    }
    assert neg_vals == {-33.33, -33.34}


def test_exact_split_validation_and_balances():
    users = mk_users(2)
    g = Group(id="g", name="G", members=users)
    e = Expense(
        id="e1",
        amount=31.0,
        description="d",
        paid_by="1",
        split_among=["1", "2"],
        split_type="EXACT",
        split_values={"1": 10.5, "2": 20.5},
        created_at=datetime(2025, 1, 10),
    )
    g.add_expense(e)
    ExpenseService.recompute_group_balances(g)

    assert users["1"].balance.get("2") == 20.5
    assert users["2"].balance.get("1") == -20.5


def test_percentage_split_and_rounding():
    users = mk_users(3)
    g = Group(id="g", name="G", members=users)
    e = Expense(
        id="e1",
        amount=100.0,
        description="d",
        paid_by="1",
        split_among=["1", "2", "3"],
        split_type="PERCENTAGE",
        split_values={"1": 0, "2": 33.33, "3": 66.67},
        created_at=datetime(2025, 1, 10),
    )
    g.add_expense(e)
    ExpenseService.recompute_group_balances(g)

    assert users["1"].balance.get("2") == 33.33
    assert users["1"].balance.get("3") == 66.67
    assert users["2"].balance.get("1") == -33.33
    assert users["3"].balance.get("1") == -66.67


def test_installments_remaining_and_balances():
    users = mk_users(2)
    g = Group(id="g", name="G", members=users)

    e = Expense(
        id="e1",
        amount=300.0,
        description="parcelado",
        paid_by="1",
        split_among=["1", "2"],
        split_type="EQUAL",
        installments_count=3,
        created_at=datetime(2025, 1, 1),
        first_due_date=datetime(2025, 1, 10),
    )
    ExpenseService.generate_installments(e)
    # Marcar a primeira como paga
    e.installments[0].paid = True
    g.add_expense(e)

    rem = ExpenseService.compute_expense_remaining(e, g)
    # Restante 200, metade do usuário 2
    assert rem["2"] == 100.0

    ExpenseService.recompute_group_balances(g)
    # Saldos só consideram parcelas não pagas (200) -> metade: 100
    assert users["1"].balance.get("2") == 100.0
    assert users["2"].balance.get("1") == -100.0


def test_monthly_analysis_and_transactions():
    users = mk_users(2)
    g = Group(id="g", name="G", members=users)

    e1 = Expense(
        id="e1",
        amount=100.0,
        description="jan",
        paid_by="1",
        split_among=["1", "2"],
        split_type="EQUAL",
        created_at=datetime(2025, 1, 5),
    )
    e2 = Expense(
        id="e2",
        amount=60.0,
        description="fev",
        paid_by="2",
        split_among=["1", "2"],
        split_type="EQUAL",
        created_at=datetime(2025, 2, 10),
    )
    g.add_expense(e1)
    g.add_expense(e2)

    monthly = ExpenseService.compute_monthly_analysis(g)
    tx = ExpenseService.compute_monthly_transactions(monthly)

    # Em jan, U1 pagou 100 dividido por 2 -> U2 deve 50
    assert monthly["2025-01"]["1"] == 50.0
    assert monthly["2025-01"]["2"] == -50.0
    # Em fev, U2 pagou 60 dividido por 2 -> U1 deve 30
    assert monthly["2025-02"]["1"] == -30.0
    assert monthly["2025-02"]["2"] == 30.0

    # Simplificação de transações por mês deve resultar em transferências diretas
    assert tx["2025-01"] == [{"from": "2", "to": "1", "amount": 50.0}]
    assert tx["2025-02"] == [{"from": "1", "to": "2", "amount": 30.0}]


def test_equal_split_payer_not_in_split():
    users = mk_users(3)
    g = Group(id="g", name="G", members=users)
    # Payer is 1, but only 2 and 3 are in split_among
    e = Expense(
        id="e1",
        amount=90.0,
        description="d",
        paid_by="1",
        split_among=["2", "3"],
        split_type="EQUAL",
        created_at=datetime(2025, 1, 10),
    )
    g.add_expense(e)
    ExpenseService.recompute_group_balances(g)
    # Each owes 45 to payer
    assert users["1"].balance.get("2") == 45.0
    assert users["1"].balance.get("3") == 45.0
    assert users["2"].balance.get("1") == -45.0
    assert users["3"].balance.get("1") == -45.0


def test_equal_split_single_participant_no_balance():
    users = mk_users(1)
    g = Group(id="g", name="G", members=users)
    e = Expense(
        id="e1",
        amount=123.45,
        description="solo",
        paid_by="1",
        split_among=["1"],
        split_type="EQUAL",
        created_at=datetime(2025, 1, 10),
    )
    g.add_expense(e)
    ExpenseService.recompute_group_balances(g)
    # No balances between different users
    assert users["1"].balance == {}


def test_exact_with_payer_portion_ignored_in_balances():
    users = mk_users(2)
    g = Group(id="g", name="G", members=users)
    e = Expense(
        id="e1",
        amount=40.0,
        description="d",
        paid_by="1",
        split_among=["1", "2"],
        split_type="EXACT",
        split_values={"1": 10.0, "2": 30.0},
        created_at=datetime(2025, 1, 10),
    )
    g.add_expense(e)
    ExpenseService.recompute_group_balances(g)
    # Payer's own portion shouldn't appear as balance; only user 2 owes 30
    assert users["1"].balance.get("2") == 30.0
    assert users["2"].balance.get("1") == -30.0


def test_installments_all_paid_zero_remaining_and_balances():
    users = mk_users(2)
    g = Group(id="g", name="G", members=users)
    e = Expense(
        id="e1",
        amount=120.0,
        description="parcelas",
        paid_by="1",
        split_among=["1", "2"],
        split_type="EQUAL",
        installments_count=3,
        created_at=datetime(2025, 1, 1),
        first_due_date=datetime(2025, 1, 10),
    )
    ExpenseService.generate_installments(e)
    # Mark all as paid
    for inst in e.installments:
        inst.paid = True
    g.add_expense(e)
    # Remaining should be empty and balances should be zeroed
    rem = ExpenseService.compute_expense_remaining(e, g)
    assert rem == {}
    ExpenseService.recompute_group_balances(g)
    assert users["1"].balance.get("2") in (None, 0)
    assert users["2"].balance.get("1") in (None, 0)


def test_simplify_balances_ignores_tiny_net_values():
    users = mk_users(3)
    g = Group(id="g", name="G", members=users)
    # Create expense with tiny per-person shares that round to 0.01
    e = Expense(
        id="e1",
        amount=0.03,
        description="tiny",
        paid_by="1",
        split_among=["1", "2", "3"],
        split_type="EQUAL",
        created_at=datetime(2025, 1, 10),
    )
    g.add_expense(e)
    ExpenseService.recompute_group_balances(g)
    tx = ExpenseService.simplify_balances(g.members)
    # Debtors each have -0.01 which are ignored by simplifier (> 0.01 threshold), so no tx
    assert tx == []


def test_generate_installments_end_of_month_dates():
    users = mk_users(2)
    g = Group(id="g", name="G", members=users)
    # Start on Jan 31, check that due dates advance keeping end-of-month appropriately
    e = Expense(
        id="e1",
        amount=300.0,
        description="eom",
        paid_by="1",
        split_among=["1", "2"],
        split_type="EQUAL",
        installments_count=3,
        created_at=datetime(2025, 1, 31),
        first_due_date=datetime(2025, 1, 31),
    )
    ExpenseService.generate_installments(e)
    # Expect: 2025-01-31, 2025-02-28, 2025-03-31
    due_dates = [inst.due_date.isoformat() for inst in e.installments]
    assert due_dates == ["2025-01-31", "2025-02-28", "2025-03-31"]


def test_percentage_boundaries_tolerance_in_recompute():
    users = mk_users(2)
    g = Group(id="g", name="G", members=users)
    # Sum is 100.01 -> service uses given values; balances should be computed from percentages
    e = Expense(
        id="e1",
        amount=100.0,
        description="pct",
        paid_by="1",
        split_among=["1", "2"],
        split_type="PERCENTAGE",
        split_values={"1": 50.0, "2": 50.01},
        created_at=datetime(2025, 1, 10),
    )
    g.add_expense(e)
    ExpenseService.recompute_group_balances(g)
    # User2 owes 50.01
    assert users["1"].balance.get("2") == 50.01
    assert users["2"].balance.get("1") == -50.01


def test_monthly_analysis_empty_group_returns_empty():
    g = Group(id="g", name="G", members={})
    monthly = ExpenseService.compute_monthly_analysis(g)
    tx = ExpenseService.compute_monthly_transactions(monthly)
    assert monthly == {}
    assert tx == {}


def test_exact_with_zero_and_missing_values():
    users = mk_users(3)
    g = Group(id="g", name="G", members=users)
    # split_among has all three, but split_values only includes 2 and 3
    e = Expense(
        id="e1",
        amount=50.0,
        description="exact zeros/missing",
        paid_by="1",
        split_among=["1", "2", "3"],
        split_type="EXACT",
        split_values={"2": 0.0, "3": 50.0},
        created_at=datetime(2025, 1, 10),
    )
    g.add_expense(e)
    ExpenseService.recompute_group_balances(g)
    # User 2 owes nothing; user 3 owes full 50
    assert users["1"].balance.get("2", 0) in (None, 0)
    assert users["1"].balance.get("3") == 50.0
    assert users["3"].balance.get("1") == -50.0
