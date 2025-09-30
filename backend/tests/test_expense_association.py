#!/usr/bin/env python3
"""Test script to verify expense-group association."""

import pytest
from src.services.database_service import DatabaseService
from src.models.expense import Expense
from datetime import datetime
import uuid


def test_expense_group_association(test_users):
    """Test if expenses are properly associated with specific groups."""

    print("=== Expense-Group Association Test ===\n")

    user1, user2, user3 = test_users[:3]

    print(f"Using test users: {user1.name} ({user1.id}) and {user2.name} ({user2.id})")
    
    # Create two groups
    print("\n2. Creating test groups...")
    group1 = DatabaseService.create_group("Group 1", [user1.id, user2.id])
    group2 = DatabaseService.create_group("Group 2", [user1.id, user2.id])
    print(f"   Group 1: {group1.name} ({group1.id})")
    print(f"   Group 2: {group2.name} ({group2.id})")
    
    # Add expense to Group 1 only
    print("\n3. Adding expense to Group 1 only...")
    expense1 = Expense(
        id=str(uuid.uuid4()),
        description="Group 1 Expense",
        amount=50.0,
        paid_by=user1.id,
        created_by=user1.id,
        split_among=[user1.id, user2.id],
        split_type="EQUAL",
        split_values={},
        created_at=datetime.now(),
        installments_count=1,
        first_due_date=datetime.now()
    )
    
    DatabaseService.add_expense_to_group(group1.id, expense1)
    print(f"   Added expense '{expense1.description}' to Group 1")
    
    # Check groups after adding expense
    print("\n4. Checking group contents after adding expense...")
    
    # Get fresh data from database
    all_groups = DatabaseService.get_all_groups()
    
    print(f"   Total groups in database: {len(all_groups)}")
    
    for group_id, group in all_groups.items():
        print(f"   Group: {group.name} ({group.id})")
        print(f"     Members: {len(group.members)}")
        print(f"     Expenses: {len(group.expenses)}")
        if group.expenses:
            for exp in group.expenses:
                print(f"       - {exp.description} (${exp.amount})")
        print()
    
    # Check specific groups
    updated_group1 = DatabaseService.get_group(group1.id)
    updated_group2 = DatabaseService.get_group(group2.id)
    
    print("5. Individual group check:")
    print(f"   Group 1 expenses: {len(updated_group1.expenses) if updated_group1 else 0}")
    print(f"   Group 2 expenses: {len(updated_group2.expenses) if updated_group2 else 0}")
    
    if updated_group1 and len(updated_group1.expenses) == 1 and updated_group2 and len(updated_group2.expenses) == 0:
        print("   ✅ SUCCESS: Expense correctly added to Group 1 only!")
    else:
        print("   ❌ ISSUE: Expense not properly isolated to Group 1!")
    
    print("\n=== Test completed ===")