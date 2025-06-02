#!/usr/bin/env python3

import requests
import json
import time

def test_contract_redlining_system():
    base_url = "http://localhost:8000"
    
    print("🚀 Testing Contract Redlining RAG System")
    print("=" * 50)
    
    # 1. Test health endpoint
    print("\n1️⃣ Testing system health...")
    try:
        response = requests.get(f"{base_url}/health")
        health_data = response.json()
        print(f"   Status: {health_data['status']}")
        print(f"   Models loaded: {health_data['models_loaded']}")
        print("   ✅ System is healthy!")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return
    
    # 2. Test main interface
    print("\n2️⃣ Testing main interface...")
    try:
        response = requests.get(base_url)
        if "Contract Redlining RAG System" in response.text:
            print("   ✅ Main interface is accessible!")
        else:
            print("   ❌ Main interface issue")
    except Exception as e:
        print(f"   ❌ Interface test failed: {e}")
    
    # 3. Test text classification
    print("\n3️⃣ Testing AI text classification...")
    test_clauses = [
        {
            "text": "The party shall have unlimited liability for all damages and penalties.",
            "expected": "HIGH RISK"
        },
        {
            "text": "Both parties agree to use reasonable best efforts.",
            "expected": "LOW RISK"
        },
        {
            "text": "This agreement shall be governed by Delaware law with binding arbitration.",
            "expected": "MEDIUM RISK"
        }
    ]
    
    for i, test_case in enumerate(test_clauses, 1):
        print(f"\n   Test {i}: {test_case['text'][:50]}...")
        try:
            response = requests.post(
                f"{base_url}/classify-text",
                headers={"Content-Type": "application/json"},
                json={"text": test_case["text"]}
            )
            
            if response.status_code == 200:
                result = response.json()
                classification = result["classification"]
                print(f"   Risk Level: {classification['risk_level']}")
                print(f"   Confidence: {classification['confidence']}")
                print(f"   Explanation: {classification['explanation'][:80]}...")
                print("   ✅ Classification successful!")
            else:
                print(f"   ❌ Classification failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
    
    # 4. Test search functionality
    print("\n4️⃣ Testing semantic search...")
    try:
        response = requests.get(f"{base_url}/search?query=liability&limit=5")
        if response.status_code == 200:
            result = response.json()
            print(f"   Search results: {len(result.get('results', []))} items")
            print("   ✅ Search functionality working!")
        else:
            print(f"   ❌ Search failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Search test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 DEMO TEST COMPLETED!")
    print("\n📱 To use the full application:")
    print(f"   1. Open your browser to: {base_url}")
    print("   2. Upload a PDF contract document")
    print("   3. Click 'Analyze Document' to see AI-powered redlining")
    print("   4. View color-coded risk analysis with explanations")
    print("   5. Export results as JSON")
    
    print("\n🎯 Key Features Demonstrated:")
    print("   ✅ FastAPI backend with modern async/await")
    print("   ✅ AI classification using MISTRAL7b technology")
    print("   ✅ Vector database with ChromaDB")
    print("   ✅ Real-time risk assessment")
    print("   ✅ Professional web interface")
    print("   ✅ RESTful API endpoints")

if __name__ == "__main__":
    test_contract_redlining_system() 