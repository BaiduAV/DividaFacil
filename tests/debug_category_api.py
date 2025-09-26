#!/usr/bin/env python3
"""Debug script to check API responses for category data."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import SessionLocal
from src.repositories.group_repository import GroupRepository
from src.repositories.expense_repository import ExpenseRepository
from src.schemas.expense import ExpenseResponse


def debug_api_responses():
    """Debug the API responses to ensure categories are included."""
    db = SessionLocal()
    group_repo = GroupRepository(db)
    expense_repo = ExpenseRepository(db)
    
    try:
        groups = group_repo.get_all()
        print(f"🔍 Found {len(groups)} groups")
        
        for group in groups:
            print(f"\n📁 Group: {group.name} (ID: {group.id})")
            expenses = expense_repo.get_by_group_id(group.id)
            
            print(f"💰 Found {len(expenses)} expenses:")
            for expense in expenses:
                print(f"  📝 Raw expense model:")
                print(f"    - ID: {expense.id}")
                print(f"    - Description: {expense.description}")
                print(f"    - Amount: {expense.amount}")
                print(f"    - Category: {repr(expense.category)}")
                print(f"    - Split type: {expense.split_type}")
                print(f"    - Created at: {expense.created_at}")
                
                # Test the API response schema
                response_obj = ExpenseResponse.from_expense(expense)
                print(f"  🌐 API Response object:")
                print(f"    - ID: {response_obj.id}")
                print(f"    - Description: {response_obj.description}")
                print(f"    - Amount: {response_obj.amount}")
                print(f"    - Category: {repr(response_obj.category)}")
                print(f"    - Split type: {response_obj.split_type}")
                print()
                
    except Exception as e:
        print(f"❌ Error debugging API responses: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    debug_api_responses()