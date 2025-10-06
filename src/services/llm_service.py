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
        self.provider: Optional[str] = None
        self.model = None
        self.client = None
        
    def _try_init_provider(self, name: str) -> bool:
        """Attempt to initialize a given provider. Returns True on success."""
        try:
            if name == "google" and settings.google_ai_api_key:
                try:
                    import google.generativeai as genai
                except ImportError as e:
                    logger.warning(f"Failed to import google.generativeai: {e}")
                    return False
                try:
                    genai.configure(api_key=settings.google_ai_api_key)
                    # Keep gemini-pro by default; if model changes are needed, adjust here
                    self.model = genai.GenerativeModel('gemini-pro')
                    self.client = None
                    self.provider = "google"
                    logger.info("LLM Service initialized with Google Gemini")
                    return True
                except Exception as e:
                    logger.warning(f"Failed to initialize Google Gemini: {e}")
                    return False
            elif name == "openai" and settings.openai_api_key:
                try:
                    from openai import AsyncOpenAI
                    self.client = AsyncOpenAI(api_key=settings.openai_api_key)
                    self.model = None
                    self.provider = "openai"
                    logger.info("LLM Service initialized with OpenAI")
                    return True
                except ImportError as e:
                    logger.warning(f"OpenAI package not available: {e}")
                    return False
                except Exception as e:
                    logger.warning(f"Failed to initialize OpenAI: {e}")
                    return False
            elif name == "openrouter" and settings.openrouter_api_key:
                try:
                    from openai import AsyncOpenAI
                    self.client = AsyncOpenAI(
                        api_key=settings.openrouter_api_key,
                        base_url="https://openrouter.ai/api/v1",
                    )
                    self.model = None
                    self.provider = "openrouter"
                    logger.info("LLM Service initialized with OpenRouter via OpenAI SDK")
                    return True
                except ImportError as e:
                    logger.warning(f"OpenAI package not available for OpenRouter: {e}")
                    return False
                except Exception as e:
                    logger.warning(f"Failed to initialize OpenRouter: {e}")
                    return False
        except Exception as e:
            logger.warning(f"Unexpected error while initializing provider {name}: {e}")
        return False

    def _ensure_initialized(self):
        """Ensure the LLM service is initialized with the first available provider."""
        if not self._initialized:
            # Default priority: google -> openai -> openrouter
            for candidate in ("google", "openai", "openrouter"):
                if self._try_init_provider(candidate):
                    self._initialized = True
                    break
            if not self._initialized:
                raise ValueError(
                    "Either OPENAI_API_KEY or GOOGLE_AI_API_KEY or OPENROUTER_API_KEY must be set in environment variables"
                )

    def _provider_cycle(self):
        """Return providers in fallback order starting from current provider."""
        order = ["google", "openai", "openrouter"]
        if self.provider in order:
            start = order.index(self.provider)
            return order[start:] + order[:start]
        return order
    
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
            
            # Try providers in fallback order until one succeeds
            last_error: Optional[Exception] = None
            content: str = ""
            for provider_name in self._provider_cycle():
                if self.provider != provider_name:
                    # attempt switching provider
                    if not self._try_init_provider(provider_name):
                        continue
                logger.info(f"Generating SRS document using {self.provider} for input: {user_input[:100]}...")
                try:
                    if self.provider in ("openai", "openrouter"):
                        extra_headers = None
                        if self.provider == "openrouter":
                            extra_headers = {}
                            if settings.openrouter_referer:
                                extra_headers["HTTP-Referer"] = settings.openrouter_referer
                            if settings.openrouter_title:
                                extra_headers["X-Title"] = settings.openrouter_title

                        response = await self.client.chat.completions.create(
                            model=(
                                "openai/gpt-4o" if self.provider == "openrouter" else "gpt-3.5-turbo"
                            ),
                            messages=[
                                {"role": "system", "content": "You are a professional Business Analyst. Return only valid JSON."},
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0.7,
                            max_tokens=4000,
                            extra_headers=extra_headers
                        )
                        content = response.choices[0].message.content or ""
                    else:
                        response = self.model.generate_content(prompt)
                        content = response.text or ""
                    # If we reach here without exception, break out with content
                    break
                except Exception as prov_err:
                    last_error = prov_err
                    logger.warning(f"Provider {self.provider} failed to generate content: {prov_err}")
                    # continue to next provider
                    continue

            if not content:
                raise Exception(str(last_error) if last_error else "Unknown LLM error")
            
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
            
            # Try providers in fallback order until one succeeds
            last_error: Optional[Exception] = None
            for provider_name in self._provider_cycle():
                if self.provider != provider_name:
                    if not self._try_init_provider(provider_name):
                        continue
                try:
                    if self.provider in ("openai", "openrouter"):
                        extra_headers = None
                        if self.provider == "openrouter":
                            extra_headers = {}
                            if settings.openrouter_referer:
                                extra_headers["HTTP-Referer"] = settings.openrouter_referer
                            if settings.openrouter_title:
                                extra_headers["X-Title"] = settings.openrouter_title

                        response = await self.client.chat.completions.create(
                            model=(
                                "openai/gpt-4o" if self.provider == "openrouter" else "gpt-3.5-turbo"
                            ),
                            messages=[{"role": "user", "content": prompt}],
                            temperature=temperature,
                            extra_headers=extra_headers
                        )
                        return response.choices[0].message.content or ""
                    else:
                        response = self.model.generate_content(prompt)
                        return response.text or ""
                except Exception as prov_err:
                    last_error = prov_err
                    logger.warning(f"Provider {self.provider} failed to generate content: {prov_err}")
                    continue
            raise Exception(str(last_error) if last_error else "Unknown LLM error")
            
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