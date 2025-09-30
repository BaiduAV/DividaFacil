#!/usr/bin/env python3
"""Test script to verify backend group deletion logic works correctly."""

from src.services.database_service import DatabaseService
from src.schemas.group import GroupResponse

def test_backend_delete_logic():
    print("=== Testing Backend Delete Logic ===")
    db_service = DatabaseService()
    
    # Get all groups
    groups = db_service.get_all_groups()
    
    if not groups:
        print("No groups found")
        return
        
    for group_id, group in groups.items():
        print(f"\nGroup: {group.name} (ID: {group_id})")
        
        # Create group response to get the calculated balances
        group_response = GroupResponse.from_group(group)
        print(f"Balances: {group_response.balances}")
        
        # Test if it's settled using our new logic
        is_settled_new = all(abs(balance) < 0.01 for balance in group_response.balances.values())
        print(f"Is settled (new logic): {is_settled_new}")
        
        # Test backend is_group_settled function
        is_settled_backend = db_service.is_group_settled(group_id)
        print(f"Is settled (backend): {is_settled_backend}")
        
        if is_settled_new != is_settled_backend:
            print("❌ MISMATCH! Frontend and backend settlement detection differ!")
        else:
            print("✅ Frontend and backend settlement detection match")
            
        if is_settled_new:
            print("🔥 This group SHOULD be deletable")

if __name__ == "__main__":
    test_backend_delete_logic()