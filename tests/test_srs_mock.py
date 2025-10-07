import asyncio
import json
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

async def test_srs_service_locally():
    """Test SRS service with mock LLM response."""
    from src.services.srs_service import SRSService
    from unittest.mock import AsyncMock, patch
    
    print("Testing SRS service with mock LLM...")
    
    # Create mock LLM service
    mock_llm_service = AsyncMock()
    mock_llm_service.generate_srs_document.return_value = {
        "title": "Math Learning Web Game",
        "version": "1.0",
        "date": "2025-10-03",
        "author": "BA Copilot AI",
        "project_overview": "Interactive web-based math learning platform for elementary students",
        "functional_requirements": [
            "User registration and authentication",
            "Interactive math exercises",
            "Progress tracking",
            "Teacher dashboard",
            "Student performance analytics"
        ],
        "non_functional_requirements": [
            "Response time < 2 seconds",
            "Support 1000+ concurrent users",
            "HTTPS security",
            "Mobile responsive design"
        ],
        "system_architecture": "Web-based three-tier architecture with React frontend, Node.js backend, and MongoDB database",
        "user_stories": [
            "As a student, I want to solve math problems interactively",
            "As a teacher, I want to track student progress",
            "As a parent, I want to see my child's performance"
        ],
        "constraints": [
            "Must work on tablets and computers",
            "Limited to elementary math curriculum",
            "Budget constraint of $50,000"
        ],
        "assumptions": [
            "Students have basic computer skills",
            "Internet connectivity available",
            "Teachers will receive training"
        ],
        "glossary": {
            "SRS": "Software Requirements Specification",
            "UI": "User Interface",
            "API": "Application Programming Interface"
        }
    }
    
    # Test with mock
    with patch('services.srs_service.get_llm_service', return_value=mock_llm_service):
        srs_service = SRSService()
        
        test_input = "Create a web-based math learning game for elementary school students with interactive exercises, progress tracking, and teacher dashboard."
        
        print(f"Generating SRS for: {test_input[:50]}...")
        
        result = await srs_service.generate_srs(test_input, user_id="test-user")
        
        print("✅ SRS generation successful!")
        print(f"Document ID: {result['document_id']}")
        print(f"Status: {result['status']}")
        print(f"Generated at: {result['generated_at']}")
        print(f"Document title: {result['document']['title']}")
        
        # Validate response structure
        required_fields = ["document_id", "user_id", "generated_at", "input_description", "document", "status"]
        for field in required_fields:
            if field in result:
                print(f"✅ {field}: Present")
            else:
                print(f"❌ {field}: Missing")
        
        # Save result
        with open("test_srs_mock_output.json", "w") as f:
            json.dump(result, f, indent=2)
        print("📄 Full result saved to test_srs_mock_output.json")

if __name__ == "__main__":
    asyncio.run(test_srs_service_locally())