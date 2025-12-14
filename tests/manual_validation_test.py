#!/usr/bin/env python3
"""
Simple test script to verify diagram generation with validation works end-to-end.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflows.class_diagram_workflow import class_diagram_graph
from workflows.usecase_diagram_workflow import usecase_diagram_graph
from workflows.activity_diagram_workflow import activity_diagram_graph

def test_class_diagram():
    """Test class diagram generation with validation"""
    print("\n=== Testing Class Diagram Generation with Validation ===")
    try:
        result = class_diagram_graph.invoke({
            "user_message": "Create a simple class diagram for a Library Management System with Book and Member classes"
        })
        print("✅ Class diagram generated successfully!")
        print(f"Type: {result['response']['type']}")
        print(f"Detail length: {len(result['response']['detail'])} characters")
        if "Validation Warning" in result['response']['detail']:
            print("⚠️  Validation warning present in output")
        else:
            print("✅ No validation warnings")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_usecase_diagram():
    """Test usecase diagram generation with validation"""
    print("\n=== Testing Use Case Diagram Generation with Validation ===")
    try:
        result = usecase_diagram_graph.invoke({
            "user_message": "Create a usecase diagram for an ATM system"
        })
        print("✅ Use case diagram generated successfully!")
        print(f"Type: {result['response']['type']}")
        print(f"Detail length: {len(result['response']['detail'])} characters")
        if "Validation Warning" in result['response']['detail']:
            print("⚠️  Validation warning present in output")
        else:
            print("✅ No validation warnings")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_activity_diagram():
    """Test activity diagram generation with validation"""
    print("\n=== Testing Activity Diagram Generation with Validation ===")
    try:
        result = activity_diagram_graph.invoke({
            "user_message": "Create an activity diagram for online shopping checkout process"
        })
        print("✅ Activity diagram generated successfully!")
        print(f"Type: {result['response']['type']}")
        print(f"Detail length: {len(result['response']['detail'])} characters")
        if "Validation Warning" in result['response']['detail']:
            print("⚠️  Validation warning present in output")
        else:
            print("✅ No validation warnings")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("BA Copilot AI - Diagram Generation with Validation Test")
    print("=" * 70)
    
    results = []
    results.append(("Class Diagram", test_class_diagram()))
    results.append(("Use Case Diagram", test_usecase_diagram()))
    results.append(("Activity Diagram", test_activity_diagram()))
    
    print("\n" + "=" * 70)
    print("Test Summary:")
    print("=" * 70)
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name:25} {status}")
    
    all_passed = all(passed for _, passed in results)
    print("=" * 70)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED!")
        sys.exit(1)
