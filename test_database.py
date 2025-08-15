#!/usr/bin/env python3
"""
Test script to verify the database integration works correctly.
This script tests all the database functions without needing the FastAPI server.
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "fastapi-service", "app"))

from database import (
    init_database,
    get_all_chores,
    get_chore_by_id,
    search_chores,
    add_chore,
    delete_chore,
)


def test_database_functions():
    """Test all database functions to ensure they work correctly."""
    print("🧪 Testing Chore Database Functions\n")

    # Test 1: Get all chores
    print("1. Testing get_all_chores()...")
    chores = get_all_chores()
    print(f"   ✅ Found {len(chores)} chores")

    # Test 2: Get specific chore
    print("\n2. Testing get_chore_by_id()...")
    microwave_chore = get_chore_by_id("microwave")
    if microwave_chore:
        print(f"   ✅ Found chore: {microwave_chore['title']}")
        print(f"   📝 Steps: {len(microwave_chore['steps'])}")
        print(f"   🕐 Time: {microwave_chore['time_min']} minutes")
    else:
        print("   ❌ Microwave chore not found")

    # Test 3: Search chores
    print("\n3. Testing search_chores()...")
    clean_chores = search_chores("clean")
    print(f"   ✅ Found {len(clean_chores)} chores with 'clean' in title")
    for chore in clean_chores:
        print(f"      - {chore['title']}")

    # Test 4: Test non-existent chore
    print("\n4. Testing get_chore_by_id() with non-existent ID...")
    non_existent = get_chore_by_id("non-existent")
    if non_existent is None:
        print("   ✅ Correctly returned None for non-existent chore")
    else:
        print("   ❌ Should have returned None")

    # Test 5: Add a temporary chore and then delete it
    print("\n5. Testing add_chore() and delete_chore()...")
    test_chore = {
        "id": "test-chore",
        "title": "Test Chore",
        "items": ["Test item"],
        "steps": ["Test step"],
        "time_min": 5,
    }

    if add_chore(test_chore):
        print("   ✅ Successfully added test chore")

        # Verify it was added
        added_chore = get_chore_by_id("test-chore")
        if added_chore:
            print("   ✅ Test chore retrieved successfully")

            # Delete the test chore
            if delete_chore("test-chore"):
                print("   ✅ Successfully deleted test chore")

                # Verify it was deleted
                deleted_chore = get_chore_by_id("test-chore")
                if deleted_chore is None:
                    print("   ✅ Test chore properly removed")
                else:
                    print("   ❌ Test chore still exists after deletion")
            else:
                print("   ❌ Failed to delete test chore")
        else:
            print("   ❌ Test chore not found after adding")
    else:
        print("   ❌ Failed to add test chore")

    print("\n🎉 Database testing complete!")


def simulate_api_responses():
    """Simulate what the API endpoints would return."""
    print("\n🌐 Simulating API Endpoint Responses\n")

    # Simulate GET /chores
    print("GET /chores")
    chores = get_all_chores()
    api_response = {"chores": chores}
    print(f"   Response: {len(api_response['chores'])} chores returned")

    # Simulate GET /chores?q=clean
    print("\nGET /chores?q=clean")
    search_results = search_chores("clean")
    api_response = {"chores": search_results}
    print(f"   Response: {len(api_response['chores'])} chores matching 'clean'")

    # Simulate GET /chores/microwave
    print("\nGET /chores/microwave")
    chore = get_chore_by_id("microwave")
    if chore:
        print(f"   Response: {chore['title']} - {chore['time_min']} minutes")
    else:
        print("   Response: 404 Not Found")

    # Simulate GET /chores/non-existent
    print("\nGET /chores/non-existent")
    chore = get_chore_by_id("non-existent")
    if chore:
        print(f"   Response: {chore}")
    else:
        print("   Response: 404 Not Found")


if __name__ == "__main__":
    test_database_functions()
    simulate_api_responses()
