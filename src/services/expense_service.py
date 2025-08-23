from typing import Dict, List
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from ..models.expense import Expense
from ..models.user import User
from ..models.group import Group
from ..models.installment import Installment

class ExpenseService:
    """Service for handling expense-related operations."""
    
    @staticmethod
    def calculate_balances(expense: Expense, users: Dict[str, User]) -> None:
        """Update user balances based on an expense.
        
        Args:
            expense: The expense to process
            users: Dictionary of user_id to User objects
        """
        payer = users[expense.paid_by]
        
        if expense.installments and expense.installments_count > 1:
            # When using installments, we do not mutate balances here. Balances are recomputed
            # from unpaid installments via recompute_group_balances().
            return
        
        if expense.split_type == 'EQUAL':
            per_person = expense.amount / len(expense.split_among)
            portions = {uid: round(per_person, 2) for uid in expense.split_among}
            diff = round(expense.amount - sum(portions.values()), 2)
            if abs(diff) > 0:
                # assign remainder to the last non-payer if possible, else payer
                candidates = [uid for uid in expense.split_among if uid != expense.paid_by] or [expense.paid_by]
                portions[candidates[-1]] = round(portions.get(candidates[-1], 0.0) + diff, 2)
            for user_id, amt in portions.items():
                if user_id == expense.paid_by:
                    continue
                payer.update_balance(user_id, amt)
                users[user_id].update_balance(expense.paid_by, -amt)
                
        elif expense.split_type == 'EXACT':
            for user_id, amount in expense.split_values.items():
                if user_id == expense.paid_by:
                    continue
                amt = round(amount, 2)
                payer.update_balance(user_id, amt)
                users[user_id].update_balance(expense.paid_by, -amt)
                
        elif expense.split_type == 'PERCENTAGE':
            for user_id, percentage in expense.split_values.items():
                if user_id == expense.paid_by:
                    continue
                amount = round((expense.amount * percentage) / 100.0, 2)
                payer.update_balance(user_id, amount)
                users[user_id].update_balance(expense.paid_by, -amount)

    @staticmethod
    def simplify_balances(users: Dict[str, User]) -> List[dict]:
        """Simplify the balances between users to minimize transactions.
        
        Returns a list of transactions needed to settle all balances.
        """
        balances = {}
        
        # Calculate net balance for each user
        for user_id, user in users.items():
            net_balance = 0.0
            for other_id, amount in user.balance.items():
                net_balance += amount
            if abs(net_balance) > 0.01:  # Ignore very small balances
                balances[user_id] = round(net_balance, 2)
        
        # Sort users by balance (debtors first, then creditors)
        sorted_balances = sorted(balances.items(), key=lambda x: x[1])
        
        transactions = []
        i, j = 0, len(sorted_balances) - 1
        
        while i < j:
            debtor, debt = sorted_balances[i]
            creditor, credit = sorted_balances[j]
            
            # Calculate the minimum amount to settle
            amount = min(abs(debt), credit)
            
            if amount > 0.01:  # Only add if the amount is significant
                transactions.append({
                    'from': debtor,
                    'to': creditor,
                    'amount': round(amount, 2)
                })
            
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

    @staticmethod
    def generate_installments(expense: Expense) -> None:
        """Generate installments for an expense if configured.
        Distributes the amount evenly across installments (last installment adjusts rounding).
        """
        if expense.installments_count <= 1:
            return
        if not expense.first_due_date:
            # default: first due date one month from created_at
            expense.first_due_date = expense.created_at
        per = round(expense.amount / expense.installments_count, 2)
        amounts = [per] * expense.installments_count
        diff = round(expense.amount - sum(amounts), 2)
        if abs(diff) > 0:
            amounts[-1] = round(amounts[-1] + diff, 2)
        expense.installments = []
        base_date = expense.first_due_date.date()
        for i in range(expense.installments_count):
            # Keep the same day-of-month across months; handle variable month lengths
            due = base_date + relativedelta(months=+i)
            expense.installments.append(Installment(number=i + 1, due_date=due, amount=amounts[i]))

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
            if exp.split_type == 'EQUAL':
                per_person = exp.amount / len(exp.split_among)
                portions = {uid: round(per_person, 2) for uid in exp.split_among}
                diff = round(exp.amount - sum(portions.values()), 2)
                if abs(diff) > 0:
                    candidates = [uid for uid in exp.split_among if uid != exp.paid_by] or [exp.paid_by]
                    portions[candidates[-1]] = round(portions.get(candidates[-1], 0.0) + diff, 2)
            elif exp.split_type == 'EXACT':
                portions = dict(exp.split_values)
            elif exp.split_type == 'PERCENTAGE':
                for uid, pct in exp.split_values.items():
                    portions[uid] = (exp.amount * pct) / 100.0

            if exp.installments_count > 1 and exp.installments:
                # Only count unpaid installments toward balances
                unpaid_ratio = sum(inst.amount for inst in exp.installments if not inst.paid) / exp.amount
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
            if exp.split_type == 'EQUAL':
                per_person = exp.amount / len(exp.split_among)
                for uid in exp.split_among:
                    portions[uid] = per_person
            elif exp.split_type == 'EXACT':
                portions = dict(exp.split_values)
            elif exp.split_type == 'PERCENTAGE':
                for uid, pct in exp.split_values.items():
                    portions[uid] = (exp.amount * pct) / 100.0

            if exp.installments_count > 1 and exp.installments:
                total = exp.amount
                for inst in exp.installments:
                    if inst.paid:
                        # Analysis is about obligation timing; include paid installments in their due month
                        pass
                    month = inst.due_date.strftime('%Y-%m')
                    ratio = inst.amount / total if total else 0
                    for uid, amt in portions.items():
                        if uid == exp.paid_by:
                            continue
                        owed = amt * ratio
                        add(month, exp.paid_by, owed)
                        add(month, uid, -owed)
            else:
                month = exp.created_at.strftime('%Y-%m')
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
                    tx.append({'from': debtor, 'to': creditor, 'amount': round(amount, 2)})
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
        if expense.split_type == 'EQUAL':
            per_person = expense.amount / len(expense.split_among)
            portions = {uid: round(per_person, 2) for uid in expense.split_among}
            diff = round(expense.amount - sum(portions.values()), 2)
            if abs(diff) > 0:
                candidates = [uid for uid in expense.split_among if uid != expense.paid_by] or [expense.paid_by]
                portions[candidates[-1]] = round(portions.get(candidates[-1], 0.0) + diff, 2)
        elif expense.split_type == 'EXACT':
            portions = dict(expense.split_values)
        elif expense.split_type == 'PERCENTAGE':
            for uid, pct in expense.split_values.items():
                portions[uid] = (expense.amount * pct) / 100.0

        remaining: Dict[str, float] = {}
        if expense.installments_count > 1 and expense.installments:
            unpaid_ratio = sum(inst.amount for inst in expense.installments if not inst.paid) / expense.amount
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
