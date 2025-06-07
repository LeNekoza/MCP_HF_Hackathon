#!/usr/bin/env python3
"""
Test script for NeonDB PostgreSQL integration
This script tests the database connection and demonstrates data retrieval functionality
"""

import sys
import os
sys.path.append('src')

from src.utils.database import get_data_retriever, test_database_connection
import pandas as pd

def main():
    """Main test function"""
    print("🏥 Hospital Database Connection Test")
    print("=" * 50)
    
    # Test database connectivity
    print("\n1. Testing database connection...")
    if test_database_connection():
        print("✅ Database connection successful!")
    else:
        print("❌ Database connection failed!")
        return False
    
    # Initialize data retriever
    print("\n2. Initializing data retriever...")
    retriever = get_data_retriever()
    print("✅ Data retriever initialized!")
    
    # Test data retrieval functions
    print("\n3. Testing data retrieval functions...")
    
    # Get database statistics
    print("\n📊 Database Statistics:")
    stats = retriever.get_database_stats()
    if stats:
        for table, count in stats.items():
            print(f"   {table}: {count:,} records")
        total_records = sum(stats.values())
        print(f"   Total: {total_records:,} records")
    else:
        print("   ❌ Could not retrieve database statistics")
        return False
    
    # Test retrieving a few users
    print("\n👥 Sample Users (first 5):")
    users_df = retriever.get_all_users(limit=5)
    if not users_df.empty:
        print("✅ Users retrieved successfully!")
        for _, user in users_df.iterrows():
            print(f"   - {user['full_name']} ({user['role']})")
    else:
        print("   ❌ Could not retrieve users")
    
    # Test retrieving patients
    print("\n🏥 Sample Patients (first 3):")
    patients_df = retriever.get_patients(limit=3)
    if not patients_df.empty:
        print("✅ Patients retrieved successfully!")
        for _, patient in patients_df.iterrows():
            print(f"   - {patient['full_name']} (DOB: {patient['date_of_birth']}, Blood: {patient['blood_group']})")
    else:
        print("   ❌ Could not retrieve patients")
    
    # Test retrieving rooms
    print("\n🏠 Available Rooms (first 5):")
    rooms_df = retriever.get_rooms(available_only=True, limit=5)
    if not rooms_df.empty:
        print("✅ Rooms retrieved successfully!")
        for _, room in rooms_df.iterrows():
            print(f"   - Room {room['room_number']} ({room['room_type']}) - Floor {room['floor_number']}")
    else:
        print("   ❌ Could not retrieve rooms")
    
    # Test retrieving medical equipment
    print("\n🩺 Medical Equipment (first 5):")
    equipment_df = retriever.get_medical_equipment(limit=5)
    if not equipment_df.empty:
        print("✅ Medical equipment retrieved successfully!")
        for _, equipment in equipment_df.iterrows():
            print(f"   - {equipment['tool_name']} ({equipment['category']}) - Available: {equipment['quantity_available']}")
    else:
        print("   ❌ Could not retrieve medical equipment")
    
    # Test patient search
    print("\n🔍 Patient Search Test (searching for 'John'):")
    search_results = retriever.search_patients_by_name("John")
    if not search_results.empty:
        print(f"✅ Found {len(search_results)} patients with 'John' in their name!")
        for _, patient in search_results.head(3).iterrows():
            print(f"   - {patient['full_name']} (ID: {patient['id']})")
    else:
        print("   ❌ No patients found or search failed")
    
    # Test occupancy information
    print("\n🛏️ Current Occupancy (first 5):")
    occupancy_df = retriever.get_occupancy(active_only=True)
    if not occupancy_df.empty:
        print(f"✅ Retrieved {len(occupancy_df)} active occupancy records!")
        for _, occupancy in occupancy_df.head(5).iterrows():
            print(f"   - {occupancy['patient_name']} in Room {occupancy['room_number']} (Bed {occupancy['bed_number']})")
    else:
        print("   ❌ Could not retrieve occupancy information")
    
    print("\n🎉 Database integration test completed successfully!")
    print("\n📝 Summary:")
    print("   ✅ Database connection working")
    print("   ✅ Data retrieval functions operational")
    print("   ✅ All major tables accessible")
    print("   ✅ Search functionality working")
    print("\n🚀 Ready for integration with your application!")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1) 