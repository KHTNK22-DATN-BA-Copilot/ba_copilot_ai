import asyncio
import json
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

async def test_srs_generation_real():
    """Test SRS generation with actual Google AI API call."""
    from src.services.llm_service import get_llm_service
    from src.core.config import settings
    
    print("Testing SRS generation with Google AI API...")
    print(f"Google AI API Key present: {bool(settings.google_ai_api_key)}")
    
    if not settings.google_ai_api_key or settings.google_ai_api_key == "your-google-ai-api-key-here":
        print("❌ GOOGLE_AI_API_KEY not properly set in .env file")
        print("Please set a valid Google AI API key in the .env file")
        return
    
    try:
        llm_service = get_llm_service()
        
        test_input = "Create a web-based math learning game for elementary school students with interactive exercises, progress tracking, and teacher dashboard."
        
        print(f"Generating SRS for: {test_input[:50]}...")
        
        result = await llm_service.generate_srs_document(test_input)
        
        print("✅ SRS generation successful!")
        print(f"Generated document with keys: {list(result.keys())}")
        print(f"Title: {result.get('title', 'Not found')}")
        print(f"Version: {result.get('version', 'Not found')}")
        
        # Save result for inspection
        with open("test_srs_output.json", "w") as f:
            json.dump(result, f, indent=2)
        print("📄 Full result saved to test_srs_output.json")
        
    except Exception as e:
        print(f"❌ Error during SRS generation: {str(e)}")
        print(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    asyncio.run(test_srs_generation_real())