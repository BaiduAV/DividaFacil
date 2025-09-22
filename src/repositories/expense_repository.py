from sqlalchemy.orm import Session, selectinload
from typing import List, Optional
import uuid

from src.database import ExpenseDB, InstallmentDB, UserDB, expense_split_among
from src.models.expense import Expense, Installment


class ExpenseRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, expense: Expense, group_id: str) -> Expense:
        """Create a new expense in the database."""
        db_expense = ExpenseDB(
            id=expense.id,
            description=expense.description,
            amount=expense.amount,
            paid_by=expense.paid_by,
            created_by=expense.created_by,
            group_id=group_id,
            split_type=expense.split_type,
            split_values=expense.split_values,
            created_at=expense.created_at,
            installments_count=expense.installments_count,
            first_due_date=expense.first_due_date
        )
        self.db.add(db_expense)
        
        # Add split_among relationships
        split_users = self.db.query(UserDB).filter(UserDB.id.in_(expense.split_among)).all()
        db_expense.split_among_users.extend(split_users)
        
        # Add installments
        for installment in expense.installments:
            db_installment = InstallmentDB(
                id=str(uuid.uuid4()),
                expense_id=expense.id,
                number=installment.number,
                amount=installment.amount,
                due_date=installment.due_date,
                paid=installment.paid,
                paid_at=installment.paid_at
            )
            self.db.add(db_installment)
        
        self.db.commit()
        self.db.refresh(db_expense)
        return self._to_domain_model(db_expense)

    def get_by_id(self, expense_id: str) -> Optional[Expense]:
        """Get expense by ID with all relationships loaded."""
        db_expense = self.db.query(ExpenseDB).options(
            selectinload(ExpenseDB.split_among_users),
            selectinload(ExpenseDB.installments)
        ).filter(ExpenseDB.id == expense_id).first()
        return self._to_domain_model(db_expense) if db_expense else None

    def get_by_group_id(self, group_id: str) -> List[Expense]:
        """Get all expenses for a group."""
        db_expenses = self.db.query(ExpenseDB).options(
            selectinload(ExpenseDB.split_among_users),
            selectinload(ExpenseDB.installments)
        ).filter(ExpenseDB.group_id == group_id).all()
        return [self._to_domain_model(db_expense) for db_expense in db_expenses]

    def update(self, expense: Expense) -> Expense:
        """Update an existing expense."""
        db_expense = self.db.query(ExpenseDB).filter(ExpenseDB.id == expense.id).first()
        if not db_expense:
            raise ValueError(f"Expense {expense.id} not found")
        
        # Update basic fields
        db_expense.description = expense.description
        db_expense.amount = expense.amount
        db_expense.paid_by = expense.paid_by
        db_expense.split_type = expense.split_type
        db_expense.split_values = expense.split_values
        db_expense.created_at = expense.created_at
        db_expense.installments_count = expense.installments_count
        db_expense.first_due_date = expense.first_due_date
        
        # Update split_among relationships
        db_expense.split_among_users.clear()
        split_users = self.db.query(UserDB).filter(UserDB.id.in_(expense.split_among)).all()
        db_expense.split_among_users.extend(split_users)
        
        # Update installments
        # Delete existing installments
        self.db.query(InstallmentDB).filter(InstallmentDB.expense_id == expense.id).delete()
        
        # Add new installments
        for installment in expense.installments:
            db_installment = InstallmentDB(
                id=str(uuid.uuid4()),
                expense_id=expense.id,
                number=installment.number,
                amount=installment.amount,
                due_date=installment.due_date,
                paid=installment.paid,
                paid_at=installment.paid_at
            )
            self.db.add(db_installment)
        
        self.db.commit()
        self.db.refresh(db_expense)
        return self._to_domain_model(db_expense)

    def delete(self, expense_id: str) -> bool:
        """Delete expense by ID."""
        db_expense = self.db.query(ExpenseDB).filter(ExpenseDB.id == expense_id).first()
        if db_expense:
            self.db.delete(db_expense)
            self.db.commit()
            return True
        return False

    def pay_installment(self, expense_id: str, installment_number: int) -> bool:
        """Mark an installment as paid."""
        from datetime import datetime
        
        db_installment = self.db.query(InstallmentDB).filter(
            InstallmentDB.expense_id == expense_id,
            InstallmentDB.number == installment_number
        ).first()
        
        if db_installment and not db_installment.paid:
            db_installment.paid = True
            db_installment.paid_at = datetime.now()
            self.db.commit()
            return True
        return False

    def get_by_created_by(self, created_by: str) -> List[Expense]:
        """Get all expenses created by a specific user."""
        db_expenses = self.db.query(ExpenseDB).options(
            selectinload(ExpenseDB.split_among_users),
            selectinload(ExpenseDB.installments)
        ).filter(ExpenseDB.created_by == created_by).all()
        
        return [self._to_domain_model(db_expense) for db_expense in db_expenses]

    def _to_domain_model(self, db_expense: ExpenseDB) -> Expense:
        """Convert database model to domain model."""
        # Convert installments
        installments = [
            Installment(
                number=db_inst.number,
                amount=db_inst.amount,
                due_date=db_inst.due_date,
                paid=db_inst.paid,
                paid_at=db_inst.paid_at
            )
            for db_inst in sorted(db_expense.installments, key=lambda x: x.number)
        ]
        
        # Get split_among user IDs
        split_among = [user.id for user in db_expense.split_among_users]
        
        return Expense(
            id=db_expense.id,
            description=db_expense.description,
            amount=db_expense.amount,
            paid_by=db_expense.paid_by,
            created_by=db_expense.created_by,  # This can be None for legacy data
            split_among=split_among,
            split_type=db_expense.split_type,
            split_values=db_expense.split_values or {},
            created_at=db_expense.created_at,
            installments_count=db_expense.installments_count,
            first_due_date=db_expense.first_due_date,
            installments=installments
        )
