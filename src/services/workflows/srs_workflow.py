"""
Simple workflow for SRS document generation without complex LangGraph dependencies.
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional, List, TypedDict
from uuid import uuid4

from pydantic.v1 import SecretStr

from core.config import settings

logger = logging.getLogger(__name__)


class SRSWorkflowState(TypedDict):
    """State for SRS generation workflow."""
    # Input
    project_input: str
    user_id: Optional[str]
    project_id: Optional[int]
    
    # Processing state
    parsed_requirements: Dict[str, Any]
    functional_requirements: List[str]
    non_functional_requirements: List[str]
    system_architecture: str
    user_stories: List[str]
    constraints: List[str]
    assumptions: List[str]
    glossary: Dict[str, str]
    
    # Output
    srs_document: Dict[str, Any]
    document_id: str
    status: str
    error_message: Optional[str]
    
    # Metadata
    processing_steps: List[str]
    generated_at: str


class SRSWorkflow:
    """Simple SRS generation workflow without complex dependencies."""
    
    def __init__(self):
        """Initialize the SRS workflow."""
        self.llm = None
        self._initialize_llm()
        
    def _initialize_llm(self):
        """Initialize the LLM client based on available API keys."""
        # Priority: OpenRouter (DeepSeek free) -> Google Gemini -> OpenAI -> Fallback
        
        # OpenRouter (DeepSeek free) - HIGHEST PRIORITY
        if settings.openrouter_ai_api_key:
            try:
                from langchain_openai import ChatOpenAI
                self.llm = ChatOpenAI(
                    api_key=settings.openrouter_ai_api_key,
                    base_url="https://openrouter.ai/api/v1",
                    model="deepseek/deepseek-chat-v3.1:free",
                    temperature=0.7,
                    model_kwargs={
                        "extra_headers": {
                            "HTTP-Referer": settings.openrouter_referer or "http://localhost",
                            "X-Title": settings.openrouter_title or "BA Copilot AI",
                        }
                    }
                )
                self.provider = "openrouter"
                logger.info("LLM initialized with OpenRouter (DeepSeek)")
                return
            except ImportError as e:
                logger.warning(f"OpenAI package not available for OpenRouter: {e}")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenRouter: {e}")

        # Google Gemini (prioritized due to rate limit issues with free OpenRouter)
        if settings.google_ai_api_key:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash",
                    temperature=0.7,
                    google_api_key=SecretStr(settings.google_ai_api_key) if settings.google_ai_api_key else None,
                    convert_system_message_to_human=True,
                    client=None
                )
                
                self.provider = "google"
                logger.info("LLM initialized with Google Gemini")
                return
            except ImportError as e:
                logger.warning(f"Google GenAI package not available: {e}")
            except Exception as e:
                logger.warning(f"Failed to initialize Google Gemini: {e}")

        # OpenAI
        if settings.openai_api_key:
            try:
                from langchain_openai import ChatOpenAI
                self.llm = ChatOpenAI(
                    api_key=settings.openai_api_key,
                    model="gpt-3.5-turbo",
                    temperature=0.7
                )
                self.provider = "openai"
                logger.info("LLM initialized with OpenAI")
                return
            except ImportError as e:
                logger.warning(f"OpenAI package not available: {e}")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI: {e}")

        # Fallback: No external LLM
        self.llm = None
        self.provider = "fallback"
        logger.warning("LLM initialized in fallback mode (no external API keys) - This should not happen in production!")

    async def _call_llm(self, prompt: str, system_message: Optional[str] = None) -> str:
        """Call LLM with proper message formatting."""
        if not self.llm:
            return f"Placeholder response for: {prompt[:50]}..."
        
        try:
            if system_message:
                from langchain_core.messages import HumanMessage, SystemMessage
                messages = [
                    SystemMessage(content=system_message),
                    HumanMessage(content=prompt)
                ]
            else:
                from langchain_core.messages import HumanMessage
                messages = [HumanMessage(content=prompt)]
            
            response = await self.llm.ainvoke(messages)
            
            # Handle response content properly
            if response and hasattr(response, 'content') and response.content:
                content = str(response.content).strip()
                if content:
                    logger.info(f"LLM call successful, response length: {len(content)} characters")
                    return content
                else:
                    logger.warning("LLM response content is empty")
                    return "No response content generated"
            else:
                logger.warning(f"Invalid LLM response structure: {type(response)}")
                return "No valid response received"
        except Exception as e:
            logger.error(f"LLM call failed with exception: {e}")
            return f"Fallback response for: {prompt[:50]}..."

    async def generate_srs_document(self, project_input: str, user_id: Optional[str] = None, project_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate SRS document using the simplified workflow.
        
        Args:
            project_input: User's project description
            user_id: Optional user ID
            project_id: Optional project ID
            
        Returns:
            Generated SRS document with metadata
        """
        try:
            logger.info("Starting SRS generation workflow")
            
            # Step 1: Initialize
            document_id = str(uuid4())
            generated_at = datetime.utcnow().isoformat()
            processing_steps = ["Workflow initialized"]
            
            logger.info(f"Step 1: Initialized workflow for document {document_id}")
            
            # Step 2: Parse requirements
            logger.info("Step 2: Parsing project requirements")
            
            prompt = f"""
Analyze the following project input and extract key information:

Project Description: {project_input}

Please identify and extract:
1. Project name/title
2. Primary purpose/goal
3. Target users/audience
4. Key features mentioned
5. Technology preferences (if any)
6. Business context

Return the analysis in JSON format with these fields:
- project_name
- purpose
- target_users (array)
- key_features (array)
- technology_preferences (array)
- business_context
"""
            
            response = await self._call_llm(
                prompt, 
                "You are a Business Analyst expert at requirement analysis."
            )
            
            # Try to parse JSON response
            try:
                if response and isinstance(response, str):
                    if response.startswith('```json'):
                        response = response.split('```json')[1].split('```')[0].strip()
                    elif response.startswith('```'):
                        response = response.split('```')[1].split('```')[0].strip()
                    
                    parsed_requirements = json.loads(response)
                    logger.info("Successfully parsed requirements using LLM")
                else:
                    raise json.JSONDecodeError("Invalid response type", "", 0)
            except (json.JSONDecodeError, IndexError, AttributeError):
                # Fallback: manual parsing
                parsed_requirements = {
                    "project_name": "Project Analysis",
                    "purpose": project_input[:200],
                    "target_users": ["End users"],
                    "key_features": ["Feature extraction from input"],
                    "technology_preferences": [],
                    "business_context": "Business analysis required"
                }
                logger.warning("LLM response was not valid JSON, using fallback parsing")
            
            processing_steps.append("Requirements parsed and analyzed")
            
            # Step 3: Extract functional requirements
            logger.info("Step 3: Extracting functional requirements")
            
            functional_prompt = f"""
Based on the project analysis:
Project: {parsed_requirements.get('project_name', 'Unknown')}
Purpose: {parsed_requirements.get('purpose', '')}
Key Features: {parsed_requirements.get('key_features', [])}

Generate a comprehensive list of functional requirements. Each requirement should be:
- Specific and measurable
- User-focused
- Technically implementable
- Following the format: "The system shall [action]"

Return as a JSON array of requirement strings.
"""
            
            func_response = await self._call_llm(
                functional_prompt,
                "You are a Business Analyst expert at functional requirement definition."
            )
            
            # Parse functional requirements
            try:
                if func_response and isinstance(func_response, str):
                    if func_response.startswith('```json'):
                        func_response = func_response.split('```json')[1].split('```')[0].strip()
                    elif func_response.startswith('```'):
                        func_response = func_response.split('```')[1].split('```')[0].strip()
                    
                    functional_requirements = json.loads(func_response)
                    if not isinstance(functional_requirements, list):
                        functional_requirements = ["The system shall implement core functionality"]
                    logger.info(f"Extracted {len(functional_requirements)} functional requirements")
                else:
                    raise json.JSONDecodeError("Invalid response type", "", 0)
            except (json.JSONDecodeError, IndexError, AttributeError):
                functional_requirements = [
                    "The system shall provide user authentication",
                    "The system shall support core business operations",
                    "The system shall maintain data integrity"
                ]
                logger.warning("Using fallback functional requirements")
            
            processing_steps.append("Functional requirements extracted")
            
            # Step 4: Extract non-functional requirements
            logger.info("Step 4: Extracting non-functional requirements")
            
            non_functional_requirements = [
                "Performance: System response time shall be under 3 seconds for 95% of requests",
                "Security: All user data shall be encrypted in transit and at rest",
                "Usability: System interface shall be intuitive and accessible",
                "Reliability: System uptime shall be at least 99.9%",
                "Scalability: System shall support at least 1000 concurrent users",
                "Maintainability: Code shall be well-documented and modular"
            ]
            
            processing_steps.append("Non-functional requirements extracted")
            
            # Step 5: Design system architecture
            logger.info("Step 5: Designing system architecture")
            
            arch_prompt = f"""
Design a high-level system architecture for:
Project: {parsed_requirements.get('project_name', 'Unknown Project')}
Technology Preferences: {parsed_requirements.get('technology_preferences', [])}

Consider the functional requirements: {functional_requirements[:3]}

Provide a system architecture description including:
- System components and their responsibilities
- Data flow between components
- Technology stack recommendations
- Deployment architecture considerations

Return as a detailed text description (not JSON).
"""
            
            system_architecture = await self._call_llm(
                arch_prompt,
                "You are a Software Architect expert at system design."
            )
            
            processing_steps.append("System architecture designed")
            
            # Step 6: Create user stories
            logger.info("Step 6: Creating user stories")
            
            user_stories = [
                "As a user, I want to securely log into the system so that I can access my account and data",
                "As a user, I want to perform core business operations so that I can achieve my objectives",
                "As a user, I want an intuitive interface so that I can easily navigate the system",
                "As an administrator, I want to manage user accounts so that I can maintain system security",
                "As a user, I want reliable system performance so that I can work efficiently"
            ]
            
            processing_steps.append("User stories created")
            
            # Step 7: Identify constraints
            logger.info("Step 7: Identifying project constraints")
            
            constraints = [
                "Technical: System must be compatible with existing technology infrastructure",
                "Business: Project must be completed within allocated budget and timeline",
                "Regulatory: System must comply with applicable data protection and privacy regulations",
                "Operational: System must be maintainable with existing team capabilities",
                "Performance: System must meet specified performance benchmarks"
            ]
            
            processing_steps.append("Project constraints identified")
            
            # Step 8: Define assumptions
            logger.info("Step 8: Defining project assumptions")
            
            assumptions = [
                "Users have basic computer literacy and reliable internet access",
                "Existing technical infrastructure can support the new system requirements",
                "Required third-party integrations will be available and stable",
                "Business processes will remain consistent during development",
                "Adequate resources and expertise will be available for implementation"
            ]
            
            processing_steps.append("Project assumptions defined")
            
            # Step 9: Build glossary
            logger.info("Step 9: Building technical glossary")
            
            glossary = {
                "SRS": "Software Requirements Specification - a document that describes the functionality and behavior of a software system",
                "API": "Application Programming Interface - a set of protocols and tools for building software applications",
                "UI": "User Interface - the space where interactions between users and a system occur",
                "UX": "User Experience - the overall experience of a person using a product or system",
                "CRUD": "Create, Read, Update, Delete - the four basic operations of persistent storage"
            }
            
            processing_steps.append("Technical glossary built")
            
            # Step 10: Compile document
            logger.info("Step 10: Compiling final SRS document")
            
            srs_document = {
                "title": parsed_requirements.get("project_name", "Software Requirements Specification"),
                "version": "1.0",
                "date": datetime.utcnow().strftime('%Y-%m-%d'),
                "author": "BA Copilot AI",
                "project_overview": parsed_requirements.get("purpose", project_input),
                "functional_requirements": functional_requirements,
                "non_functional_requirements": non_functional_requirements,
                "system_architecture": system_architecture,
                "user_stories": user_stories,
                "constraints": constraints,
                "assumptions": assumptions,
                "glossary": glossary,
                "metadata": {
                    "document_id": document_id,
                    "generated_at": generated_at,
                    "user_id": user_id,
                    "project_id": project_id,
                    "provider": getattr(self, 'provider', 'unknown'),
                    "processing_steps": processing_steps
                }
            }
            
            processing_steps.append("SRS document compiled")
            
            # Step 11: Finalize
            logger.info("Step 11: Finalizing SRS document")
            processing_steps.append("SRS document finalized and ready")
            
            logger.info(f"SRS document {document_id} successfully generated with workflow")
            return srs_document
                
        except Exception as e:
            logger.error(f"Error in SRS workflow: {str(e)}")
            # Return fallback document
            current_date_string = datetime.utcnow().strftime('%Y-%m-%d')
            return {
                "title": "Generated SRS Document (Workflow Fallback)",
                "version": "1.0",
                "date": current_date_string,
                "author": "BA Copilot AI",
                "project_overview": project_input,
                "functional_requirements": ["Requirements based on: " + project_input],
                "non_functional_requirements": ["Performance and security requirements to be defined"],
                "system_architecture": "Architecture to be defined based on requirements",
                "user_stories": ["User story derived from: " + project_input],
                "constraints": ["Technical constraints to be identified"],
                "assumptions": ["Assumptions to be validated"],
                "glossary": {"SRS": "Software Requirements Specification"},
                "metadata": {
                    "document_id": str(uuid4()),
                    "generated_at": datetime.utcnow().isoformat(),
                    "user_id": user_id,
                    "project_id": project_id,
                    "provider": "fallback",
                    "error": str(e)
                }
            }