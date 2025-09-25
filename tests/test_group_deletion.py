#!/usr/bin/env python3
"""Test script to verify group deletion functionality with settled validation."""

import pytest
import uuid
from src.services.database_service import DatabaseService
from src.services.expense_service import ExpenseService
from src.models.expense import Expense


def test_group_deletion(test_users):
    """Test group deletion with settled/unsettled scenarios."""

    print("=== Group Deletion Test ===\n")

    user1, user2, user3 = test_users[:3]

    print(f"Using test users: {user1.name}, {user2.name}, {user3.name}")

    # Create a group
    print("\n2. Creating test group...")
    group = DatabaseService.create_group("Test Delete Group", [user1.id, user2.id])
    print(f"   Group '{group.name}' created with ID: {group.id}")
    print(f"   Members: {len(group.members)}")

    # Test 1: Delete settled group (should work)
    print("\n3. Testing deletion of settled group...")
    is_settled = DatabaseService.is_group_settled(group.id)
    print(f"   Group settled status: {is_settled}")
    
    if is_settled:
        print("   Attempting to delete settled group...")
        success = DatabaseService.delete_group(group.id)
        print(f"   Deletion result: {'SUCCESS' if success else 'FAILED'}")
        
        # Verify deletion
        deleted_group = DatabaseService.get_group(group.id)
        print(f"   Group still exists: {deleted_group is not None}")
    
    # Create another group for unsettled test
    print("\n4. Creating group for unsettled test...")
    group2 = DatabaseService.create_group("Unsettled Test Group", [user1.id, user2.id])
    print(f"   Group '{group2.name}' created with ID: {group2.id}")
    
    # Add an expense to make it unsettled
    print("\n5. Adding expense to create unsettled balances...")
    expense = Expense(
        id=f"test-expense-{uuid.uuid4().hex[:8]}",
        description="Test Dinner",
        amount=100.0,
        paid_by=user1.id,
        split_type="EQUAL",
        split_among=[user1.id, user2.id],
        split_values={}
    )
    group2.add_expense(expense)
    DatabaseService.add_expense_to_group(group2.id, expense)
    
    # Calculate balances
    ExpenseService.calculate_balances(expense, group2.members)
    DatabaseService.update_user_balances(group2.members)
    
    print("   Expense added and balances calculated")
    
    # Check if group is settled now
    print("\n6. Testing deletion of unsettled group...")
    is_settled_2 = DatabaseService.is_group_settled(group2.id)
    print(f"   Group settled status: {is_settled_2}")
    
    if not is_settled_2:
        print("   Group has outstanding balances - deletion should be blocked")
        print("   User balances:")
        updated_group = DatabaseService.get_group(group2.id)
        if updated_group:
            for member_id, member in updated_group.members.items():
                if member.balance:
                    print(f"     {member.name}: {dict(member.balance)}")
    
    # Test settled calculation
    print("\n7. Testing balance calculation details...")
    if updated_group:
        balances = ExpenseService._calculate_net_balances(updated_group.members)
        print(f"   Net balances: {balances}")
        print(f"   Significant balances count: {len(balances)}")
        print(f"   Is settled (should be False): {len(balances) == 0}")
    
    print("\n=== Test completed ===")