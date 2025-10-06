import asyncio
import json
import sys
import os
import requests
from unittest.mock import AsyncMock, patch

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

def test_srs_api_endpoint():
    """Test SRS API endpoint with FastAPI test client."""
    from fastapi.testclient import TestClient
    from src.main import app
    
    print("Testing SRS API endpoint with test client...")
    
    # Create mock LLM service
    mock_llm_service = AsyncMock()
    mock_llm_service.generate_srs_document.return_value = {
        "title": "Math Learning Web Game - API Test",
        "version": "1.0",
        "date": "2025-10-03",
        "author": "BA Copilot AI",
        "project_overview": "Interactive web-based math learning platform for elementary students",
        "functional_requirements": [
            "User registration and authentication",
            "Interactive math exercises",
            "Progress tracking and analytics",
            "Teacher dashboard with student management",
            "Gamification elements and rewards"
        ],
        "non_functional_requirements": [
            "Response time under 2 seconds",
            "Support 1000+ concurrent users",
            "99.9% uptime availability",
            "HTTPS security with data encryption",
            "Mobile responsive design"
        ],
        "system_architecture": "Modern web-based three-tier architecture with React frontend, FastAPI backend, and PostgreSQL database",
        "user_stories": [
            "As a student, I want to solve math problems in a fun, interactive way",
            "As a teacher, I want to track and analyze student progress",
            "As a parent, I want to monitor my child's learning achievements",
            "As an administrator, I want to manage curriculum content"
        ],
        "constraints": [
            "Must be compatible with tablets and desktop computers",
            "Limited to elementary math curriculum (grades K-5)",
            "Development budget constraint of $50,000",
            "Must comply with COPPA regulations for children's privacy"
        ],
        "assumptions": [
            "Students have basic computer navigation skills",
            "Reliable internet connectivity is available",
            "Teachers will receive adequate training on the platform",
            "Schools have necessary hardware infrastructure"
        ],
        "glossary": {
            "SRS": "Software Requirements Specification",
            "UI": "User Interface", 
            "API": "Application Programming Interface",
            "COPPA": "Children's Online Privacy Protection Act",
            "LMS": "Learning Management System"
        }
    }
    
    # Test with mock
    with patch('src.services.srs_service.get_llm_service', return_value=mock_llm_service):
        client = TestClient(app)
        
        # Test data
        request_data = {
            "project_input": "Create a comprehensive web-based math learning game for elementary school students with interactive exercises, progress tracking, teacher dashboard, and gamification elements to enhance learning engagement."
        }
        
        print(f"Sending POST request to /v1/srs/generate...")
        print(f"Request payload: {json.dumps(request_data, indent=2)}")
        
        # Make API request
        response = client.post("/v1/srs/generate", json=request_data)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API endpoint working successfully!")
            
            data = response.json()
            print(f"✅ Document ID: {data.get('document_id', 'Not found')}")
            print(f"✅ Status: {data.get('status', 'Not found')}")
            print(f"✅ Document Title: {data.get('document', {}).get('title', 'Not found')}")
            print(f"✅ Number of Functional Requirements: {len(data.get('document', {}).get('functional_requirements', []))}")
            print(f"✅ Number of User Stories: {len(data.get('document', {}).get('user_stories', []))}")
            
            # Save full response
            with open("test_api_response.json", "w") as f:
                json.dump(data, f, indent=2)
            print("📄 Full API response saved to test_api_response.json")
            
        else:
            print(f"❌ API request failed with status {response.status_code}")
            print(f"Response: {response.text}")

def test_srs_api_with_real_server():
    """Test SRS API endpoint with real running server."""
    print("\nTesting with real server (if running)...")
    
    try:
        # Test if server is running
        health_response = requests.get("http://localhost:8000/v1/health/", timeout=5)
        if health_response.status_code == 200:
            print("✅ Server is running!")
            
            # Test SRS endpoint with mock (since we can't use network)
            request_data = {
                "project_input": "Create a simple e-commerce website with user authentication, product catalog, shopping cart, and payment processing for a small retail business."
            }
            
            # For now, just show that the server is accessible
            print("✅ Server health check passed")
            print("Note: Real API test with Google AI would require network connectivity")
            
        else:
            print("❌ Server health check failed")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Server not accessible: {str(e)}")
        print("Note: Make sure to start the server with: python src/main.py")

if __name__ == "__main__":
    test_srs_api_endpoint()
    test_srs_api_with_real_server()