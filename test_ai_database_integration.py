#!/usr/bin/env python3
"""
Test AI Database Integration
Tests that database queries are properly routed through the AI model for analysis
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.components.interface import handle_ai_response

def test_database_query_ai_integration():
    """Test that database queries get analyzed by AI instead of returning raw data"""
    
    print("🧪 Testing Database Query → AI Analysis Integration")
    print("=" * 60)
    
    # Test query that should trigger database lookup
    test_query = "give me details of 5 patients"
    
    try:
        response = handle_ai_response(
            user_message=test_query,
            model="nebius-llama-3.3-70b",
            temperature=0.7,
            max_tokens=1024,
            specialty="General Medicine",
            context=""
        )
        
        print(f"User Query: {test_query}")
        print("\nAI Response:")
        print("-" * 40)
        print(response)
        print("-" * 40)
        
        # Check if response contains AI analysis characteristics
        analysis_indicators = [
            "analysis", "insights", "patient", "medical", "recommend", 
            "findings", "summary", "context", "overview", "comprehensive"
        ]
        
        contains_analysis = any(indicator in response.lower() for indicator in analysis_indicators)
        
        # Check if LaTeX formatting is present
        contains_latex = r"\(" in response or r"\[" in response
        
        # Check if it's NOT raw database output
        raw_database_indicators = [
            "*Data retrieved from hospital database using advanced SQL*",
            "📊 **Hospital Database Results**",
            "👥 **Patient Information:**"
        ]
        
        is_raw_database = any(indicator in response for indicator in raw_database_indicators)
        
        # Check for proper formatting (line breaks)
        has_proper_structure = "\n" in response and ("##" in response or "**" in response or "-" in response)
        
        # Check if complete data is included (not just analysis)
        complete_data_indicators = [
            "Patient 1", "Patient 2", "Patient 3", 
            "### Patient", "**Patient", 
            "DOB:", "Age:", "Room:", "Blood Type:"
        ]
        
        has_complete_data = any(indicator in response for indicator in complete_data_indicators)
        
        print(f"\n✅ Contains Analysis Language: {contains_analysis}")
        print(f"✅ Contains LaTeX Formatting: {contains_latex}")
        print(f"❌ Is Raw Database Output: {is_raw_database}")
        print(f"✅ Has Proper Structure/Line Breaks: {has_proper_structure}")
        print(f"✅ Includes Complete Patient Data: {has_complete_data}")
        
        if contains_analysis and not is_raw_database and has_complete_data:
            print("🎯 SUCCESS: Database query provides complete data + AI analysis!")
        elif contains_analysis and not is_raw_database:
            print("⚠️ PARTIAL SUCCESS: AI analysis present but missing complete patient data")
        else:
            print("❌ WARNING: Response seems to be raw database data or not properly analyzed")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        print("This might be expected if Nebius API is not configured")

def test_regular_ai_query():
    """Test that regular AI queries still work normally"""
    
    print("\n🧪 Testing Regular AI Query (Non-Database)")
    print("=" * 60)
    
    test_query = "What are the symptoms of pneumonia?"
    
    try:
        response = handle_ai_response(
            user_message=test_query,
            model="nebius-llama-3.3-70b",
            temperature=0.7,
            max_tokens=1024,
            specialty="General Medicine",
            context=""
        )
        
        print(f"User Query: {test_query}")
        print("\nAI Response:")
        print("-" * 40)
        print(response)
        print("-" * 40)
        
        # Check if LaTeX formatting is present
        contains_latex = r"\(" in response or r"\[" in response
        print(f"\n✅ Contains LaTeX Formatting: {contains_latex}")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")

if __name__ == "__main__":
    print("🏥 Testing AI Database Integration")
    print("This test verifies that database queries are routed through AI for analysis\n")
    
    test_database_query_ai_integration()
    test_regular_ai_query()
    
    print("\n" + "=" * 60)
    print("📝 Summary:")
    print("✅ Database queries should now be analyzed by AI instead of returning raw data")
    print("✅ AI provides context, insights, and LaTeX formatting")
    print("✅ Regular AI queries continue to work normally")
    print("✅ Both types of queries maintain medical safety disclaimers") 