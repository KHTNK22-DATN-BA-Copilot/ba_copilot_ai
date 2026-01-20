# tests/test_constraint_context.py
"""
Comprehensive Test Suite for Document Constraint Context System

This test suite validates that the AI service properly handles prerequisite
document context provided by the Backend's constraint validation system.

The Backend is responsible for:
- Validating document constraints (required/recommended prerequisites)
- Filtering prerequisite documents based on document type
- Providing only relevant prerequisite documents via storage_paths

The AI service is responsible for:
- Loading prerequisite documents from storage_paths
- Incorporating prerequisite context into generation prompts
- Generating documents with appropriate context awareness

This test suite focuses on the AI service's context handling responsibilities.
"""

import pytest
from workflows.nodes.prerequisite_context import (
    format_prerequisite_context,
    build_context_aware_prompt,
    log_prerequisite_usage,
    validate_prerequisite_state,
    get_prerequisite_summary,
    count_prerequisite_documents,
    extract_prerequisite_filenames
)
from workflows.nodes.get_content_file import get_content_file


class TestPrerequisiteContextFormatting:
    """Test prerequisite context formatting utilities"""

    def test_format_prerequisite_context_with_documents(self):
        """Test formatting with prerequisite documents"""
        extracted_text = """### File: business-case.md
# Business Case
Project: E-commerce Platform
Cost: $500K
Benefit: $2M ROI

### File: scope-statement.md
# Scope Statement
In Scope: Mobile app, Web portal, Admin dashboard
Out of Scope: Payment processing"""

        result = format_prerequisite_context(extracted_text=extracted_text)

        assert "PREREQUISITE DOCUMENTS" in result
        assert "business-case.md" in result
        assert "scope-statement.md" in result
        assert "E-commerce Platform" in result
        assert "validated and provided as context" in result

    def test_format_prerequisite_context_with_chat_history(self):
        """Test formatting with chat context"""
        chat_context = "User previously asked for a mobile-first design approach."

        result = format_prerequisite_context(
            extracted_text="",
            chat_context=chat_context
        )

        assert "CONVERSATION HISTORY" in result
        assert "mobile-first design" in result

    def test_format_prerequisite_context_combined(self):
        """Test formatting with both prerequisites and chat history"""
        extracted_text = "### File: requirements.md\nFunctional Requirements:\n- User login"
        chat_context = "Focus on security aspects"

        result = format_prerequisite_context(
            extracted_text=extracted_text,
            chat_context=chat_context
        )

        assert "PREREQUISITE DOCUMENTS" in result
        assert "CONVERSATION HISTORY" in result
        assert "User login" in result
        assert "security aspects" in result

    def test_format_prerequisite_context_empty(self):
        """Test formatting with no context"""
        result = format_prerequisite_context(
            extracted_text="",
            chat_context=""
        )

        assert result == ""

    def test_format_prerequisite_context_whitespace_only(self):
        """Test formatting with whitespace-only content"""
        result = format_prerequisite_context(
            extracted_text="   \n\n  ",
            chat_context="  \t  "
        )

        assert result == ""


class TestContextAwarePromptBuilding:
    """Test context-aware prompt construction"""

    def test_build_context_aware_prompt_top_position(self):
        """Test building prompt with context at top"""
        base_prompt = "Generate a high-level architecture diagram"
        extracted_text = "### File: requirements.md\nSystem must handle 10K users"

        result = build_context_aware_prompt(
            base_prompt=base_prompt,
            extracted_text=extracted_text,
            context_position="top"
        )

        # Context should come before prompt
        context_index = result.find("PREREQUISITE DOCUMENTS")
        prompt_index = result.find("Generate a high-level")
        assert context_index < prompt_index
        assert "10K users" in result

    def test_build_context_aware_prompt_bottom_position(self):
        """Test building prompt with context at bottom"""
        base_prompt = "Create API documentation"
        extracted_text = "### File: hld-arch.md\nMicroservices architecture"

        result = build_context_aware_prompt(
            base_prompt=base_prompt,
            extracted_text=extracted_text,
            context_position="bottom"
        )

        # Prompt should come before context
        context_index = result.find("PREREQUISITE DOCUMENTS")
        prompt_index = result.find("Create API documentation")
        assert prompt_index < context_index
        assert "Microservices" in result

    def test_build_context_aware_prompt_no_context(self):
        """Test building prompt with no context available"""
        base_prompt = "Generate SRS document"

        result = build_context_aware_prompt(
            base_prompt=base_prompt,
            extracted_text=None,
            chat_context=None
        )

        # Should return base prompt unchanged
        assert result == base_prompt

    def test_build_context_aware_prompt_with_chat_history(self):
        """Test building prompt with chat history context"""
        base_prompt = "Create database schema"
        chat_context = "User prefers PostgreSQL with JSON columns"

        result = build_context_aware_prompt(
            base_prompt=base_prompt,
            chat_context=chat_context
        )

        assert "CONVERSATION HISTORY" in result
        assert "PostgreSQL" in result
        assert "Create database schema" in result


class TestPrerequisiteStateValidation:
    """Test prerequisite state validation"""

    def test_validate_prerequisite_state_valid(self):
        """Test validation with valid state (storage_paths + extracted_text)"""
        state = {
            'storage_paths': ['project/123/business-case.md', 'project/123/scope.md'],
            'extracted_text': '### File: business-case.md\nContent here',
            'user_message': 'Generate HLD'
        }

        result = validate_prerequisite_state(state)

        # Should return state unchanged
        assert result == state
        assert result['storage_paths'] == state['storage_paths']

    def test_validate_prerequisite_state_no_prerequisites(self):
        """Test validation with no prerequisites (valid for entry point documents)"""
        state = {
            'storage_paths': [],
            'extracted_text': '',
            'user_message': 'Generate stakeholder register'
        }

        result = validate_prerequisite_state(state)

        # Should return state unchanged
        assert result == state

    def test_validate_prerequisite_state_missing_extracted_text(self):
        """Test validation when storage_paths provided but extracted_text missing"""
        state = {
            'storage_paths': ['project/123/requirements.md'],
            'extracted_text': '',
            'user_message': 'Generate design'
        }

        # Should still return state (just logs warning)
        result = validate_prerequisite_state(state)
        assert result == state

    def test_validate_prerequisite_state_extracted_text_without_paths(self):
        """Test validation when extracted_text exists without storage_paths"""
        state = {
            'storage_paths': [],
            'extracted_text': 'Some manual context',
            'user_message': 'Generate document'
        }

        result = validate_prerequisite_state(state)
        assert result == state


class TestPrerequisiteUtilities:
    """Test utility functions for prerequisite handling"""

    def test_get_prerequisite_summary_short_text(self):
        """Test summary generation for short text"""
        text = "Short prerequisite content"

        result = get_prerequisite_summary(text, max_length=500)

        assert result == "Short prerequisite content"

    def test_get_prerequisite_summary_long_text(self):
        """Test summary generation for long text"""
        text = "A" * 1000

        result = get_prerequisite_summary(text, max_length=100)

        assert len(result) <= 120  # 100 + "... (truncated)" with some buffer
        assert result.endswith("... (truncated)")

    def test_get_prerequisite_summary_empty(self):
        """Test summary for empty text"""
        result = get_prerequisite_summary("")

        assert result == "No prerequisite content"

    def test_count_prerequisite_documents_multiple(self):
        """Test counting multiple prerequisite documents"""
        extracted_text = """### File: doc1.md
Content 1

### File: doc2.md
Content 2

### File: doc3.md
Content 3"""

        count = count_prerequisite_documents(extracted_text)

        assert count == 3

    def test_count_prerequisite_documents_single(self):
        """Test counting single prerequisite document"""
        extracted_text = "### File: requirements.md\nSome content"

        count = count_prerequisite_documents(extracted_text)

        assert count == 1

    def test_count_prerequisite_documents_none(self):
        """Test counting with no documents"""
        count = count_prerequisite_documents("")

        assert count == 0

    def test_extract_prerequisite_filenames_multiple(self):
        """Test extracting multiple filenames"""
        extracted_text = """### File: business-case.md
Content

### File: scope-statement.md
Content

### File: high-level-requirements.md
Content"""

        filenames = extract_prerequisite_filenames(extracted_text)

        assert len(filenames) == 3
        assert "business-case.md" in filenames
        assert "scope-statement.md" in filenames
        assert "high-level-requirements.md" in filenames

    def test_extract_prerequisite_filenames_single(self):
        """Test extracting single filename"""
        extracted_text = "### File: requirements.md\nContent here"

        filenames = extract_prerequisite_filenames(extracted_text)

        assert len(filenames) == 1
        assert filenames[0] == "requirements.md"

    def test_extract_prerequisite_filenames_empty(self):
        """Test extracting from empty text"""
        filenames = extract_prerequisite_filenames("")

        assert filenames == []

    def test_extract_prerequisite_filenames_malformed(self):
        """Test extracting from malformed markers"""
        extracted_text = "### File:\n### File:   \nSome content without file marker"

        filenames = extract_prerequisite_filenames(extracted_text)

        # Should not include empty filenames
        assert all(f.strip() for f in filenames)


class TestWorkflowStateIntegration:
    """Test integration with actual workflow state structures"""

    def test_workflow_state_with_prerequisites(self):
        """Test typical workflow state with prerequisite documents"""
        state = {
            'user_message': 'Generate HLD Architecture',
            'response': {},
            'content_id': None,
            'storage_paths': [
                'uploads/project-1/high-level-requirements.md',
                'uploads/project-1/scope-statement.md'
            ],
            'extracted_text': None,
            'chat_context': None
        }

        # Simulate get_content_file processing
        # In real workflow, this would fetch from Supabase
        mock_extracted = """### File: high-level-requirements.md
# High Level Requirements
- User authentication
- Data management
- Reporting dashboard

### File: scope-statement.md
# Scope Statement
In Scope: Web application, Mobile app
Out of Scope: Desktop client"""

        state['extracted_text'] = mock_extracted

        # Validate state
        validated = validate_prerequisite_state(state)
        assert 'extracted_text' in validated
        assert validated['extracted_text'] == mock_extracted

        # Format context
        formatted = format_prerequisite_context(
            extracted_text=validated['extracted_text'],
            chat_context=validated.get('chat_context')
        )

        assert "PREREQUISITE DOCUMENTS" in formatted
        assert "User authentication" in formatted
        assert "Web application" in formatted

    def test_workflow_state_entry_point_document(self):
        """Test workflow state for entry point documents (no prerequisites)"""
        state = {
            'user_message': 'Generate stakeholder register',
            'response': {},
            'content_id': None,
            'storage_paths': [],  # No prerequisites required
            'extracted_text': '',
            'chat_context': None
        }

        # Validate state
        validated = validate_prerequisite_state(state)

        # Build prompt (should work without context)
        base_prompt = "Create a stakeholder register document"
        prompt = build_context_aware_prompt(
            base_prompt=base_prompt,
            extracted_text=validated.get('extracted_text')
        )

        # Should return base prompt unchanged
        assert prompt == base_prompt

    def test_workflow_state_with_chat_context_only(self):
        """Test workflow state with chat history but no prerequisite documents"""
        state = {
            'user_message': 'Refine the design',
            'response': {},
            'content_id': 'conv-123',
            'storage_paths': [],
            'extracted_text': '',
            'chat_context': 'User requested focus on scalability and performance'
        }

        formatted = format_prerequisite_context(
            extracted_text=state['extracted_text'],
            chat_context=state['chat_context']
        )

        assert "CONVERSATION HISTORY" in formatted
        assert "scalability" in formatted
        assert "PREREQUISITE DOCUMENTS" not in formatted


class TestGetContentFileNode:
    """Test the get_content_file node function"""

    def test_get_content_file_empty_storage_paths(self):
        """Test get_content_file with no storage paths"""
        state = {
            'user_message': 'Generate document',
            'storage_paths': []
        }

        result = get_content_file(state)

        assert 'extracted_text' in result
        assert result['extracted_text'] == ""

    def test_get_content_file_none_storage_paths(self):
        """Test get_content_file with None storage paths"""
        state = {
            'user_message': 'Generate document',
            'storage_paths': None
        }

        result = get_content_file(state)

        assert 'extracted_text' in result
        assert result['extracted_text'] == ""

    def test_get_content_file_preserves_other_state(self):
        """Test that get_content_file preserves other state properties"""
        state = {
            'user_message': 'Generate document',
            'response': {'existing': 'data'},
            'content_id': 'test-123',
            'storage_paths': [],
            'chat_context': 'Some context'
        }

        result = get_content_file(state)

        assert result['user_message'] == 'Generate document'
        assert result['response'] == {'existing': 'data'}
        assert result['content_id'] == 'test-123'
        assert result['chat_context'] == 'Some context'


class TestRealWorldScenarios:
    """Test real-world document generation scenarios"""

    def test_scenario_hld_arch_with_prerequisites(self):
        """
        Scenario: Generate HLD Architecture with required prerequisites
        Prerequisites: high-level-requirements, scope-statement
        """
        # Simulate Backend providing validated prerequisites
        state = {
            'user_message': 'Create high-level architecture for e-commerce platform',
            'storage_paths': [
                'uploads/project-1/high-level-requirements.md',
                'uploads/project-1/scope-statement.md'
            ],
            'extracted_text': """### File: high-level-requirements.md
# High Level Requirements

## Functional Requirements
- User registration and authentication
- Product catalog management
- Shopping cart functionality
- Order processing
- Payment integration

## Non-Functional Requirements
- Support 10,000 concurrent users
- 99.9% uptime
- PCI DSS compliance for payments

### File: scope-statement.md
# Scope Statement

## In Scope
- Web application (React)
- Mobile apps (iOS, Android)
- Admin portal
- REST API backend
- PostgreSQL database

## Out of Scope
- Physical retail integration
- Legacy system migration
- Custom payment gateway""",
            'chat_context': None
        }

        # Build context-aware prompt
        base_prompt = """
### ROLE
You are a professional Solution Architect.

### TASK
Create a High-Level Design (HLD) Architecture Diagram.

### OUTPUT
Return HLD architecture in Mermaid format.
"""

        prompt = build_context_aware_prompt(
            base_prompt=base_prompt,
            extracted_text=state['extracted_text'],
            context_position="top"
        )

        # Verify context is properly incorporated
        assert "PREREQUISITE DOCUMENTS" in prompt
        assert "User registration and authentication" in prompt
        assert "10,000 concurrent users" in prompt
        assert "React" in prompt
        assert "PostgreSQL" in prompt
        assert "Solution Architect" in prompt

    def test_scenario_lld_api_with_hld_context(self):
        """
        Scenario: Generate LLD API with HLD architecture as prerequisite
        Prerequisites: hld-arch, high-level-requirements
        """
        state = {
            'user_message': 'Generate API specifications',
            'storage_paths': [
                'uploads/project-1/hld-arch.md',
                'uploads/project-1/high-level-requirements.md'
            ],
            'extracted_text': """### File: hld-arch.md
# HLD Architecture

## Architecture Style
Microservices architecture with API Gateway

## Services
- User Service (Authentication, Profile)
- Product Service (Catalog, Search)
- Order Service (Cart, Checkout)
- Payment Service (Integration with Stripe)

## Communication
- Synchronous: REST APIs
- Asynchronous: RabbitMQ for events

### File: high-level-requirements.md
# High Level Requirements

API Requirements:
- RESTful API design
- JWT-based authentication
- Rate limiting: 100 req/min per user
- API versioning (v1, v2)
- OpenAPI documentation""",
            'chat_context': None
        }

        formatted = format_prerequisite_context(
            extracted_text=state['extracted_text']
        )

        assert "Microservices architecture" in formatted
        assert "User Service" in formatted
        assert "JWT-based authentication" in formatted
        assert "Rate limiting" in formatted

    def test_scenario_srs_synthesis_with_multiple_prerequisites(self):
        """
        Scenario: Generate SRS (synthesis document) with multiple prerequisites
        Prerequisites: high-level-requirements, scope-statement, stakeholder-register
        """
        state = {
            'user_message': 'Create comprehensive SRS document',
            'storage_paths': [
                'uploads/project-1/high-level-requirements.md',
                'uploads/project-1/scope-statement.md',
                'uploads/project-1/stakeholder-register.md'
            ],
            'extracted_text': """### File: high-level-requirements.md
Functional: User auth, Product catalog, Order management
Non-Functional: Performance, Security, Scalability

### File: scope-statement.md
In Scope: Web + Mobile apps, Admin portal, REST API
Out of Scope: Desktop app, Legacy migration

### File: stakeholder-register.md
1. Product Owner: Jane Doe (jane@example.com)
2. Development Team: 8 engineers
3. QA Team: 3 testers
4. End Users: Online shoppers""",
            'chat_context': None
        }

        # Count prerequisites
        doc_count = count_prerequisite_documents(state['extracted_text'])
        assert doc_count == 3

        # Extract filenames
        filenames = extract_prerequisite_filenames(state['extracted_text'])
        assert len(filenames) == 3
        assert 'stakeholder-register.md' in filenames

        # Format context
        formatted = format_prerequisite_context(
            extracted_text=state['extracted_text']
        )

        assert "User auth" in formatted
        assert "Web + Mobile apps" in formatted
        assert "Jane Doe" in formatted

    def test_scenario_entry_point_no_prerequisites(self):
        """
        Scenario: Generate stakeholder register (entry point, no prerequisites)
        Prerequisites: None (entry point document)
        """
        state = {
            'user_message': 'Create stakeholder register for new CRM project',
            'storage_paths': [],  # No prerequisites needed
            'extracted_text': '',
            'chat_context': None
        }

        # Validate this is acceptable
        validated = validate_prerequisite_state(state)
        assert validated == state

        # Build prompt without context
        base_prompt = "Generate stakeholder register document"
        prompt = build_context_aware_prompt(
            base_prompt=base_prompt,
            extracted_text=state['extracted_text']
        )

        # Should be base prompt only
        assert prompt == base_prompt
        assert "PREREQUISITE" not in prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
