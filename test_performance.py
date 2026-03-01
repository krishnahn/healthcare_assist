"""
Performance test script for the RAG API
"""
import requests
import time
import json

BASE_URL = "http://127.0.0.1:8000"

def test_search(query: str, store_name: str, test_name: str):
    """Test search endpoint and measure time"""
    print(f"\n{'='*60}")
    print(f"Test: {test_name}")
    print(f"Query: {query}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/search",
            json={
                "query": query,
                "store_name": store_name
            },
            timeout=60
        )
        
        end_time = time.time()
        total_time = end_time - start_time
        
        if response.status_code == 200:
            data = response.json()
            cached = data.get('metadata', {}).get('cached', False)
            processing_time = data.get('metadata', {}).get('processing_time', 0)
            
            print(f"✅ Status: SUCCESS")
            print(f"⏱️  Total Request Time: {total_time:.2f} seconds")
            print(f"⏱️  Server Processing Time: {processing_time:.2f} seconds")
            print(f"📦 Cached: {cached}")
            print(f"📝 Answer length: {len(data.get('answer', ''))} chars")
            print(f"📚 Citations: {len(data.get('citations', []))}")
            print(f"\n📄 Answer (first 300 chars):")
            print(f"{data.get('answer', '')[:300]}...")
        else:
            print(f"❌ Status: FAILED ({response.status_code})")
            print(f"Error: {response.text}")
        
        return total_time, response.status_code == 200
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error - Is the server running?")
        return None, False
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, False

def main():
    print("\n" + "="*60)
    print("🚀 RAG API PERFORMANCE TEST")
    print("="*60)
    
    # Test 1: Health check
    print("\n📍 Test 0: Health Check")
    try:
        start = time.time()
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ Health check: {time.time() - start:.3f}s - {r.json()}")
    except Exception as e:
        print(f"❌ Server not reachable: {e}")
        print("\n⚠️  Please start the server with: python api.py")
        return
    
    # Test 2: Simple query (first time - no cache)
    time1, _ = test_search(
        "What is the key information in the ICAR reports?",
        "my-docs",
        "Simple Query - FIRST REQUEST (No Cache)"
    )
    
    # Test 3: Same query (should hit cache)
    time2, _ = test_search(
        "What is the key information in the ICAR reports?",
        "my-docs",
        "Simple Query - SECOND REQUEST (Should be Cached)"
    )
    
    # Test 4: Complex query
    time3, _ = test_search(
        "List all the districts in Punjab and their agricultural statistics",
        "my-docs",
        "Complex Query - FIRST REQUEST (No Cache)"
    )
    
    # Test 5: Same complex query (should hit cache)
    time4, _ = test_search(
        "List all the districts in Punjab and their agricultural statistics",
        "my-docs",
        "Complex Query - SECOND REQUEST (Should be Cached)"
    )
    
    # Summary
    print("\n" + "="*60)
    print("📊 PERFORMANCE SUMMARY")
    print("="*60)
    
    if time1:
        print(f"Simple Query (Uncached):   {time1:.2f}s")
    if time2:
        print(f"Simple Query (Cached):     {time2:.2f}s")
        if time1 and time2:
            improvement = ((time1 - time2) / time1) * 100
            print(f"  → Cache Improvement:     {improvement:.1f}% faster")
    
    if time3:
        print(f"\nComplex Query (Uncached):  {time3:.2f}s")
    if time4:
        print(f"Complex Query (Cached):    {time4:.2f}s")
        if time3 and time4:
            improvement = ((time3 - time4) / time3) * 100
            print(f"  → Cache Improvement:     {improvement:.1f}% faster")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
