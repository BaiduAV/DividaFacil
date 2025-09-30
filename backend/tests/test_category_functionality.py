#!/usr/bin/env python3
"""Test script to verify category functionality by creating test expenses."""

import uuid
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import SessionLocal
from src.repositories.user_repository import UserRepository
from src.repositories.group_repository import GroupRepository
from src.repositories.expense_repository import ExpenseRepository


def create_test_expenses_with_categories():
    """Create test expenses with different categories to verify functionality."""
    db = SessionLocal()
    user_repo = UserRepository(db)
    group_repo = GroupRepository(db)
    expense_repo = ExpenseRepository(db)
    
    try:
        # Create test users
        user1 = user_repo.create_with_password("Alice Johnson", "alice@test.com", "dummy_hash")
        user2 = user_repo.create_with_password("Bob Smith", "bob@test.com", "dummy_hash")
        
        # Create test group
        group = group_repo.create("Category Test Group", [user1.id, user2.id])
        
        # Create test expenses with different categories
        test_expenses = [
            {
                "description": "Dinner at Italian Restaurant",
                "amount": 45.50,
                "category": "Food & Drink"
            },
            {
                "description": "Uber to airport",
                "amount": 23.75,
                "category": "Transportation"
            },
            {
                "description": "Movie tickets",
                "amount": 18.00,
                "category": "Entertainment"
            },
            {
                "description": "Hotel booking",
                "amount": 120.00,
                "category": "Accommodation"
            },
            {
                "description": "Office supplies",
                "amount": 15.30,
                "category": "General"
            },
            {
                "description": "Lunch meeting",
                "amount": 32.00,
                "category": None  # Test null category (should default to General)
            }
        ]
        
        from src.models.expense import Expense
        
        for expense_data in test_expenses:
            expense = Expense(
                id=str(uuid.uuid4()),
                description=expense_data["description"],
                amount=expense_data["amount"],
                paid_by=user1.id,
                created_by=user1.id,
                split_among=[user1.id, user2.id],
                category=expense_data["category"],
                split_type="EQUAL",
                created_at=datetime.now()
            )
            
            expense_repo.create(expense, group.id)
            print(f"✓ Created expense: {expense.description} (Category: {expense.category or 'None -> General'})")
            
        db.commit()
        print(f"\n🎉 Test data created successfully!")
        print(f"📊 Group ID: {group.id}")
        print(f"👤 User 1 (Alice): {user1.id}")
        print(f"👤 User 2 (Bob): {user2.id}")
        print(f"\nNow you can test the category functionality in the frontend!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating test data: {e}")
        raise
    finally:
        db.close()


def verify_categories_in_db():
    """Verify that categories are properly stored in the database."""
    db = SessionLocal()
    expense_repo = ExpenseRepository(db)
    
    try:
        # Get expenses from any group to check categories
        from src.repositories.group_repository import GroupRepository
        group_repo = GroupRepository(db)
        groups = group_repo.get_all()
        
        if not groups:
            print("No groups found. Create test data first.")
            return
            
        for group in groups:
            expenses = expense_repo.get_by_group_id(group.id)
            print(f"\n📁 Group: {group.name}")
            print(f"💰 Found {len(expenses)} expenses:")
            
            for expense in expenses:
                category_display = expense.category if expense.category else "None (defaults to General)"
                print(f"  - {expense.description}: {category_display}")
                
    except Exception as e:
        print(f"❌ Error verifying categories: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Test category functionality")
    parser.add_argument("--create", action="store_true", help="Create test expenses with categories")
    parser.add_argument("--verify", action="store_true", help="Verify categories in database")
    
    args = parser.parse_args()
    
    if args.create:
        create_test_expenses_with_categories()
    elif args.verify:
        verify_categories_in_db()
    else:
        print("Usage: python test_category_functionality.py --create | --verify")
        print("  --create: Create test expenses with different categories")
        print("  --verify: Check existing expenses and their categories")