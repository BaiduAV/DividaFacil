#!/usr/bin/env python3
"""Create complete test setup for category functionality testing."""

import requests
import json


def create_complete_test_setup():
    """Create a full test setup with user, group, and categorized expenses."""
    
    base_url = "http://localhost:8000"
    
    # Login
    login_data = {
        "email": "tester@example.com",
        "password": "test123"
    }
    
    session = requests.Session()
    
    print("🔐 Logging in...")
    response = session.post(f"{base_url}/api/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return None
    
    print("✅ Login successful!")
    
    # Create a new group
    print("\n📁 Creating test group...")
    group_data = {
        "name": "Frontend Category Test",
        "description": "Testing category functionality in frontend"
    }
    
    response = session.post(f"{base_url}/api/groups", json=group_data)
    if response.status_code in [200, 201]:
        group = response.json()
        group_id = group.get('id')
        print(f"✅ Group created: {group.get('name')} (ID: {group_id})")
    else:
        print(f"❌ Group creation failed: {response.status_code} - {response.text}")
        return None
    
    # Create expenses with different categories
    test_expenses = [
        {
            "description": "Pizza delivery",
            "amount": 28.50,
            "category": "Food & Drink",
            "paid_by": "6999e981-0ef0-464d-b831-c59699ea0239",  # Test user ID
            "split_among": ["6999e981-0ef0-464d-b831-c59699ea0239"],
            "split_type": "EQUAL",
            "installments_count": 1
        },
        {
            "description": "Bus tickets",
            "amount": 12.75,
            "category": "Transportation", 
            "paid_by": "6999e981-0ef0-464d-b831-c59699ea0239",
            "split_among": ["6999e981-0ef0-464d-b831-c59699ea0239"],
            "split_type": "EQUAL",
            "installments_count": 1
        },
        {
            "description": "Concert tickets",
            "amount": 85.00,
            "category": "Entertainment",
            "paid_by": "6999e981-0ef0-464d-b831-c59699ea0239",
            "split_among": ["6999e981-0ef0-464d-b831-c59699ea0239"],
            "split_type": "EQUAL", 
            "installments_count": 1
        },
        {
            "description": "Hotel stay",
            "amount": 150.00,
            "category": "Accommodation",
            "paid_by": "6999e981-0ef0-464d-b831-c59699ea0239",
            "split_among": ["6999e981-0ef0-464d-b831-c59699ea0239"],
            "split_type": "EQUAL",
            "installments_count": 1
        },
        {
            "description": "Miscellaneous items",
            "amount": 23.45,
            "category": "General",
            "paid_by": "6999e981-0ef0-464d-b831-c59699ea0239",
            "split_among": ["6999e981-0ef0-464d-b831-c59699ea0239"],
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
    print(f"   📁 Group: Frontend Category Test (ID: {group_id})")
    print(f"   💰 Created {len(created_expenses)} expenses with categories")
    print(f"\n🌐 Now you can test the frontend at: http://localhost:3001/app/")
    print(f"   📧 Login with: tester@example.com")
    print(f"   🔑 Password: test123")
    
    return group_id, created_expenses


if __name__ == "__main__":
    create_complete_test_setup()