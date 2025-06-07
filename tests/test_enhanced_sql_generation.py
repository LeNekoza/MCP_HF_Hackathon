#!/usr/bin/env python3
"""
Test script for enhanced SQL generation using Nebius model
"""

import sys
import os
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from src.services.advanced_database_mcp import advanced_database_mcp
    from src.models.nebius_model import NebiusModel
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


def test_database_query_detection():
    """Test if database queries are properly detected"""
    print("=== Testing Database Query Detection ===")
    
    test_queries = [
        "list top 30 patients with all relevant info",
        "how many rooms are available",
        "show me all doctors",
        "what's the weather like today",  # Non-database query
        "fetch all equipment in storage",
        "tell me a joke",  # Non-database query
    ]
    
    for query in test_queries:
        is_db_query = advanced_database_mcp.is_database_query(query)
        print(f"Query: '{query}' -> Database query: {is_db_query}")
    print()


def test_nebius_model_availability():
    """Test if Nebius model is available"""
    print("=== Testing Nebius Model Availability ===")
    
    nebius_model = NebiusModel()
    is_available = nebius_model.is_available()
    print(f"Nebius model available: {is_available}")
    
    if is_available:
        model_info = nebius_model.get_model_info()
        print(f"Model info: {model_info}")
    else:
        print("Nebius model not available - will use fallback SQL generation")
    print()


def test_sql_generation():
    """Test SQL generation for various queries"""
    print("=== Testing SQL Generation ===")
    
    test_queries = [
        "list top 30 patients with all relevant info",
        "show me available rooms",
        "get all nurses working in the hospital",
        "how many patients are currently admitted",
        "find all equipment in storage room 1",
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        print("-" * 50)
        
        try:
            sql_query = advanced_database_mcp.generate_advanced_sql(query)
            print("Generated SQL:")
            print(sql_query)
        except Exception as e:
            print(f"Error generating SQL: {e}")
        
        print("-" * 50)


def test_end_to_end_processing():
    """Test end-to-end query processing"""
    print("\n=== Testing End-to-End Processing ===")
    
    # Use a simple query that should work
    test_query = "how many patients do we have"
    
    print(f"Processing query: '{test_query}'")
    try:
        response = advanced_database_mcp.process_advanced_query(test_query)
        print("Response:")
        print(response)
    except Exception as e:
        print(f"Error processing query: {e}")


def main():
    """Main test function"""
    print("Enhanced SQL Generation Test Suite")
    print("=" * 50)
    
    test_database_query_detection()
    test_nebius_model_availability()
    test_sql_generation()
    
    # Only test end-to-end if database is configured
    if advanced_database_mcp.db_config:
        test_end_to_end_processing()
    else:
        print("\n=== Skipping End-to-End Test ===")
        print("Database not configured")
    
    print("\nTest suite completed!")


if __name__ == "__main__":
    main() 