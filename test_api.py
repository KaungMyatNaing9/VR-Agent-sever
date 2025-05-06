import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_BASE_URL = "http://localhost:8000"  # Update with your actual API URL
USER_ID = "test_user_123"  # For demo purposes

def test_root_endpoint():
    """Test the root endpoint to verify API is running"""
    response = requests.get(f"{API_BASE_URL}/")
    print(f"Root endpoint response: {response.json()}")

def test_chat_endpoint(message):
    """Test the chat endpoint with a given message"""
    payload = {
        "message": message,
        "user_id": USER_ID
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{API_BASE_URL}/chat",
        headers=headers,
        data=json.dumps(payload)
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nUser: {message}")
        print(f"Assistant: {result['reply']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

def main():
    """Main function to run tests"""
    print("Testing VR Agent API...\n")
    
    # Test root endpoint
    test_root_endpoint()
    
    # Test chat endpoint with various queries
    print("\n=== Chat Tests ===")
    
    # Test general question
    test_chat_endpoint("What can you help me with?")
    
    # Test calendar question (will prompt for authentication if not already done)
    test_chat_endpoint("What's on my calendar tomorrow?")
    
    # Test creating an event
    test_chat_endpoint("Create a meeting with John on Friday at 3pm about project planning")
    
    print("\nTest completed!")

if __name__ == "__main__":
    main() 