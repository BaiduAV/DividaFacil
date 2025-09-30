from src.database import SessionLocal
from src.services.database_service import DatabaseService
from src.services.expense_service import ExpenseService
from src.repositories.user_repository import UserRepository
from src.schemas.group import GroupResponse


def test_groups_api_logic():
    """Assert core invariants of groups aggregation logic without print debugging."""
    with SessionLocal() as db:
        user_repo = UserRepository(db)
        test_user = user_repo.get_by_email("test@example.com")
        assert test_user is not None, "Seed user test@example.com must exist for this test"

    all_groups = DatabaseService.get_all_groups()
    assert isinstance(all_groups, dict)

    user_groups = [g for g in all_groups.values() if test_user.id in g.members]

    for group in user_groups:
        # Recompute balances and ensure no exception
        ExpenseService.recompute_group_balances(group)
        DatabaseService.update_user_balances(group.members)
        # Sum of balances across users for each peer pair should net to ~0
        for uid, user in group.members.items():
            for other_id, amount in user.balance.items():
                if other_id in group.members:
                    reverse = group.members[other_id].balance.get(uid, 0)
                    # amounts should be opposite signs within tolerance
                    assert round(amount + reverse, 2) == 0, "Balances must be symmetric"

    responses = [GroupResponse.from_group(g) for g in user_groups]
    for resp in responses:
        # Basic structural expectations
        assert resp.id
        assert resp.name
        # Expenses in response should match underlying group length
        original = next(g for g in user_groups if g.id == resp.id)
        assert len(resp.expenses) == len(original.expenses)
