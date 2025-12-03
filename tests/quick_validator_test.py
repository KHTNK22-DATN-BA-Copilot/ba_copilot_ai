#!/usr/bin/env python3
"""Quick test script for validator integration"""
import sys
import os
sys.path.insert(0, '/app')

from services.mermaid_validator.subprocess_manager import MermaidSubprocessManager

def test_sync_validation():
    """Test synchronous validation"""
    print("Testing synchronous validation...")
    manager = MermaidSubprocessManager()
    
    # Test 1: Valid diagram
    print("\n1. Testing valid diagram...")
    result = manager.validate_sync("graph TD\n    A-->B")
    print(f"   Result: {result}")
    assert result.get('valid') is True, f"Expected valid=True, got {result}"
    print("   ✓ PASSED")
    
    # Test 2: Invalid diagram
    print("\n2. Testing invalid diagram...")
    result = manager.validate_sync("graph TD\n    A[Unclosed bracket")
    print(f"   Result: {result}")
    assert result.get('valid') is False, f"Expected valid=False, got {result}"
    print("   ✓ PASSED")
    
    # Test 3: Class diagram
    print("\n3. Testing class diagram...")
    class_diagram = """classDiagram
    class User {
        +String name
        +String email
    }"""
    result = manager.validate_sync(class_diagram)
    print(f"   Result: {result}")
    assert result.get('valid') is True, f"Expected valid=True, got {result}"
    print("   ✓ PASSED")
    
    manager.sync_client.close()
    print("\n✅ All synchronous validation tests passed!")

if __name__ == "__main__":
    try:
        test_sync_validation()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
