"""
LLM Service for Google Gemini integration using LangChain.
"""

from datetime import datetime
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
            # Priority: OpenRouter (DeepSeek free) -> Google Gemini -> OpenAI -> Fallback
            if settings.openrouter_api_key:
                try:
                    from openai import AsyncOpenAI
                    self.client = AsyncOpenAI(
                        api_key=settings.openrouter_api_key,
                        base_url="https://openrouter.ai/api/v1",
                    )
                    self.provider = "openrouter"
                    self._initialized = True
                    logger.info("LLM Service initialized with OpenRouter via OpenAI SDK")
                    return
                except ImportError as e:
                    logger.warning(f"OpenAI package not available for OpenRouter: {e}")
                except Exception as e:
                    logger.warning(f"Failed to initialize OpenRouter: {e}")

            # Next: Google Gemini (1.5)
            if settings.google_ai_api_key:
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=settings.google_ai_api_key)
                    # Prefer a stable, widely available model
                    self.model = genai.GenerativeModel('gemini-1.5-flash')
                    self.provider = "google"
                    self._initialized = True
                    logger.info("LLM Service initialized with Google Gemini")
                    return
                except ImportError as e:
                    logger.warning(f"Failed to import google.generativeai: {e}")
                except Exception as e:
                    logger.warning(f"Failed to initialize Google Gemini: {e}")

            # Finally: OpenAI
            if settings.openai_api_key:
                try:
                    from openai import AsyncOpenAI
                    self.client = AsyncOpenAI(api_key=settings.openai_api_key)
                    self.provider = "openai"
                    self._initialized = True
                    logger.info("LLM Service initialized with OpenAI")
                    return
                except ImportError as e:
                    logger.warning(f"OpenAI package not available: {e}")
                except Exception as e:
                    logger.warning(f"Failed to initialize OpenAI: {e}")

            # Fallback provider (no external keys) to keep API functional
            self.provider = "fallback"
            self._initialized = True
            logger.info("LLM Service initialized in fallback mode (no external LLM keys)")
    
    async def generate_srs_document(self, user_input: str) -> Dict[str, Any]:
        """
        Generate SRS document using OpenAI or Google Gemini.
        
        Args:
            user_input: Input requirements from frontend
            
        Returns:
            Dict containing the generated SRS document in JSON format
        """
        try:
            self._ensure_initialized()
            
            # Create the prompt for SRS generation
            prompt = f"""
You are a Lead Business Analyst with extensive experience in creating IEEE-standard Software Requirements Specification documents.

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

Generate me a comprehensive IEEE document in JSON format based on the input: 
\"{user_input}\"

Return only valid JSON without any markdown formatting or additional text."""
            
            # Generate response based on provider
            logger.info(f"Generating SRS document using {self.provider} for input: {user_input[:100]}...")
            
            if self.provider in ("openai", "openrouter"):
                extra_headers = None
                if self.provider == "openrouter":
                    extra_headers = {}
                    if settings.openrouter_referer:
                        extra_headers["HTTP-Referer"] = settings.openrouter_referer
                    if settings.openrouter_title:
                        extra_headers["X-Title"] = settings.openrouter_title

                # Use DeepSeek free model on OpenRouter first
                model_id = (
                    "deepseek/deepseek-chat-v3.1:free" if self.provider == "openrouter" else "gpt-3.5-turbo"
                )

                response = await self.client.chat.completions.create(
                    model=model_id,
                    messages=[
                        {"role": "system", "content": "You are a professional Business Analyst. Return only valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=4000,
                    extra_headers=extra_headers
                )
                content = response.choices[0].message.content or ""
            elif self.provider == "google":
                response = self.model.generate_content(prompt)
                content = response.text or ""
            else:
                # Fallback: construct a structured response without external LLMs
                current_date_string = datetime.now().strftime('%Y-%m-%d')
                content = json.dumps({
                    "title": "Generated SRS Document (Fallback)",
                    "version": "1.0",
                    "date": current_date_string,
                    "author": "BA Copilot AI",
                    "project_overview": user_input,
                    "functional_requirements": ["Requirement derived from input"],
                    "non_functional_requirements": ["Performance and security requirements TBD"],
                    "system_architecture": "Architecture TBD",
                    "user_stories": ["As a user, I can ..."],
                    "constraints": ["Constraints TBD"],
                    "assumptions": ["Assumptions TBD"],
                    "glossary": {"SRS": "Software Requirements Specification"}
                })
            
            logger.debug(f"LLM Response: {content[:200]}...")
            
            # Ensure content is not empty
            if not content.strip():
                raise ValueError("Empty response from LLM service")
            
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
                current_date_string = datetime.now().strftime('%Y-%m-%d')
                return {
                    "title": "Generated SRS Document (Fallback)",
                    "version": "1.0",
                    "date": current_date_string,
                    "author": "BA Copilot AI",
                    "project_overview": user_input,
                    "functional_requirements": ["Requirements based on: " + user_input],
                    "non_functional_requirements": ["Performance and security requirements to be defined"],
                    "system_architecture": "Architecture to be defined based on requirements",
                    "user_stories": ["User story derived from: " + user_input],
                    "constraints": ["Technical constraints to be identified"],
                    "assumptions": ["Assumptions to be validated"],
                    "glossary": {"SRS": "Software Requirements Specification"},
                    "raw_response": content
                }
                
        except Exception as e:
            # On any unexpected error, return fallback instead of 500
            logger.error(f"Error generating SRS document: {str(e)}")
            current_date_string = datetime.now().strftime('%Y-%m-%d')
            return {
                "title": "Generated SRS Document (Fallback)",
                "version": "1.0",
                "date": current_date_string,
                "author": "BA Copilot AI",
                "project_overview": user_input,
                "functional_requirements": ["Requirements based on: " + user_input],
                "non_functional_requirements": ["Performance and security requirements to be defined"],
                "system_architecture": "Architecture to be defined based on requirements",
                "user_stories": ["User story derived from: " + user_input],
                "constraints": ["Technical constraints to be identified"],
                "assumptions": ["Assumptions to be validated"],
                "glossary": {"SRS": "Software Requirements Specification"}
            }
    
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
            
            # Generate response based on provider
            if self.provider in ("openai", "openrouter"):
                extra_headers = None
                if self.provider == "openrouter":
                    extra_headers = {}
                    if settings.openrouter_referer:
                        extra_headers["HTTP-Referer"] = settings.openrouter_referer
                    if settings.openrouter_title:
                        extra_headers["X-Title"] = settings.openrouter_title

                model_id = (
                    "deepseek/deepseek-chat-v3.1:free" if self.provider == "openrouter" else ""
                )

                response = await self.client.chat.completions.create(
                    model=model_id,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    extra_headers=extra_headers
                )
                return response.choices[0].message.content or ""
            elif self.provider == "google":  # Google Gemini
                response = self.model.generate_content(prompt)
                return response.text or ""
            else:
                return prompt  # simple echo fallback for content API
            
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            return prompt


# Global instance - initialized lazily
_llm_service_instance: Optional[LLMService] = None

def get_llm_service() -> LLMService:
    """Get or create the global LLM service instance."""
    global _llm_service_instance
    if _llm_service_instance is None:
        _llm_service_instance = LLMService()
    return _llm_service_instance

# Backwards compatibility
llm_service = get_llm_service()