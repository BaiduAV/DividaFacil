#!/usr/bin/env python3
"""Test script to check group API response format."""

from src.services.database_service import DatabaseService
from src.schemas.group import GroupResponse

def main():
    db_service = DatabaseService()
    groups = db_service.get_all_groups()
    
    if groups:
        print("Sample Group API Response Format:")
        sample_group = list(groups.values())[0]
        group_response = GroupResponse.from_group(sample_group)
        
        print(f"Group ID: {group_response.id}")
        print(f"Group Name: {group_response.name}")
        print(f"Members: {list(group_response.members.keys())}")
        print(f"Balances: {group_response.balances}")
        
        # Show the structure of members
        print("\nMembers structure:")
        for user_id, user in group_response.members.items():
            print(f"  {user_id}: name={user.name}, email={user.email}, balance={user.balance}")
        
        # Check if it's settled
        print(f"\nGroup balances: {group_response.balances}")
        all_zero = all(abs(balance) < 0.01 for balance in group_response.balances.values())
        print(f"Is settled (all balances < 0.01): {all_zero}")
    else:
        print("No groups found")

if __name__ == "__main__":
    main()