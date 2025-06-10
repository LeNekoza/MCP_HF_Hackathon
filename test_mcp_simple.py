from gradio_client import Client

# Test the exact API from Gradio docs
def test_basic():
    try:
        print("🔗 Connecting to Gradio server...")
        client = Client("http://127.0.0.1:7860/")
        
        print("📤 Sending test message...")
        result = client.predict(
            message="Hello!!",
            history=[],
            api_name="/stream_response_with_state_1"
        )
        
        print("✅ SUCCESS!")
        print("Response:", result)
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_basic() 