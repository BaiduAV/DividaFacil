#!/usr/bin/env python3
"""Test script to debug the groups API response step by step."""

import sys
sys.path.append('.')

from src.database import SessionLocal, UserDB
from src.services.database_service import DatabaseService
from src.services.expense_service import ExpenseService
from src.repositories.user_repository import UserRepository
from src.schemas.group import GroupResponse

def test_groups_api_logic():
    """Test the same logic as the groups API endpoint."""
    
    print("=== Testing Groups API Logic ===\n")
    
    # Find the test user
    with SessionLocal() as db:
        user_repo = UserRepository(db)
        test_user = user_repo.get_by_email("test@example.com")
        if not test_user:
            print("❌ Test user not found!")
            return
        
        print(f"✅ Found test user: {test_user.name} ({test_user.email})")
        print(f"   User ID: {test_user.id}")
    
    # Step 1: Get all groups (same as API)
    print("\n1. Getting all groups from DatabaseService...")
    all_groups = DatabaseService.get_all_groups()
    print(f"   Total groups in database: {len(all_groups)}")
    
    # Step 2: Filter to user groups (same as API)  
    print("\n2. Filtering to user's groups...")
    user_groups = [group for group in all_groups.values() if test_user.id in group.members]
    print(f"   User's groups count: {len(user_groups)}")
    
    for group in user_groups:
        print(f"   - {group.name}: {len(group.expenses)} expenses BEFORE recompute")
    
    # Step 3: Recompute balances (same as API)
    print("\n3. Recomputing balances...")
    for group in user_groups:
        print(f"   Processing group: {group.name}")
        print(f"     Expenses before recompute: {len(group.expenses)}")
        
        # This is what happens in the API
        ExpenseService.recompute_group_balances(group)
        DatabaseService.update_user_balances(group.members)
        
        print(f"     Expenses after recompute: {len(group.expenses)}")
        
        # Show some expense details
        for i, expense in enumerate(group.expenses):
            if i < 3:  # Show first 3
                print(f"       Expense {i+1}: {expense.description} - ${expense.amount}")
    
    # Step 4: Convert to response (same as API)
    print("\n4. Converting to API response...")
    group_responses = [GroupResponse.from_group(group) for group in user_groups]
    
    for response in group_responses:
        print(f"   Response for {response.name}:")
        print(f"     Expenses in response: {len(response.expenses)}")
        if hasattr(response, 'expenses'):
            for i, exp in enumerate(response.expenses):
                if i < 3:  # Show first 3
                    print(f"       {i+1}. {exp.description} - ${exp.amount}")

if __name__ == "__main__":
    test_groups_api_logic()