"""
Unit and integration tests for stakeholder register generation workflow
"""
import pytest
import sys
import os
from unittest.mock import Mock, MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflows.stakeholder_register_workflow import stakeholder_register_graph


class TestStakeholderRegisterWorkflow:
    """Test suite for stakeholder register workflow"""

    def test_stakeholder_register_graph_exists(self):
        """Test that stakeholder_register_graph is properly exported"""
        assert stakeholder_register_graph is not None

    @patch('workflows.stakeholder_register_workflow.workflow.OpenAI')
    def test_generate_stakeholder_register_success(self, mock_openai):
        """Test successful stakeholder register generation"""
        # Mock the OpenAI response
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = """{
            "title": "Stakeholder Register - E-commerce Platform",
            "content": "# Stakeholder Register\\n\\n## Project: E-commerce Platform\\n\\n### Document Information\\n- **Date:** 2025-12-12\\n- **Version:** 1.0\\n- **Prepared by:** BA Copilot AI\\n\\n## Executive Summary\\nThis document identifies and analyzes all stakeholders involved in the E-commerce Platform project.\\n\\n## Stakeholder List\\n\\n### Internal Stakeholders\\n\\n#### 1. Product Owner - John Smith\\n- **Department:** Product Management\\n- **Role:** Decision maker\\n- **Interest Level:** High\\n- **Influence Level:** High\\n- **Engagement Strategy:** Weekly meetings\\n- **Communication Preferences:** Email, Slack\\n- **Key Concerns:** Timeline, Features\\n\\n#### 2. Development Team Lead - Sarah Johnson\\n- **Department:** Engineering\\n- **Role:** Technical lead\\n- **Interest Level:** High\\n- **Influence Level:** Medium-High\\n- **Engagement Strategy:** Daily standups\\n- **Communication Preferences:** Slack, Jira\\n- **Key Concerns:** Technical feasibility\\n\\n### External Stakeholders\\n\\n#### 3. End Users\\n- **Category:** Primary users\\n- **Interest Level:** High\\n- **Influence Level:** Medium\\n- **Engagement Strategy:** User research\\n- **Key Concerns:** User experience\\n\\n## Stakeholder Analysis Matrix\\n\\n| Stakeholder | Power | Interest | Strategy |\\n|-------------|-------|----------|----------|\\n| Product Owner | High | High | Manage Closely |\\n| Development Lead | High | High | Manage Closely |\\n| End Users | Medium | High | Keep Informed |\\n\\n## Communication Plan\\n\\n### High-Priority Stakeholders\\n- Product Owner: Weekly updates\\n- Development Lead: Daily standups\\n\\n## Conclusion\\nEffective stakeholder management is critical for project success."
        }"""
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client

        # Test input
        test_input = {
            "user_message": "Create a stakeholder register for e-commerce platform project with product owner, development team, and end users"
        }

        # Invoke workflow
        result = stakeholder_register_graph.invoke(test_input)

        # Assertions
        assert result is not None
        assert "response" in result
        assert "title" in result["response"]
        assert "content" in result["response"]
        assert "Stakeholder Register" in result["response"]["title"]
        assert "Stakeholder List" in result["response"]["content"] or "stakeholder" in result["response"]["content"].lower()

    @patch('workflows.stakeholder_register_workflow.workflow.OpenAI')
    def test_generate_stakeholder_register_with_multiple_stakeholders(self, mock_openai):
        """Test stakeholder register with multiple stakeholder types"""
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = """{
            "title": "Stakeholder Register - Mobile Banking App",
            "content": "# Stakeholder Register\\n\\n## Stakeholder List\\n\\n### Internal Stakeholders\\n1. Executive Sponsor\\n2. Product Manager\\n3. Development Team\\n4. QA Team\\n5. Security Team\\n\\n### External Stakeholders\\n1. End Users\\n2. Regulatory Bodies\\n3. Third-party Vendors\\n\\n## Analysis Matrix\\n| Stakeholder | Power | Interest |\\n|-------------|-------|----------|\\n| Exec Sponsor | High | Medium |\\n| Product Mgr | High | High |\\n| Dev Team | Medium | High |\\n| End Users | Low | High |\\n| Regulators | High | Medium |"
        }"""
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client

        test_input = {
            "user_message": "Generate stakeholder register for mobile banking application with executive sponsor, product manager, dev team, QA, security team, end users, regulatory bodies, and vendors"
        }

        result = stakeholder_register_graph.invoke(test_input)

        assert result is not None
        assert "response" in result
        assert "title" in result["response"]
        assert "content" in result["response"]

    @patch('workflows.stakeholder_register_workflow.workflow.OpenAI')
    def test_generate_stakeholder_register_error_handling(self, mock_openai):
        """Test error handling in stakeholder register generation"""
        # Mock the client and its methods
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        test_input = {
            "user_message": "Create stakeholder register"
        }

        result = stakeholder_register_graph.invoke(test_input)

        # Should return error in response
        assert result is not None
        assert "response" in result
        assert "content" in result["response"]
        assert "Error generating document" in result["response"]["content"]

    @patch('workflows.stakeholder_register_workflow.workflow.OpenAI')
    def test_generate_stakeholder_register_invalid_json(self, mock_openai):
        """Test handling of invalid JSON response"""
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = "This is not valid JSON"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client

        test_input = {
            "user_message": "Create stakeholder register"
        }

        result = stakeholder_register_graph.invoke(test_input)

        # Should handle gracefully
        assert result is not None
        assert "response" in result

    @patch('workflows.stakeholder_register_workflow.workflow.OpenAI')
    def test_stakeholder_register_includes_engagement_strategy(self, mock_openai):
        """Test that generated register includes engagement strategies"""
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = """{
            "title": "Stakeholder Register",
            "content": "# Stakeholder Register\\n\\n## Engagement Activities\\n1. Kick-off Meeting\\n2. Requirements Workshops\\n3. Sprint Reviews\\n4. User Acceptance Testing\\n\\n## Communication Plan\\n- Weekly updates for high-priority stakeholders\\n- Monthly reports for executive sponsors"
        }"""
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client

        test_input = {
            "user_message": "Create comprehensive stakeholder register with engagement strategies"
        }

        result = stakeholder_register_graph.invoke(test_input)

        assert result is not None
        assert "response" in result
        assert "content" in result["response"]

    @patch('workflows.stakeholder_register_workflow.workflow.OpenAI')
    def test_stakeholder_register_includes_risk_assessment(self, mock_openai):
        """Test that generated register includes risk assessment"""
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = """{
            "title": "Stakeholder Register - CRM System",
            "content": "# Stakeholder Register\\n\\n## Risk Assessment\\n- Conflicting stakeholder interests\\n- Communication gaps between departments\\n- Decision delays due to multiple approval layers\\n\\n## Mitigation Strategies\\n- Regular alignment meetings\\n- Clear escalation paths\\n- Documented decision-making process"
        }"""
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client

        test_input = {
            "user_message": "Generate stakeholder register for CRM system with risk assessment"
        }

        result = stakeholder_register_graph.invoke(test_input)

        assert result is not None
        assert "response" in result
        assert "title" in result["response"]
        assert "content" in result["response"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
