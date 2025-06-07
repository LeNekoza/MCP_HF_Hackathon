#!/usr/bin/env python3
"""
Debug script to examine SQL generation and results
"""

import sys
import os
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.services.advanced_database_mcp import advanced_database_mcp


def debug_patient_queries():
    """Debug patient-related queries to see what's happening"""
    
    print("🔍 Debugging Patient Query Results")
    print("=" * 50)
    
    test_queries = [
        "list 10 patient with names and full detail",
        "give me patient with DOB '16-12-1951' AND Blood group 'B+'"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        print("-" * 40)
        
        # Generate SQL
        sql_query = advanced_database_mcp.generate_advanced_sql(query)
        print("Generated SQL:")
        print(sql_query)
        print()
        
        # Execute query
        result = advanced_database_mcp.execute_query(sql_query)
        print(f"Query Success: {result.success}")
        print(f"Row Count: {result.row_count}")
        print(f"Tables Used: {result.tables_used}")
        
        if result.data:
            print("First Record Structure:")
            first_record = result.data[0]
            for key, value in first_record.items():
                print(f"  {key}: {value}")
            
            # Check what columns are available
            print(f"\nAvailable Columns: {list(first_record.keys())}")
            
            # Check if we have name fields
            name_fields = [k for k in first_record.keys() if 'name' in k.lower()]
            print(f"Name-related fields: {name_fields}")
        
        print("\n" + "=" * 50)


if __name__ == "__main__":
    debug_patient_queries() 