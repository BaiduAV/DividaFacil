"""Service for handling expense-related operations."""

import logging
from decimal import ROUND_HALF_UP, Decimal
from typing import Dict, List

from dateutil.relativedelta import relativedelta

from ..constants import (
    ERROR_INVALID_SPLIT_TYPE,
    ERROR_NO_SPLIT_VALUES,
    ERROR_NO_USERS_TO_SPLIT,
    MIN_BALANCE_THRESHOLD,
    PERCENTAGE_BASE,
    SPLIT_EQUAL,
    SPLIT_EXACT,
    SPLIT_PERCENTAGE,
)
from ..models.expense import Expense
from ..models.group import Group
from ..models.installment import Installment
from ..models.user import User

logger = logging.getLogger(__name__)


class ExpenseCalculationError(Exception):
    """Raised when expense calculation fails."""

    pass


class ExpenseService:
    """Service for handling expense-related operations."""

    @classmethod
    def calculate_balances(cls, expense: Expense, users: Dict[str, User]) -> None:
        """Update user balances based on an expense.

        Args:
            expense: The expense to process
            users: Dictionary of user_id to User objects

        Raises:
            ExpenseCalculationError: If calculation fails
        """
        try:
            if expense.paid_by not in users:
                raise ExpenseCalculationError(f"Payer {expense.paid_by} not found in users")

            payer = users[expense.paid_by]

            # Skip balance calculation for installment expenses - handled separately
            if cls._is_installment_expense(expense):
                return

            portions = cls._calculate_portions(expense)
            cls._update_user_balances(expense, payer, users, portions)

        except Exception as e:
            logger.exception("Error calculating balances for expense %s", expense.id)
            raise ExpenseCalculationError(f"Failed to calculate balances: {str(e)}") from e

    @classmethod
    def _is_installment_expense(cls, expense: Expense) -> bool:
        """Check if expense uses installments."""
        return expense.installments and expense.installments_count > 1

    @classmethod
    def _calculate_portions(cls, expense: Expense) -> Dict[str, Decimal]:
        """Calculate how much each user owes for the expense."""
        amount = Decimal(str(expense.amount))

        if expense.split_type == SPLIT_EQUAL:
            return cls._calculate_equal_split(expense, amount)
        elif expense.split_type == SPLIT_EXACT:
            return cls._calculate_exact_split(expense)
        elif expense.split_type == SPLIT_PERCENTAGE:
            return cls._calculate_percentage_split(expense, amount)
        else:
            raise ExpenseCalculationError(f"{ERROR_INVALID_SPLIT_TYPE}: {expense.split_type}")

    @classmethod
    def _calculate_equal_split(cls, expense: Expense, amount: Decimal) -> Dict[str, Decimal]:
        """Calculate equal split portions."""
        if not expense.split_among:
            raise ExpenseCalculationError(ERROR_NO_USERS_TO_SPLIT)

        per_person = amount / len(expense.split_among)
        portions = {uid: cls._round_decimal(per_person) for uid in expense.split_among}

        # Handle rounding differences
        total_allocated = sum(portions.values())
        diff = amount - total_allocated

        if abs(diff) > 0:
            # Assign remainder to the last non-payer if possible, else payer
            candidates = [uid for uid in expense.split_among if uid != expense.paid_by] or [
                expense.paid_by
            ]
            portions[candidates[-1]] += diff
            portions[candidates[-1]] = cls._round_decimal(portions[candidates[-1]])

        return portions

    @classmethod
    def _calculate_exact_split(cls, expense: Expense) -> Dict[str, Decimal]:
        """Calculate exact split portions."""
        if not expense.split_values:
            raise ExpenseCalculationError(ERROR_NO_SPLIT_VALUES)

        return {
            uid: cls._round_decimal(Decimal(str(amount)))
            for uid, amount in expense.split_values.items()
        }

    @classmethod
    def _calculate_percentage_split(cls, expense: Expense, amount: Decimal) -> Dict[str, Decimal]:
        """Calculate percentage split portions."""
        if not expense.split_values:
            raise ExpenseCalculationError(ERROR_NO_SPLIT_VALUES)

        portions = {}
        for uid, percentage in expense.split_values.items():
            portion_amount = (amount * Decimal(str(percentage))) / PERCENTAGE_BASE
            portions[uid] = cls._round_decimal(portion_amount)

        return portions

    @classmethod
    def _update_user_balances(
        cls, expense: Expense, payer: User, users: Dict[str, User], portions: Dict[str, Decimal]
    ) -> None:
        """Update user balances based on calculated portions."""
        for user_id, amount in portions.items():
            if user_id == expense.paid_by:
                continue

            if user_id not in users:
                logger.warning("User %s not found when updating balances", user_id)
                continue

            amount_float = float(amount)
            payer.update_balance(user_id, amount_float)
            users[user_id].update_balance(expense.paid_by, -amount_float)

    @classmethod
    def _round_decimal(cls, value: Decimal) -> Decimal:
        """Round decimal to appropriate precision."""
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @classmethod
    def simplify_balances(cls, users: Dict[str, User]) -> List[Dict[str, any]]:
        """Simplify the balances between users to minimize transactions.

        Returns a list of transactions needed to settle all balances.
        """
        try:
            balances = cls._calculate_net_balances(users)
            return cls._compute_settlement_transactions(balances)
        except Exception as e:
            logger.exception("Error simplifying balances")
            raise ExpenseCalculationError(f"Failed to simplify balances: {str(e)}") from e

    @classmethod
    def _calculate_net_balances(cls, users: Dict[str, User]) -> Dict[str, Decimal]:
        """Calculate net balance for each user."""
        balances = {}

        for user_id, user in users.items():
            net_balance = Decimal("0.0")
            for _other_id, amount in user.balance.items():
                net_balance += Decimal(str(amount))

            # Only include significant balances
            if abs(net_balance) > MIN_BALANCE_THRESHOLD:
                balances[user_id] = cls._round_decimal(net_balance)

        return balances

    @classmethod
    def _compute_settlement_transactions(cls, balances: Dict[str, Decimal]) -> List[Dict[str, any]]:
        """Compute the minimum transactions needed to settle balances."""
        # Sort users by balance (debtors first, then creditors)
        sorted_balances = sorted(balances.items(), key=lambda x: x[1])

        transactions = []
        i, j = 0, len(sorted_balances) - 1

        while i < j:
            debtor, debt = sorted_balances[i]
            creditor, credit = sorted_balances[j]

            # Calculate the minimum amount to settle
            amount = min(abs(debt), credit)

            if amount > MIN_BALANCE_THRESHOLD:
                transactions.append(
                    {"from": debtor, "to": creditor, "amount": float(cls._round_decimal(amount))}
                )

            # Update balances
            if abs(debt) > credit:
                sorted_balances[i] = (debtor, debt + amount)
                j -= 1
            elif abs(debt) < credit:
                sorted_balances[j] = (creditor, credit - amount)
                i += 1
            else:
                i += 1
                j -= 1

        return transactions

    @classmethod
    def generate_installments(cls, expense: Expense) -> None:
        """Generate installments for an expense if configured."""
        try:
            if expense.installments_count <= 1:
                return

            cls._set_default_first_due_date(expense)
            installment_amounts = cls._calculate_installment_amounts(expense)
            expense.installments = cls._create_installments(expense, installment_amounts)

        except Exception as e:
            logger.exception("Error generating installments for expense %s", expense.id)
            raise ExpenseCalculationError(f"Failed to generate installments: {str(e)}") from e

    @classmethod
    def _set_default_first_due_date(cls, expense: Expense) -> None:
        """Set default first due date if not provided."""
        if not expense.first_due_date:
            expense.first_due_date = expense.created_at

    @classmethod
    def _calculate_installment_amounts(cls, expense: Expense) -> List[Decimal]:
        """Calculate the amount for each installment."""
        total_amount = Decimal(str(expense.amount))
        per_installment = total_amount / expense.installments_count

        # Create list with equal amounts
        amounts = [cls._round_decimal(per_installment)] * expense.installments_count

        # Adjust for rounding differences in the last installment
        total_allocated = sum(amounts)
        diff = total_amount - total_allocated

        if abs(diff) > 0:
            amounts[-1] = cls._round_decimal(amounts[-1] + diff)

        return amounts

    @classmethod
    def _create_installments(cls, expense: Expense, amounts: List[Decimal]) -> List[Installment]:
        """Create installment objects."""
        installments = []
        base_date = expense.first_due_date.date()

        for i, amount in enumerate(amounts):
            due_date = base_date + relativedelta(months=+i)
            installments.append(Installment(number=i + 1, due_date=due_date, amount=float(amount)))

        return installments

    @staticmethod
    def recompute_group_balances(group: Group) -> None:
        """Recompute all user balances in a group from expenses and unpaid installments."""
        # reset balances
        for u in group.members.values():
            u.balance.clear()

        for exp in group.expenses:
            payer = group.members[exp.paid_by]
            # Determine portion per user for this expense
            portions: Dict[str, float] = {}
            if exp.split_type == "EQUAL":
                per_person = exp.amount / len(exp.split_among)
                portions = {uid: round(per_person, 2) for uid in exp.split_among}
                diff = round(exp.amount - sum(portions.values()), 2)
                if abs(diff) > 0:
                    candidates = [uid for uid in exp.split_among if uid != exp.paid_by] or [
                        exp.paid_by
                    ]
                    portions[candidates[-1]] = round(portions.get(candidates[-1], 0.0) + diff, 2)
            elif exp.split_type == "EXACT":
                portions = dict(exp.split_values)
            elif exp.split_type == "PERCENTAGE":
                for uid, pct in exp.split_values.items():
                    portions[uid] = (exp.amount * pct) / 100.0

            if exp.installments_count > 1 and exp.installments:
                # Only count unpaid installments toward balances
                unpaid_ratio = (
                    sum(inst.amount for inst in exp.installments if not inst.paid) / exp.amount
                )
                if unpaid_ratio <= 0:
                    continue
                for uid, amt in portions.items():
                    if uid == exp.paid_by:
                        continue
                    owed = round(amt * unpaid_ratio, 2)
                    payer.update_balance(uid, owed)
                    group.members[uid].update_balance(exp.paid_by, -owed)
            else:
                # Full amount counts
                for uid, amt in portions.items():
                    if uid == exp.paid_by:
                        continue
                    owed = round(amt, 2)
                    payer.update_balance(uid, owed)
                    group.members[uid].update_balance(exp.paid_by, -owed)

    @staticmethod
    def compute_monthly_analysis(group: Group) -> Dict[str, Dict[str, float]]:
        """Compute month-by-month net amounts per user in the group.
        Returns mapping: 'YYYY-MM' -> { user_id: net_amount }
        Positive = user is owed, Negative = user owes.
        """
        monthly: Dict[str, Dict[str, float]] = {}

        def add(month: str, user_id: str, amount: float):
            if month not in monthly:
                monthly[month] = {}
            monthly[month][user_id] = monthly[month].get(user_id, 0.0) + amount

        for exp in group.expenses:
            # Determine portions per user
            portions: Dict[str, float] = {}
            if exp.split_type == "EQUAL":
                per_person = exp.amount / len(exp.split_among)
                for uid in exp.split_among:
                    portions[uid] = per_person
            elif exp.split_type == "EXACT":
                portions = dict(exp.split_values)
            elif exp.split_type == "PERCENTAGE":
                for uid, pct in exp.split_values.items():
                    portions[uid] = (exp.amount * pct) / 100.0

            if exp.installments_count > 1 and exp.installments:
                total = exp.amount
                for inst in exp.installments:
                    if inst.paid:
                        # Analysis is about obligation timing; include paid installments in their due month
                        pass
                    month = inst.due_date.strftime("%Y-%m")
                    ratio = inst.amount / total if total else 0
                    for uid, amt in portions.items():
                        if uid == exp.paid_by:
                            continue
                        owed = amt * ratio
                        add(month, exp.paid_by, owed)
                        add(month, uid, -owed)
            else:
                month = exp.created_at.strftime("%Y-%m")
                for uid, amt in portions.items():
                    if uid == exp.paid_by:
                        continue
                    add(month, exp.paid_by, amt)
                    add(month, uid, -amt)

        # Round
        for m in monthly:
            for uid in monthly[m]:
                monthly[m][uid] = round(monthly[m][uid], 2)
        return monthly

    @staticmethod
    def compute_monthly_transactions(monthly: Dict[str, Dict[str, float]]) -> Dict[str, List[dict]]:
        """For each month, compute simplified settlement transactions from the
        monthly net balances mapping produced by compute_monthly_analysis().

        Args:
            monthly: mapping 'YYYY-MM' -> { user_id: net_amount }

        Returns:
            mapping 'YYYY-MM' -> [ { 'from': uid, 'to': uid, 'amount': float } ]
        """
        result: Dict[str, List[dict]] = {}

        for ym, per_user in monthly.items():
            # Build balances list similar to simplify_balances
            balances = {uid: round(val, 2) for uid, val in per_user.items() if abs(val) > 0.01}
            sorted_balances = sorted(balances.items(), key=lambda x: x[1])

            tx: List[dict] = []
            i, j = 0, len(sorted_balances) - 1
            while i < j:
                debtor, debt = sorted_balances[i]
                creditor, credit = sorted_balances[j]
                amount = min(abs(debt), credit)
                if amount > 0.01:
                    tx.append({"from": debtor, "to": creditor, "amount": round(amount, 2)})
                if abs(debt) > credit:
                    sorted_balances[i] = (debtor, debt + amount)
                    j -= 1
                elif abs(debt) < credit:
                    sorted_balances[j] = (creditor, credit - amount)
                    i += 1
                else:
                    i += 1
                    j -= 1
            result[ym] = tx

        return result

    @staticmethod
    def compute_expense_remaining(expense: Expense, group: Group) -> Dict[str, float]:
        """Compute remaining amount per user for a single expense that is still owed to the payer.

        Returns mapping user_id -> amount_owed_to_payer (only for users different from payer, values >= 0).
        For non-installment expenses, the full share is considered remaining (no partial payments supported).
        For installment expenses, only unpaid installments ratio counts.
        """
        portions: Dict[str, float] = {}
        if expense.split_type == "EQUAL":
            per_person = expense.amount / len(expense.split_among)
            portions = {uid: round(per_person, 2) for uid in expense.split_among}
            diff = round(expense.amount - sum(portions.values()), 2)
            if abs(diff) > 0:
                candidates = [uid for uid in expense.split_among if uid != expense.paid_by] or [
                    expense.paid_by
                ]
                portions[candidates[-1]] = round(portions.get(candidates[-1], 0.0) + diff, 2)
        elif expense.split_type == "EXACT":
            portions = dict(expense.split_values)
        elif expense.split_type == "PERCENTAGE":
            for uid, pct in expense.split_values.items():
                portions[uid] = (expense.amount * pct) / 100.0

        remaining: Dict[str, float] = {}
        if expense.installments_count > 1 and expense.installments:
            unpaid_ratio = (
                sum(inst.amount for inst in expense.installments if not inst.paid) / expense.amount
            )
            if unpaid_ratio <= 0:
                return {}
            for uid, amt in portions.items():
                if uid == expense.paid_by:
                    continue
                owed = round(amt * unpaid_ratio, 2)
                if owed > 0.01:
                    remaining[uid] = owed
        else:
            for uid, amt in portions.items():
                if uid == expense.paid_by:
                    continue
                owed = round(amt, 2)
                if owed > 0.01:
                    remaining[uid] = owed
        return remaining
