#!/usr/bin/env python3
"""End-to-end test for diagram generation with validation"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_class_diagram_generation():
    """Test class diagram generation with validation"""
    print("\n" + "="*60)
    print("Test 1: Class Diagram Generation with Validation")
    print("="*60)
    
    payload = {
        "message": "Create a simple class diagram with User and Admin classes"
    }
    
    print(f"\n📤 Sending request to {BASE_URL}/api/v1/generate/class-diagram")
    start_time = time.time()
    
    response = requests.post(
        f"{BASE_URL}/api/v1/generate/class-diagram",
        json=payload,
        timeout=90
    )
    
    elapsed = time.time() - start_time
    print(f"⏱️  Response time: {elapsed:.2f}s")
    print(f"📊 Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Response received")
        print(f"📝 Response type: {data.get('type')}")
        
        detail = data.get('detail', '')
        if '```mermaid' in detail:
            print(f"✅ Mermaid diagram generated")
            
            # Check for validation warning
            if 'Validation Warning' in detail:
                print(f"⚠️  Diagram has validation warnings")
            else:
                print(f"✅ Diagram passed validation")
            
            # Show first 200 chars of diagram
            preview = detail[:200].replace('\n', '\\n')
            print(f"📄 Preview: {preview}...")
            return True
        else:
            print(f"❌ No mermaid diagram in response")
            print(f"Response: {json.dumps(data, indent=2)}")
            return False
    else:
        print(f"❌ Request failed: {response.text}")
        return False

def test_usecase_diagram_generation():
    """Test usecase diagram generation with validation"""
    print("\n" + "="*60)
    print("Test 2: Use Case Diagram Generation with Validation")
    print("="*60)
    
    payload = {
        "message": "Create a use case diagram for a login system"
    }
    
    print(f"\n📤 Sending request to {BASE_URL}/api/v1/generate/usecase-diagram")
    start_time = time.time()
    
    response = requests.post(
        f"{BASE_URL}/api/v1/generate/usecase-diagram",
        json=payload,
        timeout=90
    )
    
    elapsed = time.time() - start_time
    print(f"⏱️  Response time: {elapsed:.2f}s")
    print(f"📊 Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Response received")
        
        detail = data.get('detail', '')
        if '```mermaid' in detail or 'graph' in detail:
            print(f"✅ Diagram generated")
            
            if 'Validation Warning' in detail:
                print(f"⚠️  Diagram has validation warnings (expected for some use case diagrams)")
            else:
                print(f"✅ Diagram passed validation")
            return True
        else:
            print(f"❌ No diagram in response")
            return False
    else:
        print(f"❌ Request failed: {response.text}")
        return False

def test_activity_diagram_generation():
    """Test activity diagram generation with validation"""
    print("\n" + "="*60)
    print("Test 3: Activity Diagram Generation with Validation")
    print("="*60)
    
    payload = {
        "message": "Create an activity diagram for user registration"
    }
    
    print(f"\n📤 Sending request to {BASE_URL}/api/v1/generate/activity-diagram")
    start_time = time.time()
    
    response = requests.post(
        f"{BASE_URL}/api/v1/generate/activity-diagram",
        json=payload,
        timeout=90
    )
    
    elapsed = time.time() - start_time
    print(f"⏱️  Response time: {elapsed:.2f}s")
    print(f"📊 Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Response received")
        
        detail = data.get('detail', '')
        if '```mermaid' in detail or 'graph' in detail:
            print(f"✅ Diagram generated")
            
            if 'Validation Warning' in detail:
                print(f"⚠️  Diagram has validation warnings")
            else:
                print(f"✅ Diagram passed validation")
            return True
        else:
            print(f"❌ No diagram in response")
            return False
    else:
        print(f"❌ Request failed: {response.text}")
        return False

if __name__ == "__main__":
    print("\n🚀 Starting End-to-End Diagram Generation Tests")
    print("="*60)
    
    results = []
    
    # Test health endpoint first
    try:
        health = requests.get(f"{BASE_URL}/health", timeout=5)
        if health.status_code == 200:
            print("✅ Health check passed")
        else:
            print("❌ Health check failed")
            exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to service: {e}")
        exit(1)
    
    # Run tests
    results.append(("Class Diagram", test_class_diagram_generation()))
    results.append(("Use Case Diagram", test_usecase_diagram_generation()))
    results.append(("Activity Diagram", test_activity_diagram_generation()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name}: {status}")
    
    total = len(results)
    passed_count = sum(1 for _, p in results if p)
    print(f"\nTotal: {passed_count}/{total} tests passed")
    
    if passed_count == total:
        print("\n🎉 All tests passed!")
        exit(0)
    else:
        print("\n⚠️  Some tests failed")
        exit(1)
