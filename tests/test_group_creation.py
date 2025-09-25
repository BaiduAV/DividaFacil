#!/usr/bin/env python3
"""Test script to verify group creation with email functionality."""

import pytest
from src.services.database_service import DatabaseService


def test_group_creation_with_emails(test_users):
    """Test creating groups with email addresses."""

    user1, user2, user3 = test_users

    print(f"Using test users:")
    print(f"- {user1.name} ({user1.email}) - ID: {user1.id}")
    print(f"- {user2.name} ({user2.email}) - ID: {user2.id}")
    print(f"- {user3.name} ({user3.email}) - ID: {user3.id}")

    # Test group creation with member IDs
    print(f"\nCreating group with member IDs...")
    group1 = DatabaseService.create_group("Test Group 1", [user1.id, user2.id])
    print(f"Group '{group1.name}' created with {len(group1.members)} members:")
    for member_id, member in group1.members.items():
        print(f"- {member.name} ({member.email})")

    # Verify group was created correctly
    assert group1.name == "Test Group 1"
    assert len(group1.members) == 2
    assert user1.id in group1.members
    assert user2.id in group1.members
    assert user3.id not in group1.members

    # Test group creation with emails (simulate API behavior)
    print(f"\nCreating group with member emails...")
    # Convert emails to user IDs (like the API does)
    member_ids_from_emails = []
    for email in [user2.email, user3.email]:
        user = DatabaseService.get_user_by_email(email)
        if user:
            member_ids_from_emails.append(user.id)
    
    group2 = DatabaseService.create_group("Test Group 2", member_ids_from_emails)
    print(f"Group '{group2.name}' created with {len(group2.members)} members:")
    for member_id, member in group2.members.items():
        print(f"- {member.name} ({member.email})")

    # Verify group was created correctly
    assert group2.name == "Test Group 2"
    assert len(group2.members) == 2
    assert user2.id in group2.members
    assert user3.id in group2.members
    assert user1.id not in group2.members

    print("\n✅ All group creation tests passed!")