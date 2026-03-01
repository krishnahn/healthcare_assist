"""
Test script for FastAPI endpoints
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print("Health Check:", response.json())

def test_list_stores():
    """Test list stores endpoint"""
    response = requests.get(f"{BASE_URL}/api/stores")
    print("\nAvailable Stores:", json.dumps(response.json(), indent=2))

def test_search():
    """Test search endpoint"""
    data = {
        "query": "What are the key findings from ICAR reports?",
        "store_name": "my-docs",
        "temperature": 0.0,
        "max_tokens": 1024
    }
    
    response = requests.post(f"{BASE_URL}/api/search", json=data)
    result = response.json()
    
    print("\n=== Search Result ===")
    print(f"Answer: {result['answer']}")
    print(f"\nCitations: {len(result.get('citations', []))} sources")
    print(f"Processing Time: {result['metadata'].get('processing_time', 0):.2f}s")

def test_upload():
    """Test file upload endpoint"""
    # Example: upload a file
    files = {
        'file': open('data/documents/sample_document.txt', 'rb')
    }
    data = {
        'store_name': 'my-docs'
    }
    
    response = requests.post(f"{BASE_URL}/api/upload", files=files, data=data)
    print("\nUpload Result:", response.json())

if __name__ == "__main__":
    print("Testing FastAPI Endpoints...\n")
    
    try:
        # Test 1: Health check
        test_health()
        
        # Test 2: List stores
        test_list_stores()
        
        # Test 3: Search
        test_search()
        
        # Test 4: Upload (optional - uncomment if needed)
        # test_upload()
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API. Make sure the server is running!")
        print("Run: uvicorn api:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")
