"""Balance calculation service for expense splitting."""

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List

from ..models.expense import Expense
from ..models.user import User


@dataclass
class Balance:
    """Represents a balance between two users."""

    id: str
    from_user: User
    to_user: User
    amount: float  # Positive means from_user receives, negative means from_user owes


@dataclass
class SettlementSuggestion:
    """Represents a suggested settlement to minimize transactions."""

    id: str
    from_user: User
    to_user: User
    amount: float


class BalanceService:
    """Service for calculating balances and settlement suggestions."""

    def calculate_group_balances(
        self, expenses: List[Expense], users: Dict[str, User]
    ) -> List[Balance]:
        """
        Calculate balances between all users in a group.

        Args:
            expenses: List of expenses in the group
            users: Dictionary of user_id -> User objects

        Returns:
            List of Balance objects representing who owes whom
        """
        # Track net balances for each user (positive = they are owed, negative = they owe)
        user_balances = defaultdict(float)

        for expense in expenses:
            # Calculate how much each person should pay
            split_amounts = self._calculate_split_amounts(expense)

            # The person who paid gets credited
            user_balances[expense.paid_by] += expense.amount

            # Each person in the split gets debited their share
            for user_id, amount in split_amounts.items():
                user_balances[user_id] -= amount

        # Convert net balances to pairwise balances
        balances = []
        user_ids = list(user_balances.keys())

        for i, user1_id in enumerate(user_ids):
            for user2_id in user_ids[i + 1 :]:
                balance1 = user_balances[user1_id]
                balance2 = user_balances[user2_id]

                # Calculate net balance between these two users
                net_balance = balance1 - balance2

                if abs(net_balance) > 0.01:  # Only include non-zero balances
                    balance = Balance(
                        id=f"{user1_id}_{user2_id}",
                        from_user=users[user1_id],
                        to_user=users[user2_id],
                        amount=net_balance / 2,  # Split the difference
                    )
                    balances.append(balance)

        return balances

    def calculate_user_summary(self, user_id: str, expenses: List[Expense]) -> Dict[str, float]:
        """
        Calculate summary balances for a specific user.

        Args:
            user_id: ID of the user
            expenses: List of expenses involving the user

        Returns:
            Dictionary with 'owes', 'owed', and 'total_spent' amounts
        """
        total_paid = 0.0
        total_share = 0.0

        for expense in expenses:
            # Calculate user's share of this expense
            split_amounts = self._calculate_split_amounts(expense)
            user_share = split_amounts.get(user_id, 0.0)
            total_share += user_share

            # Add amount if user paid for this expense
            if expense.paid_by == user_id:
                total_paid += expense.amount

        net_balance = total_paid - total_share

        return {
            "owes": max(0, -net_balance),
            "owed": max(0, net_balance),
            "total_spent": total_paid,
            "total_share": total_share,
        }

    def generate_settlement_suggestions(
        self, balances: List[Balance]
    ) -> List[SettlementSuggestion]:
        """
        Generate optimal settlement suggestions to minimize number of transactions.

        Args:
            balances: List of current balances

        Returns:
            List of settlement suggestions
        """
        # Create a net balance map for each user
        net_balances = defaultdict(float)
        users_map = {}

        for balance in balances:
            if balance.amount > 0:
                # from_user is owed money
                net_balances[balance.from_user.id] += balance.amount
                net_balances[balance.to_user.id] -= balance.amount
            else:
                # from_user owes money
                net_balances[balance.from_user.id] += balance.amount
                net_balances[balance.to_user.id] -= balance.amount

            users_map[balance.from_user.id] = balance.from_user
            users_map[balance.to_user.id] = balance.to_user

        # Separate creditors (positive balance) and debtors (negative balance)
        creditors = [(user_id, amount) for user_id, amount in net_balances.items() if amount > 0.01]
        debtors = [(user_id, -amount) for user_id, amount in net_balances.items() if amount < -0.01]

        suggestions = []
        suggestion_id = 1

        # Match debtors with creditors to minimize transactions
        i, j = 0, 0
        while i < len(debtors) and j < len(creditors):
            debtor_id, debt_amount = debtors[i]
            creditor_id, credit_amount = creditors[j]

            # Settle the smaller amount
            settle_amount = min(debt_amount, credit_amount)

            if settle_amount > 0.01:
                suggestion = SettlementSuggestion(
                    id=str(suggestion_id),
                    from_user=users_map[debtor_id],
                    to_user=users_map[creditor_id],
                    amount=settle_amount,
                )
                suggestions.append(suggestion)
                suggestion_id += 1

            # Update remaining amounts
            debtors[i] = (debtor_id, debt_amount - settle_amount)
            creditors[j] = (creditor_id, credit_amount - settle_amount)

            # Move to next debtor/creditor if current one is settled
            if debtors[i][1] <= 0.01:
                i += 1
            if creditors[j][1] <= 0.01:
                j += 1

        return suggestions

    def _calculate_split_amounts(self, expense: Expense) -> Dict[str, float]:
        """
        Calculate how much each person should pay for an expense.

        Args:
            expense: The expense to calculate splits for

        Returns:
            Dictionary mapping user_id to amount they should pay
        """
        split_amounts = {}

        if expense.split_type == "EQUAL":
            # Split equally among all people
            amount_per_person = expense.amount / len(expense.split_among)
            for user_id in expense.split_among:
                split_amounts[user_id] = amount_per_person

        elif expense.split_type == "EXACT":
            # Use exact amounts specified
            for user_id in expense.split_among:
                split_amounts[user_id] = expense.split_values.get(user_id, 0.0)

        elif expense.split_type == "PERCENTAGE":
            # Calculate based on percentages
            for user_id in expense.split_among:
                percentage = expense.split_values.get(user_id, 0.0)
                split_amounts[user_id] = (expense.amount * percentage) / 100.0

        return split_amounts

    def calculate_group_statistics(
        self, expenses: List[Expense], users: Dict[str, User]
    ) -> Dict[str, any]:
        """
        Calculate various statistics for a group.

        Args:
            expenses: List of expenses in the group
            users: Dictionary of user_id -> User objects

        Returns:
            Dictionary with various statistics
        """
        if not expenses:
            return {
                "total_expenses": 0.0,
                "average_expense": 0.0,
                "total_transactions": 0,
                "most_active_user": None,
                "largest_expense": None,
                "pending_settlements": 0,
            }

        total_amount = sum(expense.amount for expense in expenses)
        average_expense = total_amount / len(expenses)

        # Count expenses per user
        user_expense_counts = defaultdict(int)
        for expense in expenses:
            user_expense_counts[expense.paid_by] += 1

        most_active_user_id = max(user_expense_counts.keys(), key=lambda x: user_expense_counts[x])
        most_active_user = users.get(most_active_user_id)

        # Find largest expense
        largest_expense = max(expenses, key=lambda x: x.amount)

        # Calculate pending settlements
        balances = self.calculate_group_balances(expenses, users)
        pending_settlements = len([b for b in balances if abs(b.amount) > 0.01])

        return {
            "total_expenses": total_amount,
            "average_expense": average_expense,
            "total_transactions": len(expenses),
            "most_active_user": most_active_user,
            "largest_expense": largest_expense,
            "pending_settlements": pending_settlements,
        }
