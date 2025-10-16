#!/usr/bin/env python3
"""
Comprehensive Integration Test for BA Copilot System
Tests the complete workflow: User Registration → Login → Project Creation → SRS Generation
"""

import requests
import json
import time
import sys
from datetime import datetime

# Service endpoints
BACKEND_URL = "http://localhost:8010"
AI_SERVICE_URL = "http://localhost:8000"

def test_service_health():
    """Test that all services are healthy."""
    print("🔍 Testing service health...")
    
    # Test backend health
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend service is healthy")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend service not accessible: {e}")
        return False
    
    # Test AI service health
    try:
        response = requests.get(f"{AI_SERVICE_URL}/v1/health", timeout=10)
        if response.status_code == 200:
            print("✅ AI service is healthy")
        else:
            print(f"❌ AI service health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ AI service not accessible: {e}")
        return False
    
    return True

def test_user_registration():
    """Test user registration."""
    print("🔍 Testing user registration...")
    
    # Generate unique username
    timestamp = int(time.time())
    test_user = {
        "name": f"Test User {timestamp}",
        "email": f"test_{timestamp}@example.com",
        "passwordhash": "TestPassword123!"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/auth/register",
            json=test_user,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ User registration successful")
            return test_user
        else:
            print(f"❌ User registration failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ User registration error: {e}")
        return None

def test_user_login(user_data):
    """Test user login and get access token."""
    print("🔍 Testing user login...")
    
    try:
        login_data = {
            "email": user_data["email"],
            "password": user_data["passwordhash"]
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/v1/auth/login",
            data=login_data,  # Form data, not JSON
            timeout=30
        )
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            if access_token:
                print("✅ User login successful")
                return access_token
            else:
                print("❌ No access token in login response")
                return None
        else:
            print(f"❌ User login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ User login error: {e}")
        return None

def test_project_creation(access_token):
    """Test project creation."""
    print("🔍 Testing project creation...")
    
    project_data = {
        "name": f"Test Project {int(time.time())}",
        "description": "A comprehensive test project for integration testing"
    }
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/projects/",
            json=project_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            project = response.json()
            print("✅ Project creation successful")
            return project
        else:
            print(f"❌ Project creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Project creation error: {e}")
        return None

def test_srs_generation():
    """Test SRS document generation."""
    print("🔍 Testing SRS generation...")
    
    srs_request = {
        "project_input": "Create a web-based project management system that allows users to register, create projects, assign tasks, track progress, and generate reports. The system should have user authentication, role-based access control, and real-time notifications."
    }
    
    try:
        response = requests.post(
            f"{AI_SERVICE_URL}/v1/srs/generate",
            json=srs_request,
            timeout=180  # 3 minutes timeout for AI generation
        )
        
        if response.status_code == 200:
            srs_data = response.json()
            if srs_data.get("status") == "completed" and "document" in srs_data:
                document = srs_data["document"]
                if "title" in document and "project_overview" in document:
                    print("✅ SRS generation successful")
                    print(f"📄 Generated SRS: {document.get('title', 'Unknown Title')}")
                    return srs_data
                else:
                    print("❌ SRS document missing required fields")
                    return None
            else:
                print("❌ SRS generation not completed or missing document")
                return None
        else:
            print(f"❌ SRS generation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ SRS generation error: {e}")
        return None

def main():
    """Run the comprehensive integration test."""
    print("🚀 Starting BA Copilot Integration Test")
    print("=" * 50)
    
    start_time = time.time()
    
    # Test 1: Service Health
    if not test_service_health():
        print("❌ Service health checks failed. Exiting.")
        sys.exit(1)
    
    print()
    
    # Test 2: User Registration
    user_data = test_user_registration()
    if not user_data:
        print("❌ User registration failed. Exiting.")
        sys.exit(1)
    
    print()
    
    # Test 3: User Login
    access_token = test_user_login(user_data)
    if not access_token:
        print("❌ User login failed. Exiting.")
        sys.exit(1)
    
    print()
    
    # Test 4: Project Creation
    project = test_project_creation(access_token)
    if not project:
        print("❌ Project creation failed. Exiting.")
        sys.exit(1)
    
    print()
    
    # Test 5: SRS Generation
    srs_data = test_srs_generation()
    if not srs_data:
        print("❌ SRS generation failed. Exiting.")
        sys.exit(1)
    
    print()
    print("=" * 50)
    print("🎉 ALL INTEGRATION TESTS PASSED!")
    print(f"⏱️ Total test time: {time.time() - start_time:.1f} seconds")
    print()
    print("✅ User Registration → Login → Project Creation → SRS Generation workflow is fully functional!")
    
if __name__ == "__main__":
    main()