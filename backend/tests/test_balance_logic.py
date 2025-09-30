#!/usr/bin/env python3
"""Test balance calculations with specific examples to identify the issue."""

import sys
sys.path.append('.')

from src.database import SessionLocal
from src.services.database_service import DatabaseService
from src.services.expense_service import ExpenseService
from src.repositories.user_repository import UserRepository

def test_balance_logic():
    """Test balance calculations with concrete examples."""
    
    print("=== Testing Balance Logic ===\n")
    
    # Find the test user
    with SessionLocal() as db:
        user_repo = UserRepository(db)
        test_user = user_repo.get_by_email("test@example.com")
        testuser = user_repo.get_by_email("testuser@example.com")
        
        if not test_user or not testuser:
            print("❌ Test users not found!")
            return
        
        print(f"User 1: {test_user.name} (ID: {test_user.id})")
        print(f"User 2: {testuser.name} (ID: {testuser.id})")
    
    # Get the groups
    all_groups = DatabaseService.get_all_groups()
    test_group = None
    
    for group in all_groups.values():
        if "Teste2" in group.name and test_user.id in group.members:
            test_group = group
            break
    
    if not test_group:
        print("❌ Test group not found!")
        return
    
    print(f"\n📊 Analyzing group: {test_group.name}")
    print(f"Members: {len(test_group.members)}")
    print(f"Expenses: {len(test_group.expenses)}")
    
    # Show initial balances (before recompute)
    print("\n💰 Balances BEFORE recompute:")
    for user_id, user in test_group.members.items():
        total_balance = sum(user.balance.values())
        print(f"  {user.name}: ${total_balance:.2f}")
        if user.balance:
            for other_user_id, amount in user.balance.items():
                other_user = test_group.members.get(other_user_id)
                other_name = other_user.name if other_user else other_user_id[:8]
                print(f"    → {other_name}: ${amount:.2f}")
    
    # Analyze expenses in detail
    print(f"\n📝 Expense Analysis:")
    for i, expense in enumerate(test_group.expenses):
        print(f"  Expense {i+1}: {expense.description}")
        print(f"    Amount: ${expense.amount}")
        
        payer = test_group.members.get(expense.paid_by)
        payer_name = payer.name if payer else expense.paid_by[:8]
        print(f"    Paid by: {payer_name}")
        print(f"    Split among: {len(expense.split_among)} people")
        print(f"    Split type: {expense.split_type}")
        print(f"    Split values: {expense.split_values}")
        
        # Show who's in the split
        print("    Split participants:")
        for split_user_id in expense.split_among:
            split_user = test_group.members.get(split_user_id)
            split_name = split_user.name if split_user else "Unknown"
            print(f"      - {split_name} ({split_user_id[:8]}...)")
        
        # Calculate what each person should owe
        if expense.split_type == "EQUAL":
            per_person = expense.amount / len(expense.split_among)
            print(f"    Per person: ${per_person:.2f}")
            
            print("    Expected debts:")
            for split_user_id in expense.split_among:
                split_user = test_group.members.get(split_user_id)
                split_name = split_user.name if split_user else split_user_id[:8]
                if split_user_id != expense.paid_by:
                    print(f"      {split_name} owes payer: ${per_person:.2f}")
                else:
                    print(f"      {split_name} paid, should be owed: ${per_person * (len(expense.split_among) - 1):.2f}")
    
    # Recompute balances
    print(f"\n🔄 Recomputing balances...")
    ExpenseService.recompute_group_balances(test_group)
    
    # Show balances after recompute
    print("\n💰 Balances AFTER recompute:")
    for user_id, user in test_group.members.items():
        total_balance = sum(user.balance.values())
        print(f"  {user.name} ({user_id[:8]}...): ${total_balance:.2f}")
        if user.balance:
            for other_user_id, amount in user.balance.items():
                other_user = test_group.members.get(other_user_id)
                other_name = other_user.name if other_user else "Unknown"
                print(f"    → owes {other_name} ({other_user_id[:8]}...): ${amount:.2f}")
    
    # Verify balance consistency
    print(f"\n✅ Balance Verification:")
    total_balance = 0
    for user_id, user in test_group.members.items():
        user_total = sum(user.balance.values())
        total_balance += user_total
        print(f"  {user.name} net: ${user_total:.2f}")
    
    print(f"  Total system balance: ${total_balance:.2f} (should be $0.00)")
    
    if abs(total_balance) < 0.01:
        print("  ✅ Balances are consistent!")
    else:
        print("  ❌ Balance inconsistency detected!")

if __name__ == "__main__":
    test_balance_logic()