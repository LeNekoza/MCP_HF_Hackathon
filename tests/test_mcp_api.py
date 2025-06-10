#!/usr/bin/env python3
"""
Test file to verify the MCP API endpoint for stream_response_with_state_1
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_mcp_api():
    """Test the MCP API using Gradio client"""
    try:
        from gradio_client import Client
        
        print("🔗 Connecting to Gradio client...")
        client = Client("http://127.0.0.1:7860/")
        
        print("📤 Sending test message...")
        result = client.predict(
            message="Find patient John Smith",
            history=[],
            api_name="/stream_response_with_state_1"
        )
        
        print("✅ Response received:")
        print("=" * 50)
        print(result)
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing MCP API: {str(e)}")
        return False

def test_multiple_queries():
    """Test multiple different queries"""
    test_messages = [
        "Hello! How can you help me?",
        "Show me hospital statistics",
        "What equipment is available?",
        "List all patients",
        "Find room R001 status"
    ]
    
    try:
        from gradio_client import Client
        client = Client("http://127.0.0.1:7860/")
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n🧪 Test {i}: {message}")
            print("-" * 40)
            
            result = client.predict(
                message=message,
                history=[],
                api_name="/stream_response_with_state_1"
            )
            
            print(f"Response: {str(result)[:200]}...")
            if len(str(result)) > 200:
                print("(truncated)")
            print("-" * 40)
            
    except Exception as e:
        print(f"❌ Error in multiple queries test: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting MCP API Tests")
    print("="*60)
    
    # Test 1: Basic API call
    print("\n📋 Test 1: Basic API Call")
    success = test_mcp_api()
    
    if success:
        # Test 2: Multiple queries
        print("\n📋 Test 2: Multiple Query Types")
        test_multiple_queries()
    else:
        print("❌ Basic test failed, skipping additional tests")
        print("\nPlease ensure:")
        print("1. Your Gradio server is running on http://127.0.0.1:7860")
        print("2. The gradio_client package is installed: pip install gradio_client") 