"""
Unit and integration tests for high-level requirements generation workflow
"""
import pytest
import sys
import os
from unittest.mock import Mock, MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflows.high_level_requirements_workflow import high_level_requirements_graph


class TestHighLevelRequirementsWorkflow:
    """Test suite for high-level requirements workflow"""

    def test_high_level_requirements_graph_exists(self):
        """Test that high_level_requirements_graph is properly exported"""
        assert high_level_requirements_graph is not None

    @patch('workflows.high_level_requirements_workflow.workflow.OpenAI')
    def test_generate_high_level_requirements_success(self, mock_openai):
        """Test successful high-level requirements generation"""
        # Mock the OpenAI response
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = """{
            "title": "High-Level Requirements - E-commerce Platform",
            "content": "# High-Level Requirements Document\\n\\n## Project: E-commerce Platform\\n\\n### Document Control\\n- **Version:** 1.0\\n- **Date:** 2025-12-12\\n- **Status:** Draft\\n\\n## 1. Introduction\\n\\n### 1.1 Purpose\\nThis document outlines high-level requirements for the E-commerce Platform.\\n\\n### 1.2 Scope\\nOnline marketplace with payment processing and inventory management.\\n\\n### 1.3 Business Objectives\\n- Increase online sales by 30%\\n- Improve customer experience\\n- Reduce operational costs\\n\\n## 2. Stakeholder Requirements\\n\\n### 2.1 Retail Customers\\n- Browse product catalog\\n- Add items to cart\\n- Complete checkout\\n- Track orders\\n\\n### 2.2 Administrators\\n- Manage products\\n- Process orders\\n- Generate reports\\n\\n## 3. Functional Requirements\\n\\n### 3.1 User Management (FR-UM)\\n- **FR-UM-001:** User registration and authentication\\n- **FR-UM-002:** User profile management\\n- **FR-UM-003:** Role-based access control\\n\\n### 3.2 Product Catalog (FR-PC)\\n- **FR-PC-001:** Product listings with images\\n- **FR-PC-002:** Search and filtering\\n- **FR-PC-003:** Real-time inventory\\n\\n### 3.3 Shopping Cart (FR-SC)\\n- **FR-SC-001:** Add/remove cart items\\n- **FR-SC-002:** Calculate totals\\n- **FR-SC-003:** Multiple payment methods\\n\\n## 4. Non-Functional Requirements\\n\\n### 4.1 Performance (NFR-P)\\n- **NFR-P-001:** Page load < 2 seconds\\n- **NFR-P-002:** Support 10,000 concurrent users\\n\\n### 4.2 Security (NFR-S)\\n- **NFR-S-001:** Data encryption\\n- **NFR-S-002:** PCI-DSS compliance\\n\\n### 4.3 Usability (NFR-U)\\n- **NFR-U-001:** Multi-device support\\n- **NFR-U-002:** Multi-language support\\n\\n## 5. Constraints\\n- Budget: $500,000\\n- Timeline: 6 months\\n- Must integrate with existing ERP\\n\\n## 6. Assumptions\\n- Payment gateway APIs available\\n- ERP provides REST APIs\\n\\n## 7. Dependencies\\n- Payment gateway integration\\n- Cloud infrastructure\\n\\n## 8. Acceptance Criteria\\n- All functional requirements implemented\\n- Performance benchmarks met\\n- Security audit passed\\n\\n## 9. Approval\\n| Role | Name | Signature | Date |\\n|------|------|-----------|------|\\n| Product Owner | | | |\\n| Business Analyst | | | |"
        }"""
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client

        # Test input
        test_input = {
            "user_message": "Create high-level requirements for e-commerce platform with user management, product catalog, shopping cart, and payment processing"
        }

        # Invoke workflow
        result = high_level_requirements_graph.invoke(test_input)

        # Assertions
        assert result is not None
        assert "response" in result
        assert "title" in result["response"]
        assert "content" in result["response"]
        assert "High-Level Requirements" in result["response"]["title"]
        assert "Functional Requirements" in result["response"]["content"] or "functional" in result["response"]["content"].lower()

    @patch('workflows.high_level_requirements_workflow.workflow.OpenAI')
    def test_generate_high_level_requirements_with_nfrs(self, mock_openai):
        """Test requirements generation including non-functional requirements"""
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = """{
            "title": "High-Level Requirements - Healthcare System",
            "content": "# High-Level Requirements\\n\\n## Functional Requirements\\n- **FR-001:** Patient registration\\n- **FR-002:** Appointment scheduling\\n- **FR-003:** Medical records management\\n\\n## Non-Functional Requirements\\n### Performance\\n- **NFR-P-001:** Response time < 1 second\\n- **NFR-P-002:** Handle 5000 concurrent users\\n\\n### Security\\n- **NFR-S-001:** HIPAA compliance\\n- **NFR-S-002:** End-to-end encryption\\n- **NFR-S-003:** Two-factor authentication\\n\\n### Reliability\\n- **NFR-R-001:** 99.99% uptime\\n- **NFR-R-002:** Automated backups\\n\\n### Usability\\n- **NFR-U-001:** WCAG 2.1 AA compliance\\n- **NFR-U-002:** Mobile responsive"
        }"""
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client

        test_input = {
            "user_message": "Generate high-level requirements for healthcare system with HIPAA compliance, performance requirements, and security needs"
        }

        result = high_level_requirements_graph.invoke(test_input)

        assert result is not None
        assert "response" in result
        assert "title" in result["response"]
        assert "content" in result["response"]

    @patch('workflows.high_level_requirements_workflow.workflow.OpenAI')
    def test_generate_requirements_with_constraints(self, mock_openai):
        """Test requirements generation with constraints and assumptions"""
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = """{
            "title": "High-Level Requirements - Mobile App",
            "content": "# Requirements Document\\n\\n## Constraints\\n### Budget\\n- Total budget: $200,000\\n\\n### Timeline\\n- Development: 4 months\\n- Launch: Q2 2026\\n\\n### Technical\\n- Must support iOS 15+\\n- Must support Android 11+\\n- Cloud-hosted backend\\n\\n### Regulatory\\n- GDPR compliance\\n- App store guidelines\\n\\n## Assumptions\\n- Third-party APIs are stable\\n- Users have internet connectivity\\n- Device cameras are functional\\n\\n## Dependencies\\n- Cloud provider account\\n- API keys for services\\n- Design assets from UX team"
        }"""
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client

        test_input = {
            "user_message": "Create requirements for mobile app with budget $200k, 4-month timeline, iOS/Android support"
        }

        result = high_level_requirements_graph.invoke(test_input)

        assert result is not None
        assert "response" in result

    @patch('workflows.high_level_requirements_workflow.workflow.OpenAI')
    def test_generate_requirements_error_handling(self, mock_openai):
        """Test error handling in requirements generation"""
        # Mock the client and its methods
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Connection Error")

        test_input = {
            "user_message": "Create high-level requirements"
        }

        result = high_level_requirements_graph.invoke(test_input)

        # Should return error in response
        assert result is not None
        assert "response" in result
        assert "content" in result["response"]
        assert "Error generating document" in result["response"]["content"]

    @patch('workflows.high_level_requirements_workflow.workflow.OpenAI')
    def test_requirements_includes_acceptance_criteria(self, mock_openai):
        """Test that requirements include acceptance criteria"""
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = """{
            "title": "High-Level Requirements - CRM System",
            "content": "# Requirements\\n\\n## Acceptance Criteria\\n\\n### Functional\\n- All FR requirements implemented and tested\\n- User workflows validated\\n- Integration with existing systems verified\\n\\n### Performance\\n- Load testing passed for 10k concurrent users\\n- Page load times under 2 seconds\\n- API response times under 500ms\\n\\n### Security\\n- Security audit passed\\n- No critical vulnerabilities\\n- Penetration testing completed\\n\\n### Quality\\n- Code coverage > 80%\\n- All critical bugs resolved\\n- UAT sign-off obtained"
        }"""
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client

        test_input = {
            "user_message": "Generate requirements with detailed acceptance criteria"
        }

        result = high_level_requirements_graph.invoke(test_input)

        assert result is not None
        assert "response" in result

    @patch('workflows.high_level_requirements_workflow.workflow.OpenAI')
    def test_requirements_with_stakeholder_needs(self, mock_openai):
        """Test requirements generation addressing multiple stakeholder needs"""
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = """{
            "title": "High-Level Requirements - Inventory System",
            "content": "# Requirements\\n\\n## Stakeholder Requirements\\n\\n### Warehouse Staff\\n- Scan barcodes for quick inventory updates\\n- View stock levels in real-time\\n- Generate picking lists\\n- Report damaged items\\n\\n### Managers\\n- View inventory reports and analytics\\n- Set reorder points\\n- Forecast demand\\n- Track inventory turnover\\n\\n### Suppliers\\n- Receive automated purchase orders\\n- Update delivery status\\n- View historical order data\\n\\n### Finance Team\\n- Track inventory valuation\\n- Generate cost reports\\n- Audit trail for all transactions"
        }"""
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client

        test_input = {
            "user_message": "Create requirements for inventory management system serving warehouse staff, managers, suppliers, and finance team"
        }

        result = high_level_requirements_graph.invoke(test_input)

        assert result is not None
        assert "response" in result
        assert "title" in result["response"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
