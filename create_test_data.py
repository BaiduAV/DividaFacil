#!/usr/bin/env python3
"""
Test script to create sample data for testing the notification system
"""

import sys
from pathlib import Path
from datetime import datetime, date, timedelta

# Ensure project root is in sys.path for module imports
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.services.database_service import DatabaseService
from src.models.expense import Expense
from src.services.expense_service import ExpenseService

def create_test_data():
    """Create test users, groups, and expenses with overdue installments"""
    
    print("🔧 Creating test data...")
    
    # Initialize database
    DatabaseService.initialize()
    
    # Create test users
    user1 = DatabaseService.create_user("Alice Silva", "alice@example.com")
    user2 = DatabaseService.create_user("Bob Santos", "bob@example.com")
    user3 = DatabaseService.create_user("Carol Oliveira", "carol@example.com")
    
    print(f"✅ Created users: {user1.name}, {user2.name}, {user3.name}")
    
    # Create a test group
    group = DatabaseService.create_group("Casa Compartilhada", [user1.id, user2.id, user3.id])
    print(f"✅ Created group: {group.name}")
    
    # Create an expense with installments that has overdue payments
    today = date.today()
    overdue_date = today - timedelta(days=5)  # 5 days ago
    upcoming_date = today + timedelta(days=2)  # 2 days from now
    
    # Expense 1: Overdue installments
    expense1 = Expense(
        id="test-expense-1",
        amount=600.0,
        description="Conta de Internet",
        paid_by=user1.id,
        split_among=[user1.id, user2.id, user3.id],
        split_type='EQUAL',
        created_at=datetime.combine(overdue_date, datetime.min.time()),
        installments_count=3,
        first_due_date=datetime.combine(overdue_date, datetime.min.time())
    )
    
    ExpenseService.generate_installments(expense1)
    DatabaseService.add_expense_to_group(group.id, expense1)
    print(f"✅ Created expense with overdue installments: {expense1.description}")
    
    # Expense 2: Upcoming installments
    expense2 = Expense(
        id="test-expense-2", 
        amount=450.0,
        description="Conta de Energia",
        paid_by=user2.id,
        split_among=[user1.id, user2.id, user3.id],
        split_type='EQUAL',
        created_at=datetime.combine(upcoming_date, datetime.min.time()),
        installments_count=2,
        first_due_date=datetime.combine(upcoming_date, datetime.min.time())
    )
    
    ExpenseService.generate_installments(expense2)
    DatabaseService.add_expense_to_group(group.id, expense2)
    print(f"✅ Created expense with upcoming installments: {expense2.description}")
    
    # Refresh group and compute balances
    group = DatabaseService.get_group(group.id)
    ExpenseService.recompute_group_balances(group)
    DatabaseService.update_user_balances(group.members)
    
    print("✅ Test data created successfully!")
    print("\nℹ️ Test data includes:")
    print("- 3 users with notification preferences enabled")
    print("- 1 group with shared expenses")
    print("- Expense 1: 3 installments, first due 5 days ago (overdue)")
    print("- Expense 2: 2 installments, first due in 2 days (upcoming)")
    print("\nYou can now test:")
    print("  python notifications.py overdue --report-only")
    print("  python notifications.py upcoming --report-only")

if __name__ == '__main__':
    create_test_data()