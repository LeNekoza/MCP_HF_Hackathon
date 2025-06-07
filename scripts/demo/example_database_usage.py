#!/usr/bin/env python3
"""
Example script demonstrating how to use NeonDB PostgreSQL data retrieval
in your MCP HF Hackathon application
"""

import sys
import os
sys.path.append('src')

from src.utils.database import get_data_retriever
import pandas as pd

def main():
    """Example usage of database functionality"""
    print("🏥 NeonDB PostgreSQL Data Retrieval Examples")
    print("=" * 60)
    
    # Initialize the data retriever
    retriever = get_data_retriever()
    
    # Example 1: Get database statistics
    print("\n📊 1. Database Overview:")
    stats = retriever.get_database_stats()
    for table, count in stats.items():
        print(f"   {table}: {count:,} records")
    
    # Example 2: Find patients by name
    print("\n🔍 2. Search Patients (example: 'Sarah'):")
    patients = retriever.search_patients_by_name("Sarah")
    print(f"   Found {len(patients)} patients with 'Sarah' in their name")
    if not patients.empty:
        for _, patient in patients.head(3).iterrows():
            print(f"   - {patient['full_name']} (DOB: {patient['date_of_birth']}, Blood: {patient['blood_group']})")
    
    # Example 3: Get all staff members
    print("\n👨‍⚕️ 3. Medical Staff:")
    staff = retriever.get_staff(limit=5)
    if not staff.empty:
        for _, member in staff.iterrows():
            print(f"   - {member['full_name']} ({member['role']}) - {member['staff_type']}")
    
    # Example 4: Check available rooms
    print("\n🏠 4. Available Rooms:")
    available_rooms = retriever.get_rooms(available_only=True, limit=5)
    if not available_rooms.empty:
        for _, room in available_rooms.iterrows():
            print(f"   - Room {room['room_number']} ({room['room_type']}) - Floor {room['floor_number']}")
    else:
        print("   No available rooms found")
    
    # Example 5: Get medical equipment
    print("\n🩺 5. Medical Equipment (available only):")
    equipment = retriever.get_medical_equipment(available_only=True, limit=5)
    if not equipment.empty:
        for _, item in equipment.iterrows():
            print(f"   - {item['tool_name']} ({item['category']}) - Qty: {item['quantity_available']}")
    
    # Example 6: Get all patients from a specific blood group
    print("\n🩸 6. Patients with Blood Type O+:")
    all_patients = retriever.get_patients()
    if not all_patients.empty:
        o_positive_patients = all_patients[all_patients['blood_group'] == 'O+']
        print(f"   Found {len(o_positive_patients)} patients with O+ blood type")
        for _, patient in o_positive_patients.head(3).iterrows():
            print(f"   - {patient['full_name']} (DOB: {patient['date_of_birth']})")
    
    # Example 7: Storage room overview
    print("\n📦 7. Storage Rooms:")
    storage_rooms = retriever.get_storage_rooms()
    if not storage_rooms.empty:
        for _, room in storage_rooms.head(5).iterrows():
            print(f"   - {room['storage_number']} ({room['storage_type']}) - Floor {room['floor_number']}")
    
    print("\n✅ Example completed! You can now integrate these functions into your application.")
    print("\n💡 Integration Tips:")
    print("   1. Import: from src.utils.database import get_data_retriever")
    print("   2. Initialize: retriever = get_data_retriever()")
    print("   3. Use any of the retriever methods shown above")
    print("   4. All methods return pandas DataFrames for easy manipulation")
    print("   5. Use .to_dict() or .to_json() to convert DataFrames for API responses")

# Example function for API integration
def get_patient_data_for_api(patient_name_search: str = None, limit: int = 10) -> dict:
    """
    Example function showing how to format data for API responses
    """
    retriever = get_data_retriever()
    
    if patient_name_search:
        patients_df = retriever.search_patients_by_name(patient_name_search)
    else:
        patients_df = retriever.get_patients(limit=limit)
    
    # Convert DataFrame to dictionary for JSON response
    patients_data = patients_df.to_dict('records')
    
    return {
        "status": "success",
        "count": len(patients_data),
        "data": patients_data
    }

# Example function for Gradio integration
def get_hospital_overview() -> str:
    """
    Example function for displaying hospital overview in Gradio interface
    """
    retriever = get_data_retriever()
    stats = retriever.get_database_stats()
    
    overview = "🏥 Hospital Database Overview\n\n"
    overview += f"Total Records: {sum(stats.values()):,}\n\n"
    
    for table, count in stats.items():
        overview += f"• {table.replace('_', ' ').title()}: {count:,}\n"
    
    return overview

if __name__ == "__main__":
    try:
        main()
        
        # Example API usage
        print("\n" + "="*60)
        print("🌐 API Integration Example:")
        api_result = get_patient_data_for_api("John", limit=3)
        print(f"API Response: {api_result['count']} patients found")
        
        # Example Gradio usage
        print("\n📊 Gradio Integration Example:")
        gradio_overview = get_hospital_overview()
        print(gradio_overview)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1) 