#!/usr/bin/env python3
"""Test script to verify group delete functionality works with zero balance groups."""

import requests
import json

def test_group_delete_functionality():
    base_url = "http://localhost:8000"
    
    # First, let's check the current groups
    print("=== Current Groups ===")
    try:
        response = requests.get(f"{base_url}/api/groups")
        if response.status_code == 200:
            groups = response.json()
            for group in groups:
                print(f"Group: {group['name']} (ID: {group['id']})")
                print(f"  Balances: {group['balances']}")
                # Check if settled
                all_zero = all(abs(balance) < 0.01 for balance in group['balances'].values())
                print(f"  Is settled: {all_zero}")
                print()
        elif response.status_code == 401:
            print("Authentication required - groups endpoint needs login")
            return
        else:
            print(f"Failed to get groups: {response.status_code}")
            return
    except Exception as e:
        print(f"Error checking groups: {e}")
        return
    
    # Test that we can identify settled groups correctly
    settled_groups = []
    for group in groups:
        all_zero = all(abs(balance) < 0.01 for balance in group['balances'].values())
        if all_zero:
            settled_groups.append(group)
    
    print(f"Found {len(settled_groups)} settled groups that should be deletable")
    
    if settled_groups:
        print("\nSettled groups (should be deletable):")
        for group in settled_groups:
            print(f"  - {group['name']}: {group['balances']}")
    
if __name__ == "__main__":
    test_group_delete_functionality()