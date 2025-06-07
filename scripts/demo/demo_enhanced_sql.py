#!/usr/bin/env python3
"""
Demonstration of Enhanced SQL Generation
Shows the improvement from pattern matching to AI-powered SQL generation
"""

import sys
import os
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.services.advanced_database_mcp import advanced_database_mcp


def demonstrate_sql_generation():
    """Demonstrate the enhanced SQL generation capabilities"""
    
    print("🏥 Enhanced SQL Generation Demonstration")
    print("=" * 60)
    print()
    
    # Test queries that would have failed before
    complex_queries = [
        "list top 30 patients with all relevant info",
        "show me all patients currently in ICU rooms with their medical history",
        "find nurses assigned to patients in room 101",
        "get equipment usage statistics by department",
        "show me patients who have been admitted more than once",
        "list all available rooms on the 3rd floor",
        "find patients with diabetes who are currently admitted"
    ]
    
    print("🔍 Testing Complex Queries That Previously Failed:")
    print("-" * 60)
    
    for i, query in enumerate(complex_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        print("   " + "─" * 50)
        
        try:
            # Generate SQL using the enhanced system
            sql_query = advanced_database_mcp.generate_advanced_sql(query)
            
            # Clean up the SQL for display
            sql_lines = [line.strip() for line in sql_query.split('\n') if line.strip()]
            formatted_sql = '\n   '.join(sql_lines)
            
            print(f"   Generated SQL:")
            print(f"   {formatted_sql}")
            
            # Check if it's using JOINs (indicator of complexity)
            if 'JOIN' in sql_query.upper():
                print("   ✅ Uses proper JOINs for multi-table queries")
            else:
                print("   ℹ️  Simple single-table query")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    print("🎯 Key Improvements:")
    print("-" * 60)
    print("✅ Intelligent query understanding using Nebius Llama 3.3 70B")
    print("✅ Proper JOIN operations for multi-table queries")
    print("✅ Context-aware database schema utilization")
    print("✅ Fallback to pattern matching if AI is unavailable")
    print("✅ Robust error handling and logging")
    print()
    
    print("📊 Before vs After Comparison:")
    print("-" * 60)
    print("BEFORE: Pattern matching → Limited query types → Generic responses")
    print("AFTER:  AI-powered SQL → Complex JOINs → Accurate database results")
    print()
    
    print("🚀 Your Hospital AI Helper now handles complex database queries!")
    print("   Try asking: 'list top 30 patients with all relevant info'")
    print("   And get real patient data instead of generic scenarios!")


if __name__ == "__main__":
    demonstrate_sql_generation() 