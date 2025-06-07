#!/usr/bin/env python3
"""
Test script for the Chatbot Loader Integration

This script launches the Gradio interface to test the loading indicators
functionality in the hospital AI assistant chatbot.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.components.interface import create_main_interface


def test_loader_integration():
    """Test the chatbot loader integration"""

    # Mock configuration for testing
    test_config = {
        "default_model": "nebius-llama-3.3-70b",
        "api_key": "test-key",  # This will show fallback behavior
        "temperature": 0.7,
        "max_tokens": 1000,
    }

    print("🧪 Testing Chatbot Loader Integration...")
    print("=" * 50)
    print()
    print("✅ Features being tested:")
    print("  • Loading indicators with dynamic status text")
    print("  • Animated dots and shimmer effects")
    print("  • Different loading states for different operations:")
    print("    - 🤔 Thinking...")
    print("    - 🔍 Analyzing your request...")
    print("    - 🏥 Checking hospital systems...")
    print("    - 🗄️ Querying the database...")
    print("    - 🧠 Analyzing results with AI...")
    print("    - 🚀 Generating response...")
    print("  • Accessibility features (aria-live, role attributes)")
    print("  • Responsive design and dark mode support")
    print("  • Reduced motion support")
    print()
    print("🌐 Starting Gradio interface...")
    print("📝 Try these test messages:")
    print("  • 'Hello' (general AI response)")
    print("  • 'Show me patient information' (database query)")
    print("  • 'Hospital status update' (quick action)")
    print()

    try:
        # Create the interface
        demo = create_main_interface(test_config)

        # Launch with specific settings for testing
        demo.launch(
            server_name="127.0.0.1",
            server_port=7860,
            share=False,
            debug=True,
            quiet=False,
            inbrowser=True,
        )

    except Exception as e:
        print(f"❌ Error launching interface: {e}")
        print("\n🔧 Troubleshooting:")
        print("  • Make sure all dependencies are installed")
        print("  • Check that port 7860 is available")
        print("  • Verify the src directory structure is correct")
        return False

    return True


if __name__ == "__main__":
    print("🏥 Hospital AI Helper - Chatbot Loader Integration Test")
    print("=" * 60)
    print()

    success = test_loader_integration()

    if success:
        print("\n✅ Test completed successfully!")
        print("🎯 The loader integration should now be visible in the interface")
    else:
        print("\n❌ Test failed - please check the error messages above")
        sys.exit(1)
