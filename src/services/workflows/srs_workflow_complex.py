"""
LangGraph workflow for SRS document generation using a multi-step approach.
NOT COMPLETE, DO NOT USE
"""

# import logging
# import json
# from datetime import datetime
# from typing import Dict, Any, Optional, List, TypedDict
# from uuid import uuid4

# from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
# from langchain_core.runnables import RunnableConfig
# from langgraph.graph import StateGraph
# from langgraph.graph.state import CompiledStateGraph

# from core.config import settings

# logger = logging.getLogger(__name__)


# class SRSWorkflowState(TypedDict):
#     """State for SRS generation workflow."""
#     # Input
#     project_input: str
#     user_id: Optional[str]
#     project_id: Optional[int]
    
#     # Processing state
#     parsed_requirements: Dict[str, Any]
#     functional_requirements: List[str]
#     non_functional_requirements: List[str]
#     system_architecture: str
#     user_stories: List[str]
#     constraints: List[str]
#     assumptions: List[str]
#     glossary: Dict[str, str]
    
#     # Output
#     srs_document: Dict[str, Any]
#     document_id: str
#     status: str
#     error_message: Optional[str]
    
#     # Metadata
#     processing_steps: List[str]
#     generated_at: str


# class SRSWorkflow:
#     """LangGraph workflow for comprehensive SRS document generation."""
    
#     def __init__(self):
#         """Initialize the SRS workflow."""
#         self.llm = None
#         self.graph: Optional[CompiledStateGraph] = None
#         self._initialize_llm()
#         self._build_graph()
        
#     def _initialize_llm(self):
#         """Initialize the LLM client based on available API keys."""
#         # Priority: OpenRouter (DeepSeek free) -> Google Gemini -> OpenAI -> Fallback
#         if settings.openrouter_ai_api_key:
#             try:
#                 from langchain_openai import ChatOpenAI
#                 self.llm = ChatOpenAI(
#                     api_key=settings.openrouter_ai_api_key,
#                     base_url="https://openrouter.ai/api/v1",
#                     model="deepseek/deepseek-chat-v3.1:free",
#                     temperature=0.7,
#                     model_kwargs={
#                         "extra_headers": {
#                             "HTTP-Referer": settings.openrouter_referer or "http://localhost",
#                             "X-Title": settings.openrouter_title or "BA Copilot AI",
#                         }
#                     }
#                 )
#                 self.provider = "openrouter"
#                 logger.info("LLM initialized with OpenRouter (DeepSeek)")
#                 return
#             except ImportError as e:
#                 logger.warning(f"OpenAI package not available for OpenRouter: {e}")
#             except Exception as e:
#                 logger.warning(f"Failed to initialize OpenRouter: {e}")

#         # Google Gemini
#         if settings.google_ai_api_key:
#             try:
#                 from langchain_google_genai import ChatGoogleGenerativeAI
#                 self.llm = ChatGoogleGenerativeAI(
#                     model="gemini-1.5-flash",
#                     google_api_key=settings.google_ai_api_key,
#                     temperature=0.7
#                 )
#                 self.provider = "google"
#                 logger.info("LLM initialized with Google Gemini")
#                 return
#             except ImportError as e:
#                 logger.warning(f"Google GenAI package not available: {e}")
#             except Exception as e:
#                 logger.warning(f"Failed to initialize Google Gemini: {e}")

#         # OpenAI
#         if settings.openai_api_key:
#             try:
#                 from langchain_openai import ChatOpenAI
#                 self.llm = ChatOpenAI(
#                     api_key=settings.openai_api_key,
#                     model="gpt-3.5-turbo",
#                     temperature=0.7
#                 )
#                 self.provider = "openai"
#                 logger.info("LLM initialized with OpenAI")
#                 return
#             except ImportError as e:
#                 logger.warning(f"OpenAI package not available: {e}")
#             except Exception as e:
#                 logger.warning(f"Failed to initialize OpenAI: {e}")

#         # Fallback: No external LLM
#         self.llm = None
#         self.provider = "fallback"
#         logger.info("LLM initialized in fallback mode (no external API keys)")

#     def _build_graph(self):
#         """Build the LangGraph workflow graph."""
#         workflow = StateGraph(SRSWorkflowState)
        
#         # Add nodes
#         workflow.add_node("initialize", self._initialize_state)
#         workflow.add_node("parse_requirements", self._parse_requirements)
#         workflow.add_node("extract_functional_requirements", self._extract_functional_requirements)
#         workflow.add_node("extract_non_functional_requirements", self._extract_non_functional_requirements)
#         workflow.add_node("design_system_architecture", self._design_system_architecture)
#         workflow.add_node("create_user_stories", self._create_user_stories)
#         workflow.add_node("identify_constraints", self._identify_constraints)
#         workflow.add_node("define_assumptions", self._define_assumptions)
#         workflow.add_node("build_glossary", self._build_glossary)
#         workflow.add_node("compile_document", self._compile_document)
#         workflow.add_node("finalize", self._finalize_document)
        
#         # Add edges
#         workflow.set_entry_point("initialize")
#         workflow.add_edge("initialize", "parse_requirements")
#         workflow.add_edge("parse_requirements", "extract_functional_requirements")
#         workflow.add_edge("extract_functional_requirements", "extract_non_functional_requirements")
#         workflow.add_edge("extract_non_functional_requirements", "design_system_architecture")
#         workflow.add_edge("design_system_architecture", "create_user_stories")
#         workflow.add_edge("create_user_stories", "identify_constraints")
#         workflow.add_edge("identify_constraints", "define_assumptions")
#         workflow.add_edge("define_assumptions", "build_glossary")
#         workflow.add_edge("build_glossary", "compile_document")
#         workflow.add_edge("compile_document", "finalize")
#         workflow.set_finish_point("finalize")
        
#         # Compile the graph
#         self.graph = workflow.compile()
#         logger.info("SRS workflow graph compiled successfully")
    
#     async def _initialize_state(self, state: SRSWorkflowState, config: RunnableConfig) -> SRSWorkflowState:
#         """Initialize the workflow state."""
#         logger.info("Step 1: Initializing SRS generation workflow")
        
#         state["document_id"] = str(uuid4())
#         state["generated_at"] = datetime.utcnow().isoformat()
#         state["status"] = "processing"
#         state["processing_steps"] = ["Workflow initialized"]
#         state["error_message"] = None
        
#         # Initialize empty collections
#         state["parsed_requirements"] = {}
#         state["functional_requirements"] = []
#         state["non_functional_requirements"] = []
#         state["system_architecture"] = ""
#         state["user_stories"] = []
#         state["constraints"] = []
#         state["assumptions"] = []
#         state["glossary"] = {}
#         state["srs_document"] = {}
        
#         logger.info(f"Initialized workflow for document {state['document_id']}")
#         return state
    
#     async def _parse_requirements(self, state: SRSWorkflowState, config: RunnableConfig) -> SRSWorkflowState:
#         """Parse and understand the input requirements."""
#         logger.info("Step 2: Parsing project requirements")
        
#         if self.llm:
#             try:
#                 prompt = f"""
# Analyze the following project input and extract key information:

# Project Description: {state['project_input']}

# Please identify and extract:
# 1. Project name/title
# 2. Primary purpose/goal
# 3. Target users/audience
# 4. Key features mentioned
# 5. Technology preferences (if any)
# 6. Business context

# Return the analysis in JSON format with these fields:
# - project_name
# - purpose
# - target_users
# - key_features (array)
# - technology_preferences (array)
# - business_context
# """
                
#                 messages = [
#                     SystemMessage(content="You are a Business Analyst expert at requirement analysis."),
#                     HumanMessage(content=prompt)
#                 ]
                
#                 response = await self.llm.ainvoke(messages)
#                 content = response.content
                
#                 # Try to parse JSON response
#                 try:
#                     if content.startswith('```json'):
#                         content = content.split('```json')[1].split('```')[0].strip()
#                     elif content.startswith('```'):
#                         content = content.split('```')[1].split('```')[0].strip()
                    
#                     parsed_data = json.loads(content)
#                     state["parsed_requirements"] = parsed_data
#                     logger.info("Successfully parsed requirements using LLM")
#                 except json.JSONDecodeError:
#                     # Fallback: manual parsing
#                     state["parsed_requirements"] = {
#                         "project_name": "Project Analysis",
#                         "purpose": state['project_input'][:200],
#                         "target_users": ["End users"],
#                         "key_features": ["Feature extraction from input"],
#                         "technology_preferences": [],
#                         "business_context": "Business analysis required"
#                     }
#                     logger.warning("LLM response was not valid JSON, using fallback parsing")
                    
#             except Exception as e:
#                 logger.error(f"Error in LLM parsing: {e}")
#                 # Fallback parsing
#                 state["parsed_requirements"] = {
#                     "project_name": "Project Analysis",
#                     "purpose": state['project_input'][:200],
#                     "target_users": ["End users"],
#                     "key_features": ["Feature extraction required"],
#                     "technology_preferences": [],
#                     "business_context": "Business analysis required"
#                 }
#         else:
#             # Fallback: basic text analysis without LLM
#             logger.info("Using fallback parsing (no LLM available)")
#             state["parsed_requirements"] = {
#                 "project_name": "Generated Project",
#                 "purpose": state['project_input'],
#                 "target_users": ["End users"],
#                 "key_features": ["Features to be defined"],
#                 "technology_preferences": ["Technology stack TBD"],
#                 "business_context": "Business context analysis needed"
#             }
        
#         state["processing_steps"].append("Requirements parsed and analyzed")
#         return state
    
#     async def _extract_functional_requirements(self, state: SRSWorkflowState, config: RunnableConfig) -> SRSWorkflowState:
#         """Extract functional requirements from parsed input."""
#         logger.info("Step 3: Extracting functional requirements")
        
#         if self.llm:
#             try:
#                 parsed_req = state["parsed_requirements"]
#                 prompt = f"""
# Based on the project analysis:
# Project: {parsed_req.get('project_name', 'Unknown')}
# Purpose: {parsed_req.get('purpose', '')}
# Key Features: {parsed_req.get('key_features', [])}

# Generate a comprehensive list of functional requirements. Each requirement should be:
# - Specific and measurable
# - User-focused
# - Technically implementable
# - Following the format: "The system shall [action]"

# Return as a JSON array of requirement strings.
# """
                
#                 messages = [
#                     SystemMessage(content="You are a Business Analyst expert at functional requirement definition."),
#                     HumanMessage(content=prompt)
#                 ]
                
#                 response = await self.llm.ainvoke(messages)
#                 content = response.content
                
#                 # Parse JSON response
#                 try:
#                     if content.startswith('```json'):
#                         content = content.split('```json')[1].split('```')[0].strip()
#                     elif content.startswith('```'):
#                         content = content.split('```')[1].split('```')[0].strip()
                    
#                     requirements = json.loads(content)
#                     if isinstance(requirements, list):
#                         state["functional_requirements"] = requirements
#                     else:
#                         state["functional_requirements"] = ["The system shall implement core functionality"]
#                     logger.info(f"Extracted {len(state['functional_requirements'])} functional requirements")
#                 except json.JSONDecodeError:
#                     state["functional_requirements"] = [
#                         "The system shall provide user authentication",
#                         "The system shall support core business operations",
#                         "The system shall maintain data integrity"
#                     ]
#                     logger.warning("Using fallback functional requirements")
                    
#             except Exception as e:
#                 logger.error(f"Error extracting functional requirements: {e}")
#                 state["functional_requirements"] = [
#                     "The system shall provide user authentication",
#                     "The system shall support core business operations",
#                     "The system shall maintain data integrity"
#                 ]
#         else:
#             # Fallback without LLM
#             logger.info("Extracting functional requirements (fallback mode)")
#             state["functional_requirements"] = [
#                 "The system shall provide user authentication and authorization",
#                 "The system shall support core business operations",
#                 "The system shall maintain data integrity and consistency",
#                 "The system shall provide a user-friendly interface",
#                 "The system shall support data input and output operations"
#             ]
        
#         state["processing_steps"].append("Functional requirements extracted")
#         return state
    
#     async def _extract_non_functional_requirements(self, state: SRSWorkflowState, config: RunnableConfig) -> SRSWorkflowState:
#         """Extract non-functional requirements."""
#         logger.info("Step 4: Extracting non-functional requirements")
        
#         if self.llm:
#             try:
#                 prompt = f"""
# Based on the project analysis for: {state['parsed_requirements'].get('project_name', 'Unknown Project')}

# Generate non-functional requirements covering:
# - Performance (response time, throughput)
# - Security (authentication, authorization, data protection)
# - Usability (ease of use, accessibility)
# - Reliability (uptime, error handling)
# - Scalability (user load, data volume)
# - Maintainability (code quality, documentation)

# Return as a JSON array of requirement strings, each starting with a category like "Performance:", "Security:", etc.
# """
                
#                 messages = [
#                     SystemMessage(content="You are a Business Analyst expert at non-functional requirement definition."),
#                     HumanMessage(content=prompt)
#                 ]
                
#                 response = await self.llm.ainvoke(messages)
#                 content = response.content
                
#                 try:
#                     if content.startswith('```json'):
#                         content = content.split('```json')[1].split('```')[0].strip()
#                     elif content.startswith('```'):
#                         content = content.split('```')[1].split('```')[0].strip()
                    
#                     requirements = json.loads(content)
#                     if isinstance(requirements, list):
#                         state["non_functional_requirements"] = requirements
#                     else:
#                         state["non_functional_requirements"] = ["Performance: Response time shall be under 3 seconds"]
#                     logger.info(f"Extracted {len(state['non_functional_requirements'])} non-functional requirements")
#                 except json.JSONDecodeError:
#                     state["non_functional_requirements"] = [
#                         "Performance: System response time shall be under 3 seconds",
#                         "Security: All data shall be encrypted in transit and at rest",
#                         "Usability: Interface shall be intuitive for end users"
#                     ]
                    
#             except Exception as e:
#                 logger.error(f"Error extracting non-functional requirements: {e}")
#                 state["non_functional_requirements"] = [
#                     "Performance: System response time shall be under 3 seconds",
#                     "Security: All data shall be encrypted in transit and at rest",
#                     "Usability: Interface shall be intuitive for end users"
#                 ]
#         else:
#             # Fallback without LLM
#             logger.info("Extracting non-functional requirements (fallback mode)")
#             state["non_functional_requirements"] = [
#                 "Performance: System response time shall be under 3 seconds for 95% of requests",
#                 "Security: All user data shall be encrypted in transit and at rest",
#                 "Usability: System interface shall be intuitive and accessible",
#                 "Reliability: System uptime shall be at least 99.9%",
#                 "Scalability: System shall support at least 1000 concurrent users",
#                 "Maintainability: Code shall be well-documented and modular"
#             ]
        
#         state["processing_steps"].append("Non-functional requirements extracted")
#         return state
    
#     async def _design_system_architecture(self, state: SRSWorkflowState, config: RunnableConfig) -> SRSWorkflowState:
#         """Design high-level system architecture."""
#         logger.info("Step 5: Designing system architecture")
        
#         if self.llm:
#             try:
#                 prompt = f"""
# Design a high-level system architecture for:
# Project: {state['parsed_requirements'].get('project_name', 'Unknown Project')}
# Technology Preferences: {state['parsed_requirements'].get('technology_preferences', [])}

# Consider the functional requirements: {state['functional_requirements'][:3]}

# Provide a system architecture description including:
# - System components and their responsibilities
# - Data flow between components
# - Technology stack recommendations
# - Deployment architecture considerations

# Return as a detailed text description (not JSON).
# """
                
#                 messages = [
#                     SystemMessage(content="You are a Software Architect expert at system design."),
#                     HumanMessage(content=prompt)
#                 ]
                
#                 response = await self.llm.ainvoke(messages)
#                 state["system_architecture"] = response.content
#                 logger.info("Generated system architecture using LLM")
                
#             except Exception as e:
#                 logger.error(f"Error designing system architecture: {e}")
#                 state["system_architecture"] = """
# The system follows a modern three-tier architecture:

# 1. Presentation Layer: Web-based user interface
# 2. Application Layer: Business logic and API services
# 3. Data Layer: Database and storage systems

# Key Components:
# - Frontend: Responsive web application
# - Backend API: RESTful services
# - Database: Relational database for data persistence
# - Authentication: Secure user management system
# - Integration: APIs for external system connectivity

# The architecture supports scalability, maintainability, and security requirements.
# """.strip()
#         else:
#             # Fallback without LLM
#             logger.info("Designing system architecture (fallback mode)")
#             state["system_architecture"] = """
# The system follows a modern three-tier architecture:

# 1. Presentation Layer: Web-based user interface providing user interaction
# 2. Application Layer: Business logic, API services, and core functionality
# 3. Data Layer: Database and storage systems for data persistence

# Key Components:
# - Frontend: Responsive web application for user interaction
# - Backend API: RESTful services handling business logic
# - Database: Relational database for secure data storage
# - Authentication: User management and security system
# - Integration Layer: APIs for external system connectivity

# The architecture supports scalability, maintainability, and security requirements.
# """.strip()
        
#         state["processing_steps"].append("System architecture designed")
#         return state
    
#     async def _create_user_stories(self, state: SRSWorkflowState, config: RunnableConfig) -> SRSWorkflowState:
#         """Create user stories based on requirements."""
#         logger.info("Step 6: Creating user stories")
        
#         if self.llm:
#             try:
#                 prompt = f"""
# Create user stories for the project: {state['parsed_requirements'].get('project_name', 'Unknown Project')}
# Target Users: {state['parsed_requirements'].get('target_users', [])}
# Based on functional requirements: {state['functional_requirements'][:5]}

# Generate user stories in the format:
# "As a [user type], I want [goal] so that [benefit]"

# Include acceptance criteria for each story when possible.
# Return as a JSON array of user story strings.
# """
                
#                 messages = [
#                     SystemMessage(content="You are a Product Owner expert at writing user stories."),
#                     HumanMessage(content=prompt)
#                 ]
                
#                 response = await self.llm.ainvoke(messages)
#                 content = response.content
                
#                 try:
#                     if content.startswith('```json'):
#                         content = content.split('```json')[1].split('```')[0].strip()
#                     elif content.startswith('```'):
#                         content = content.split('```')[1].split('```')[0].strip()
                    
#                     stories = json.loads(content)
#                     if isinstance(stories, list):
#                         state["user_stories"] = stories
#                     else:
#                         state["user_stories"] = ["As a user, I want to access the system functionality"]
#                     logger.info(f"Created {len(state['user_stories'])} user stories")
#                 except json.JSONDecodeError:
#                     state["user_stories"] = [
#                         "As a user, I want to securely log into the system so that I can access my account",
#                         "As a user, I want to perform core operations so that I can achieve my goals",
#                         "As an administrator, I want to manage user accounts so that I can maintain system security"
#                     ]
                    
#             except Exception as e:
#                 logger.error(f"Error creating user stories: {e}")
#                 state["user_stories"] = [
#                     "As a user, I want to securely log into the system so that I can access my account",
#                     "As a user, I want to perform core operations so that I can achieve my goals",
#                     "As an administrator, I want to manage user accounts so that I can maintain system security"
#                 ]
#         else:
#             # Fallback without LLM
#             logger.info("Creating user stories (fallback mode)")
#             state["user_stories"] = [
#                 "As a user, I want to securely log into the system so that I can access my account and data",
#                 "As a user, I want to perform core business operations so that I can achieve my objectives",
#                 "As a user, I want an intuitive interface so that I can easily navigate the system",
#                 "As an administrator, I want to manage user accounts so that I can maintain system security",
#                 "As a user, I want reliable system performance so that I can work efficiently"
#             ]
        
#         state["processing_steps"].append("User stories created")
#         return state
    
#     async def _identify_constraints(self, state: SRSWorkflowState, config: RunnableConfig) -> SRSWorkflowState:
#         """Identify project constraints."""
#         logger.info("Step 7: Identifying project constraints")
        
#         if self.llm:
#             try:
#                 prompt = f"""
# Identify potential constraints for the project: {state['parsed_requirements'].get('project_name', 'Unknown Project')}
# Business Context: {state['parsed_requirements'].get('business_context', '')}

# Consider constraints in these categories:
# - Technical constraints (technology, integration, performance)
# - Business constraints (budget, timeline, resources)
# - Regulatory constraints (compliance, legal requirements)
# - Operational constraints (maintenance, support, deployment)

# Return as a JSON array of constraint strings, each prefixed with the category.
# """
                
#                 messages = [
#                     SystemMessage(content="You are a Project Manager expert at constraint identification."),
#                     HumanMessage(content=prompt)
#                 ]
                
#                 response = await self.llm.ainvoke(messages)
#                 content = response.content
                
#                 try:
#                     if content.startswith('```json'):
#                         content = content.split('```json')[1].split('```')[0].strip()
#                     elif content.startswith('```'):
#                         content = content.split('```')[1].split('```')[0].strip()
                    
#                     constraints = json.loads(content)
#                     if isinstance(constraints, list):
#                         state["constraints"] = constraints
#                     else:
#                         state["constraints"] = ["Technical: Technology stack must be modern and maintainable"]
#                     logger.info(f"Identified {len(state['constraints'])} constraints")
#                 except json.JSONDecodeError:
#                     state["constraints"] = [
#                         "Technical: System must be compatible with existing infrastructure",
#                         "Business: Project must be completed within budget constraints",
#                         "Regulatory: System must comply with data protection regulations"
#                     ]
                    
#             except Exception as e:
#                 logger.error(f"Error identifying constraints: {e}")
#                 state["constraints"] = [
#                     "Technical: System must be compatible with existing infrastructure",
#                     "Business: Project must be completed within budget and timeline constraints",
#                     "Regulatory: System must comply with applicable data protection regulations"
#                 ]
#         else:
#             # Fallback without LLM
#             logger.info("Identifying constraints (fallback mode)")
#             state["constraints"] = [
#                 "Technical: System must be compatible with existing technology infrastructure",
#                 "Business: Project must be completed within allocated budget and timeline",
#                 "Regulatory: System must comply with applicable data protection and privacy regulations",
#                 "Operational: System must be maintainable with existing team capabilities",
#                 "Performance: System must meet specified performance benchmarks"
#             ]
        
#         state["processing_steps"].append("Project constraints identified")
#         return state
    
#     async def _define_assumptions(self, state: SRSWorkflowState, config: RunnableConfig) -> SRSWorkflowState:
#         """Define project assumptions."""
#         logger.info("Step 8: Defining project assumptions")
        
#         if self.llm:
#             try:
#                 prompt = f"""
# Define key assumptions for the project: {state['parsed_requirements'].get('project_name', 'Unknown Project')}

# Consider assumptions about:
# - User behavior and capabilities
# - Technical environment and infrastructure
# - Business processes and requirements
# - External dependencies and integrations
# - Timeline and resource availability

# Return as a JSON array of assumption strings.
# """
                
#                 messages = [
#                     SystemMessage(content="You are a Business Analyst expert at assumption definition."),
#                     HumanMessage(content=prompt)
#                 ]
                
#                 response = await self.llm.ainvoke(messages)
#                 content = response.content
                
#                 try:
#                     if content.startswith('```json'):
#                         content = content.split('```json')[1].split('```')[0].strip()
#                     elif content.startswith('```'):
#                         content = content.split('```')[1].split('```')[0].strip()
                    
#                     assumptions = json.loads(content)
#                     if isinstance(assumptions, list):
#                         state["assumptions"] = assumptions
#                     else:
#                         state["assumptions"] = ["Users have basic computer literacy"]
#                     logger.info(f"Defined {len(state['assumptions'])} assumptions")
#                 except json.JSONDecodeError:
#                     state["assumptions"] = [
#                         "Users have basic computer literacy and internet access",
#                         "Existing infrastructure can support the new system",
#                         "Required integrations will be available and stable"
#                     ]
                    
#             except Exception as e:
#                 logger.error(f"Error defining assumptions: {e}")
#                 state["assumptions"] = [
#                     "Users have basic computer literacy and internet access",
#                     "Existing infrastructure can support the new system",
#                     "Required integrations will be available and stable"
#                 ]
#         else:
#             # Fallback without LLM
#             logger.info("Defining assumptions (fallback mode)")
#             state["assumptions"] = [
#                 "Users have basic computer literacy and reliable internet access",
#                 "Existing technical infrastructure can support the new system requirements",
#                 "Required third-party integrations will be available and stable",
#                 "Business processes will remain consistent during development",
#                 "Adequate resources and expertise will be available for implementation"
#             ]
        
#         state["processing_steps"].append("Project assumptions defined")
#         return state
    
#     async def _build_glossary(self, state: SRSWorkflowState, config: RunnableConfig) -> SRSWorkflowState:
#         """Build a glossary of technical terms."""
#         logger.info("Step 9: Building technical glossary")
        
#         if self.llm:
#             try:
#                 prompt = f"""
# Create a glossary of technical terms and business concepts for: {state['parsed_requirements'].get('project_name', 'Unknown Project')}

# Based on the requirements and architecture, define key terms that stakeholders should understand.
# Include both technical terms and business domain terms.

# Return as a JSON object where keys are terms and values are definitions.
# Example: {{"API": "Application Programming Interface - a set of protocols for building software applications"}}
# """
                
#                 messages = [
#                     SystemMessage(content="You are a Technical Writer expert at creating glossaries."),
#                     HumanMessage(content=prompt)
#                 ]
                
#                 response = await self.llm.ainvoke(messages)
#                 content = response.content
                
#                 try:
#                     if content.startswith('```json'):
#                         content = content.split('```json')[1].split('```')[0].strip()
#                     elif content.startswith('```'):
#                         content = content.split('```')[1].split('```')[0].strip()
                    
#                     glossary = json.loads(content)
#                     if isinstance(glossary, dict):
#                         state["glossary"] = glossary
#                     else:
#                         state["glossary"] = {"SRS": "Software Requirements Specification"}
#                     logger.info(f"Built glossary with {len(state['glossary'])} terms")
#                 except json.JSONDecodeError:
#                     state["glossary"] = {
#                         "SRS": "Software Requirements Specification",
#                         "API": "Application Programming Interface",
#                         "UI": "User Interface"
#                     }
                    
#             except Exception as e:
#                 logger.error(f"Error building glossary: {e}")
#                 state["glossary"] = {
#                     "SRS": "Software Requirements Specification",
#                     "API": "Application Programming Interface",
#                     "UI": "User Interface"
#                 }
#         else:
#             # Fallback without LLM
#             logger.info("Building glossary (fallback mode)")
#             state["glossary"] = {
#                 "SRS": "Software Requirements Specification - a document that describes the functionality and behavior of a software system",
#                 "API": "Application Programming Interface - a set of protocols and tools for building software applications",
#                 "UI": "User Interface - the space where interactions between users and a system occur",
#                 "UX": "User Experience - the overall experience of a person using a product or system",
#                 "CRUD": "Create, Read, Update, Delete - the four basic operations of persistent storage"
#             }
        
#         state["processing_steps"].append("Technical glossary built")
#         return state
    
#     async def _compile_document(self, state: SRSWorkflowState, config: RunnableConfig) -> SRSWorkflowState:
#         """Compile all sections into final SRS document."""
#         logger.info("Step 10: Compiling final SRS document")
        
#         # Compile the complete SRS document
#         srs_document = {
#             "title": state["parsed_requirements"].get("project_name", "Software Requirements Specification"),
#             "version": "1.0",
#             "date": datetime.utcnow().strftime('%Y-%m-%d'),
#             "author": "BA Copilot AI",
#             "project_overview": state["parsed_requirements"].get("purpose", state["project_input"]),
#             "functional_requirements": state["functional_requirements"],
#             "non_functional_requirements": state["non_functional_requirements"],
#             "system_architecture": state["system_architecture"],
#             "user_stories": state["user_stories"],
#             "constraints": state["constraints"],
#             "assumptions": state["assumptions"],
#             "glossary": state["glossary"],
#             "metadata": {
#                 "document_id": state["document_id"],
#                 "generated_at": state["generated_at"],
#                 "user_id": state.get("user_id"),
#                 "project_id": state.get("project_id"),
#                 "provider": getattr(self, 'provider', 'unknown'),
#                 "processing_steps": state["processing_steps"]
#             }
#         }
        
#         state["srs_document"] = srs_document
#         state["processing_steps"].append("SRS document compiled")
#         logger.info(f"Compiled SRS document with {len(state['functional_requirements'])} functional requirements")
        
#         return state
    
#     async def _finalize_document(self, state: SRSWorkflowState, config: RunnableConfig) -> SRSWorkflowState:
#         """Finalize the document and set completion status."""
#         logger.info("Step 11: Finalizing SRS document")
        
#         state["status"] = "completed"
#         state["processing_steps"].append("SRS document finalized and ready")
        
#         logger.info(f"SRS document {state['document_id']} successfully generated with LangGraph workflow")
#         return state
    
#     async def generate_srs_document(self, project_input: str, user_id: Optional[str] = None, project_id: Optional[int] = None) -> Dict[str, Any]:
#         """
#         Generate SRS document using the LangGraph workflow.
        
#         Args:
#             project_input: User's project description
#             user_id: Optional user ID
#             project_id: Optional project ID
            
#         Returns:
#             Generated SRS document with metadata
#         """
#         try:
#             # Initialize state
#             initial_state: SRSWorkflowState = {
#                 "project_input": project_input,
#                 "user_id": user_id,
#                 "project_id": project_id,
#                 "parsed_requirements": {},
#                 "functional_requirements": [],
#                 "non_functional_requirements": [],
#                 "system_architecture": "",
#                 "user_stories": [],
#                 "constraints": [],
#                 "assumptions": [],
#                 "glossary": {},
#                 "srs_document": {},
#                 "document_id": "",
#                 "status": "starting",
#                 "error_message": None,
#                 "processing_steps": [],
#                 "generated_at": ""
#             }
            
#             # Run the workflow
#             logger.info("Starting SRS generation workflow")
#             final_state = await self.graph.ainvoke(initial_state)
            
#             if final_state["status"] == "completed":
#                 logger.info(f"SRS workflow completed successfully for document {final_state['document_id']}")
#                 return final_state["srs_document"]
#             else:
#                 raise Exception(f"Workflow failed with status: {final_state['status']}")
                
#         except Exception as e:
#             logger.error(f"Error in SRS workflow: {str(e)}")
#             # Return fallback document
#             current_date_string = datetime.utcnow().strftime('%Y-%m-%d')
#             return {
#                 "title": "Generated SRS Document (Workflow Fallback)",
#                 "version": "1.0",
#                 "date": current_date_string,
#                 "author": "BA Copilot AI",
#                 "project_overview": project_input,
#                 "functional_requirements": ["Requirements based on: " + project_input],
#                 "non_functional_requirements": ["Performance and security requirements to be defined"],
#                 "system_architecture": "Architecture to be defined based on requirements",
#                 "user_stories": ["User story derived from: " + project_input],
#                 "constraints": ["Technical constraints to be identified"],
#                 "assumptions": ["Assumptions to be validated"],
#                 "glossary": {"SRS": "Software Requirements Specification"},
#                 "metadata": {
#                     "document_id": str(uuid4()),
#                     "generated_at": datetime.utcnow().isoformat(),
#                     "user_id": user_id,
#                     "project_id": project_id,
#                     "provider": "fallback",
#                     "error": str(e)
#                 }
#             }