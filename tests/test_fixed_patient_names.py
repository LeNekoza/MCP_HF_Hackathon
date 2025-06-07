#!/usr/bin/env python3
"""
Test script to verify patient names are showing correctly after the fix
"""

import sys
import os
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.services.advanced_database_mcp import advanced_database_mcp


def test_fixed_patient_queries():
    """Test that patient names are now showing correctly"""
    
    print("🧪 Testing Fixed Patient Name Display")
    print("=" * 60)
    
    test_queries = [
        "list 5 patient with names and full detail",
        "give me patient with DOB '16-12-1951' AND Blood group 'B+'",
        "show me patient names with blood group B+"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        print("-" * 40)
        
        # Process the complete query (SQL generation + formatting)
        response = advanced_database_mcp.process_advanced_query(query)
        print("Formatted Response:")
        print(response)
        
        print("\n" + "=" * 60)


if __name__ == "__main__":
    test_fixed_patient_queries() 