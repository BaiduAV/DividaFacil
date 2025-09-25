#!/usr/bin/env python3
"""Test script to verify group creation with email functionality."""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from src.services.database_service import DatabaseService


def test_group_creation_with_emails():
    """Test creating groups with email addresses."""
    
    # Create some test users first
    print("Creating test users...")
    user1 = DatabaseService.create_user("Alice Smith", "alice@test.com")
    user2 = DatabaseService.create_user("Bob Johnson", "bob@test.com")
    user3 = DatabaseService.create_user("Charlie Brown", "charlie@test.com")
    
    print(f"Created users:")
    print(f"- {user1.name} ({user1.email}) - ID: {user1.id}")
    print(f"- {user2.name} ({user2.email}) - ID: {user2.id}")
    print(f"- {user3.name} ({user3.email}) - ID: {user3.id}")
    
    # Test group creation with member IDs
    print(f"\nCreating group with member IDs...")
    group1 = DatabaseService.create_group("Test Group 1", [user1.id, user2.id])
    print(f"Group '{group1.name}' created with {len(group1.members)} members:")
    for member_id, member in group1.members.items():
        print(f"- {member.name} ({member.email})")
    
    # Test user lookup by email
    print(f"\nTesting email lookup...")
    alice_found = DatabaseService.get_user_by_email("alice@test.com")
    bob_found = DatabaseService.get_user_by_email("bob@test.com")
    nonexistent = DatabaseService.get_user_by_email("nonexistent@test.com")
    
    print(f"Alice lookup: {'Found' if alice_found else 'Not found'}")
    print(f"Bob lookup: {'Found' if bob_found else 'Not found'}")
    print(f"Nonexistent lookup: {'Found' if nonexistent else 'Not found'}")
    
    print(f"\nTest completed successfully!")


if __name__ == "__main__":
    test_group_creation_with_emails()