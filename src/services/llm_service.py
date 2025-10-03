"""
LLM Service for Google Gemini integration using LangChain.
"""

import json
import logging
import os
from typing import Dict, Any, Optional
from core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with Google Gemini API using LangChain."""
    
    def __init__(self):
        """Initialize the LLM service with Google Gemini."""
        self.llm = None
        self._initialized = False
        
    def _ensure_initialized(self):
        """Ensure the LLM service is initialized."""
        if not self._initialized:
            if not settings.google_ai_api_key:
                raise ValueError("GOOGLE_AI_API_KEY must be set in environment variables")
            
            try:
                # Use the google-generativeai package directly for better compatibility
                import google.generativeai as genai
                genai.configure(api_key=settings.google_ai_api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')  # Use the correct model name
                self._initialized = True
                logger.info("LLM Service initialized with Google Gemini")
            except ImportError as e:
                logger.error(f"Failed to import google.generativeai: {e}")
                raise ImportError("google-generativeai package is required")
            except Exception as e:
                logger.error(f"Failed to initialize Google Gemini: {e}")
                raise
    
    async def generate_srs_document(self, user_input: str) -> Dict[str, Any]:
        """
        Generate SRS document using Google Gemini.
        
        Args:
            user_input: Input requirements from frontend
            
        Returns:
            Dict containing the generated SRS document in JSON format
        """
        try:
            self._ensure_initialized()
            
            # Create the prompt for SRS generation
            prompt = f"""You are a Lead Business Analyst with extensive experience in creating IEEE-standard Software Requirements Specification documents.

Your task is to generate a comprehensive IEEE document in JSON format based on the provided input.

Return ONLY the document in JSON format along with metadata, without any additional comments, explanations, or text.

The JSON structure should include:
- title: Project title
- version: Document version
- date: Creation date
- author: Document author
- project_overview: High-level project description
- functional_requirements: Array of detailed functional requirements
- non_functional_requirements: Array of performance, security, usability requirements
- system_architecture: High-level system design description
- user_stories: Array of user stories and acceptance criteria
- constraints: Array of technical and business constraints
- assumptions: Array of project assumptions
- glossary: Object with technical terms and definitions

Ensure the document follows IEEE standards and is comprehensive yet clear.

Generate me a comprehensive IEEE document in JSON format based on the input: {user_input}

Return only valid JSON without any markdown formatting or additional text."""
            
            # Generate response
            logger.info(f"Generating SRS document for input: {user_input[:100]}...")
            response = self.model.generate_content(prompt)
            
            # Parse the response content
            content = response.text
            logger.debug(f"LLM Response: {content[:200]}...")
            
            # Try to parse as JSON
            try:
                # Clean the response if it has markdown formatting
                if content.startswith('```json'):
                    content = content.replace('```json', '').replace('```', '').strip()
                elif content.startswith('```'):
                    content = content.replace('```', '').strip()
                
                srs_document = json.loads(content)
                logger.info("Successfully generated and parsed SRS document")
                return srs_document
                
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse LLM response as JSON: {e}")
                # Return a structured fallback response
                return {
                    "title": "Generated SRS Document FALLBACK RESPONSE",
                    "version": "1.0",
                    "date": "2024-01-01",
                    "author": "BA Copilot AI",
                    "project_overview": user_input,
                    "functional_requirements": ["Requirements based on: " + user_input],
                    "non_functional_requirements": ["Performance and security requirements to be defined"],
                    "system_architecture": "Architecture to be defined based on requirements",
                    "user_stories": ["User story derived from: " + user_input],
                    "constraints": ["Technical constraints to be identified"],
                    "assumptions": ["Assumptions to be validated"],
                    "glossary": {"SRS": "Software Requirements Specification"},
                    "raw_response": content  # Include raw response for debugging
                }
                
        except Exception as e:
            logger.error(f"Error generating SRS document: {str(e)}")
            raise Exception(f"Failed to generate SRS document: {str(e)}")
    
    async def generate_content(
        self, 
        prompt: str, 
        temperature: float = 0.7
    ) -> str:
        """
        Generate content using Google Gemini with custom parameters.
        
        Args:
            prompt: User prompt
            temperature: Response creativity (0.0 to 1.0)
            
        Returns:
            Generated content as string
        """
        try:
            self._ensure_initialized()
            
            # Generate response
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            raise Exception(f"Failed to generate content: {str(e)}")


# Global instance - initialized lazily
_llm_service_instance = None

def get_llm_service() -> LLMService:
    """Get or create the global LLM service instance."""
    global _llm_service_instance
    if _llm_service_instance is None:
        _llm_service_instance = LLMService()
    return _llm_service_instance

# Backwards compatibility
llm_service = get_llm_service()