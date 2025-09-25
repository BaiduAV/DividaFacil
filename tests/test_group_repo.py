#!/usr/bin/env python3
"""Test the group repository directly to see if expenses are loaded correctly."""

import sys
sys.path.append('.')

from src.database import SessionLocal, GroupDB, ExpenseDB, UserDB
from src.repositories.group_repository import GroupRepository
from sqlalchemy.orm import selectinload

def test_group_repository():
    """Test if GroupRepository loads expenses correctly."""
    
    print("=== Testing Group Repository ===\n")
    
    db = SessionLocal()
    
    try:
        # Test direct database query first
        print("1. Direct database query:")
        casa_group = db.query(GroupDB).filter(GroupDB.name == "Casa").first()
        if casa_group:
            print(f"   Group: {casa_group.name}")
            print(f"   ID: {casa_group.id}")
            print(f"   Direct expenses count: {len(casa_group.expenses)}")
            
            # Load with selectinload
            casa_group_loaded = (
                db.query(GroupDB)
                .options(selectinload(GroupDB.expenses))
                .filter(GroupDB.name == "Casa")
                .first()
            )
            if casa_group_loaded:
                print(f"   With selectinload expenses count: {len(casa_group_loaded.expenses)}")
                
                # Show some expense details
                for i, exp in enumerate(casa_group_loaded.expenses):
                    if i < 3:  # Show first 3
                        print(f"     Expense {i+1}: {exp.description} - ${exp.amount}")
        else:
            print("   Casa group not found!")
        
        print("\n2. Using GroupRepository:")
        group_repo = GroupRepository(db)
        
        # Get all groups
        all_groups = group_repo.get_all()
        print(f"   Total groups: {len(all_groups)}")
        
        for group in all_groups:
            if group.name == "Casa":
                print(f"   Casa group via repository:")
                print(f"     Name: {group.name}")
                print(f"     ID: {group.id}")
                print(f"     Expenses count: {len(group.expenses)}")
                print(f"     Members count: {len(group.members)}")
                
                # Show expense details
                for i, expense in enumerate(group.expenses):
                    if i < 3:  # Show first 3
                        print(f"       Expense {i+1}: {expense.description} - ${expense.amount}")
                break
        
        print("\n3. Testing individual group fetch:")
        if casa_group:
            group_id = str(casa_group.id)
            fetched_group = group_repo.get_by_id(group_id)
            if fetched_group:
                print(f"   Fetched group: {fetched_group.name}")
                print(f"   Expenses: {len(fetched_group.expenses)}")
                for i, expense in enumerate(fetched_group.expenses):
                    if i < 3:  # Show first 3
                        print(f"     Expense {i+1}: {expense.description} - ${expense.amount}")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_group_repository()