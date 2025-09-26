#!/usr/bin/env python3
"""Complete test setup for category functionality testing."""

import requests
import json
import sys


def create_test_user():
    """Create the test user first."""
    base_url = "http://localhost:8000"
    
    # Create test user
    user_data = {
        "email": "tester@example.com",
        "password": "test123",
        "name": "Test User"
    }
    
    print("👤 Creating test user...")
    response = requests.post(f"{base_url}/api/signup", json=user_data)
    if response.status_code in [200, 201]:
        user = response.json()
        print(f"✅ Test user created: {user.get('email')}")
        return user
    elif response.status_code == 400 and "already exists" in response.text:
        print("ℹ️  Test user already exists")
        return {"email": "tester@example.com"}
    else:
        print(f"❌ User creation failed: {response.status_code} - {response.text}")
        return None


def create_complete_test_setup():
    """Create a full test setup with user, group, and categorized expenses."""
    
    base_url = "http://localhost:8000"
    
    # First, ensure test user exists
    user = create_test_user()
    if not user:
        print("❌ Cannot proceed without test user")
        return None
    
    # Login
    login_data = {
        "email": "tester@example.com",
        "password": "test123"
    }
    
    session = requests.Session()
    
    print("\n🔐 Logging in...")
    response = session.post(f"{base_url}/api/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return None

    login_response = response.json()
    user_id = login_response.get('user_id')
    print(f"✅ Login successful! User ID: {user_id}")
    
    # Create a new group
    print("\n📁 Creating test group...")
    group_data = {
        "name": "Category Test Group",
        "description": "Testing category functionality"
    }
    
    response = session.post(f"{base_url}/api/groups", json=group_data)
    if response.status_code in [200, 201]:
        group = response.json()
        group_id = group.get('id')
        print(f"✅ Group created: {group.get('name')} (ID: {group_id})")
    else:
        print(f"❌ Group creation failed: {response.status_code} - {response.text}")
        return None
    
    # Create expenses with different categories using frontend category names
    test_expenses = [
        {
            "description": "Pizza party dinner",
            "amount": 35.50,
            "category": "Food & Drink",
            "paid_by": user_id,
            "split_among": [user_id],
            "split_type": "EQUAL",
            "installments_count": 1
        },
        {
            "description": "Uber rides",
            "amount": 18.75,
            "category": "Transportation", 
            "paid_by": user_id,
            "split_among": [user_id],
            "split_type": "EQUAL",
            "installments_count": 1
        },
        {
            "description": "Movie tickets",
            "amount": 24.00,
            "category": "Entertainment",
            "paid_by": user_id,
            "split_among": [user_id],
            "split_type": "EQUAL", 
            "installments_count": 1
        },
        {
            "description": "Hotel booking",
            "amount": 120.00,
            "category": "Accommodation",
            "paid_by": user_id,
            "split_among": [user_id],
            "split_type": "EQUAL",
            "installments_count": 1
        },
        {
            "description": "Clothes shopping",
            "amount": 67.90,
            "category": "Shopping",
            "paid_by": user_id,
            "split_among": [user_id],
            "split_type": "EQUAL",
            "installments_count": 1
        },
        {
            "description": "Office supplies",
            "amount": 15.30,
            "category": "Other",
            "paid_by": user_id,
            "split_among": [user_id],
            "split_type": "EQUAL",
            "installments_count": 1
        }
    ]
    
    print(f"\n💰 Creating {len(test_expenses)} test expenses...")
    created_expenses = []
    
    for expense_data in test_expenses:
        response = session.post(f"{base_url}/api/groups/{group_id}/expenses", json=expense_data)
        if response.status_code in [200, 201]:
            expense = response.json()
            created_expenses.append(expense)
            print(f"✅ Created: {expense.get('description')} (Category: {expense.get('category')})")
        else:
            print(f"❌ Failed to create expense '{expense_data['description']}': {response.status_code} - {response.text}")
    
    print(f"\n🎉 Test setup complete!")
    print(f"   📁 Group: Category Test Group (ID: {group_id})")
    print(f"   💰 Created {len(created_expenses)} expenses with categories:")
    
    # Show summary by category
    categories = {}
    for expense in created_expenses:
        cat = expense.get('category', 'Unknown')
        categories[cat] = categories.get(cat, 0) + 1
    
    for category, count in categories.items():
        print(f"      • {category}: {count} expense(s)")
    
    print(f"\n🌐 Now you can test the frontend at: http://localhost:3001/app/")
    print(f"   📧 Login with: tester@example.com")
    print(f"   🔑 Password: test123")
    print(f"\nNext steps:")
    print(f"   1. Open the frontend URL above")
    print(f"   2. Login with the credentials")
    print(f"   3. Navigate to the 'Category Test Group'")
    print(f"   4. Check the Expenses tab to verify categories and filters work")
    
    return group_id, created_expenses


if __name__ == "__main__":
    try:
        create_complete_test_setup()
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure the backend server is running on http://localhost:8000")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)