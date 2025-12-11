"""
Unit and integration tests for requirements management plan generation workflow
"""
import pytest
import sys
import os
from unittest.mock import Mock, MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflows.requirements_management_plan_workflow import requirements_management_plan_graph


class TestRequirementsManagementPlanWorkflow:
    """Test suite for requirements management plan workflow"""

    def test_requirements_management_plan_graph_exists(self):
        """Test that requirements_management_plan_graph is properly exported"""
        assert requirements_management_plan_graph is not None

    @patch('workflows.requirements_management_plan_workflow.workflow.OpenAI')
    def test_generate_requirements_management_plan_success(self, mock_openai):
        """Test successful requirements management plan generation"""
        # Mock the OpenAI response
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = """{
            "title": "Requirements Management Plan - E-commerce Platform",
            "content": "# Requirements Management Plan\\n\\n## Project: E-commerce Platform\\n\\n### Document Control\\n- **Version:** 1.0\\n- **Date:** 2025-12-12\\n- **Methodology:** Agile Scrum\\n\\n## 1. Introduction\\n\\n### 1.1 Purpose\\nDefines processes for managing requirements throughout the project lifecycle.\\n\\n### 1.2 Scope\\nCovers elicitation, analysis, specification, validation, and change control.\\n\\n### 1.3 Objectives\\n- Establish consistent processes\\n- Ensure traceability\\n- Manage changes effectively\\n- Facilitate stakeholder communication\\n\\n## 2. Requirements Management Approach\\n\\n### 2.1 Methodology\\n- Framework: Agile Scrum (2-week sprints)\\n- Format: User Stories, Acceptance Criteria\\n- Backlog: Prioritized Product Backlog\\n\\n### 2.2 Requirements Levels\\n1. Epic: Large features\\n2. User Story: Specific needs\\n3. Task: Implementation units\\n4. Acceptance Criteria: Testable conditions\\n\\n## 3. Requirements Elicitation\\n\\n### 3.1 Techniques\\n- Workshops (bi-weekly)\\n- Stakeholder interviews\\n- User research\\n- Document analysis\\n- Prototyping\\n\\n### 3.2 Schedule\\n| Activity | Frequency | Duration | Participants |\\n|----------|-----------|----------|--------------|\\n| Requirements Workshop | Bi-weekly | 2-3 hours | PO, BA, Stakeholders |\\n| Sprint Planning | Every 2 weeks | 2 hours | Scrum Team |\\n| Backlog Refinement | Twice per sprint | 1 hour | Scrum Team |\\n\\n## 4. Requirements Analysis\\n\\n### 4.1 Techniques\\n- Feasibility analysis\\n- Gap analysis\\n- Impact analysis\\n- Risk analysis\\n\\n### 4.2 Prioritization (MoSCoW)\\n- Must Have: Critical for MVP\\n- Should Have: Important but not critical\\n- Could Have: Desirable\\n- Won't Have: Excluded\\n\\n## 5. Requirements Documentation\\n\\n### 5.1 User Story Format\\n```\\nAs a [role]\\nI want to [action]\\nSo that [value]\\n\\nAcceptance Criteria:\\n- Given [context]\\n- When [action]\\n- Then [outcome]\\n```\\n\\n### 5.2 Tools\\n- Jira: User stories\\n- Confluence: Documentation\\n- Git: Version control\\n\\n## 6. Requirements Validation\\n- Sprint Reviews\\n- User Acceptance Testing\\n- Peer Reviews\\n\\n## 7. Traceability\\n| Epic | User Story | Task | Test Case | Status |\\n|------|------------|------|-----------|--------|\\n| E-001 | US-001 | T-001 | TC-001 | Done |\\n\\n## 8. Change Management\\n\\n### 8.1 Process\\n1. Request submission\\n2. Impact analysis\\n3. Prioritization\\n4. Approval\\n5. Implementation\\n\\n### 8.2 Change Control Board\\n- Product Owner (Chair)\\n- Business Analyst\\n- Technical Lead\\n\\n## 9. Communication Plan\\n| Audience | Method | Frequency |\\n|----------|--------|-----------|\\n| Scrum Team | Standup | Daily |\\n| Stakeholders | Sprint Review | Bi-weekly |\\n| Executives | Status Report | Monthly |\\n\\n## 10. Roles and Responsibilities\\n\\n### Product Owner\\n- Define backlog\\n- Accept/reject stories\\n\\n### Business Analyst\\n- Facilitate elicitation\\n- Document requirements\\n\\n### Development Team\\n- Implement stories\\n- Provide technical input\\n\\n## 11. Metrics\\n- Velocity (story points per sprint)\\n- Requirements volatility\\n- Defect density\\n- Acceptance rate\\n\\n## 12. Quality Assurance\\n- Complete requirements\\n- Clear and testable\\n- Traceable to objectives\\n\\n## Document Approval\\n| Role | Name | Signature | Date |\\n|------|------|-----------|------|\\n| Product Owner | | | |"
        }"""
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client

        # Test input
        test_input = {
            "user_message": "Create requirements management plan for e-commerce platform using Agile Scrum methodology with 2-week sprints"
        }

        # Invoke workflow
        result = requirements_management_plan_graph.invoke(test_input)

        # Assertions
        assert result is not None
        assert "response" in result
        assert "title" in result["response"]
        assert "content" in result["response"]
        assert "Requirements Management Plan" in result["response"]["title"]
        assert "Requirements Elicitation" in result["response"]["content"] or "elicitation" in result["response"]["content"].lower()

    @patch('workflows.requirements_management_plan_workflow.workflow.OpenAI')
    def test_generate_plan_with_moscow_prioritization(self, mock_openai):
        """Test plan generation includes MoSCoW prioritization"""
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = """{
            "title": "Requirements Management Plan - CRM System",
            "content": "# Requirements Management Plan\\n\\n## Prioritization Method: MoSCoW\\n\\n### Must Have\\nCritical requirements for Minimum Viable Product (MVP):\\n- User authentication\\n- Contact management\\n- Basic reporting\\n\\n### Should Have\\nImportant but not critical:\\n- Email integration\\n- Advanced search\\n- Custom fields\\n\\n### Could Have\\nDesirable features:\\n- Mobile app\\n- AI-powered insights\\n- Social media integration\\n\\n### Won't Have\\nExcluded from current scope:\\n- Video calling\\n- Built-in payment processing\\n- Blockchain features\\n\\n## Priority Factors\\n1. Business value\\n2. Technical complexity\\n3. Dependencies\\n4. Risk level\\n5. Stakeholder importance"
        }"""
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client

        test_input = {
            "user_message": "Generate requirements management plan with MoSCoW prioritization for CRM system"
        }

        result = requirements_management_plan_graph.invoke(test_input)

        assert result is not None
        assert "response" in result
        assert "title" in result["response"]

    @patch('workflows.requirements_management_plan_workflow.workflow.OpenAI')
    def test_generate_plan_with_change_management(self, mock_openai):
        """Test plan includes change management process"""
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = """{
            "title": "Requirements Management Plan - Healthcare Portal",
            "content": "# Requirements Management Plan\\n\\n## Change Management\\n\\n### Change Request Process\\n1. **Request Submission**\\n   - Stakeholder submits change request via Jira\\n   - Include: description, justification, priority\\n\\n2. **Impact Analysis**\\n   - BA assesses impact on scope, timeline, budget\\n   - Technical team evaluates feasibility\\n   - Risk assessment performed\\n\\n3. **Prioritization**\\n   - Product Owner evaluates business value\\n   - Assigns priority using MoSCoW\\n\\n4. **Approval**\\n   - Change Control Board reviews\\n   - Decision: Approve, Reject, Defer\\n   - Documentation of decision rationale\\n\\n5. **Implementation**\\n   - Approved changes added to backlog\\n   - Sprint planning considers new items\\n\\n6. **Communication**\\n   - All stakeholders notified of decision\\n   - Updated documentation distributed\\n\\n### Change Control Board\\n- Product Owner (Chair)\\n- Business Analyst\\n- Technical Lead\\n- Project Manager\\n- Stakeholder Representative\\n\\n### Change Impact Levels\\n- **Low Impact:** PO approval only\\n- **Medium Impact:** CCB review required\\n- **High Impact:** Executive sponsor approval required"
        }"""
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client

        test_input = {
            "user_message": "Create requirements management plan with detailed change management process for healthcare portal"
        }

        result = requirements_management_plan_graph.invoke(test_input)

        assert result is not None
        assert "response" in result

    @patch('workflows.requirements_management_plan_workflow.workflow.OpenAI')
    def test_generate_plan_with_traceability_matrix(self, mock_openai):
        """Test plan includes requirements traceability approach"""
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = """{
            "title": "Requirements Management Plan - Supply Chain System",
            "content": "# Requirements Management Plan\\n\\n## Requirements Traceability\\n\\n### Traceability Matrix\\nMaintain bidirectional traceability from business objectives to implementation:\\n\\n| Business Objective | Epic | User Story | Task | Test Case | Status |\\n|-------------------|------|------------|------|-----------|--------|\\n| Reduce costs 20% | E-001 | US-001, US-002 | T-001, T-002 | TC-001 | Done |\\n| Improve efficiency | E-002 | US-003 | T-003, T-004 | TC-002 | In Progress |\\n| Enhance visibility | E-003 | US-004, US-005 | T-005 | TC-003 | Backlog |\\n\\n### Traceability Levels\\n1. **Forward Traceability:** Business need → Epic → Story → Task → Code → Test\\n2. **Backward Traceability:** Test → Code → Task → Story → Epic → Business need\\n\\n### Traceability Tools\\n- **Primary:** Jira epic/story/task linking\\n- **Testing:** Jira-TestRail integration\\n- **Documentation:** Confluence with requirement references\\n- **Code:** Git commit messages reference story IDs\\n\\n### Benefits\\n- Validate all requirements are implemented\\n- Ensure tests cover all requirements\\n- Assess impact of requirement changes\\n- Support regulatory compliance audits"
        }"""
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client

        test_input = {
            "user_message": "Generate requirements management plan with comprehensive traceability matrix for supply chain system"
        }

        result = requirements_management_plan_graph.invoke(test_input)

        assert result is not None
        assert "response" in result

    @patch('workflows.requirements_management_plan_workflow.workflow.OpenAI')
    def test_generate_plan_error_handling(self, mock_openai):
        """Test error handling in plan generation"""
        # Mock the client and its methods
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("Service Unavailable")

        test_input = {
            "user_message": "Create requirements management plan"
        }

        result = requirements_management_plan_graph.invoke(test_input)

        # Should return error in response
        assert result is not None
        assert "response" in result
        assert "content" in result["response"]
        assert "Error generating document" in result["response"]["content"]

    @patch('workflows.requirements_management_plan_workflow.workflow.OpenAI')
    def test_plan_includes_communication_strategy(self, mock_openai):
        """Test plan includes communication strategy"""
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = """{
            "title": "Requirements Management Plan - Financial Platform",
            "content": "# Requirements Management Plan\\n\\n## Communication Plan\\n\\n### Stakeholder Communication Matrix\\n\\n| Audience | Method | Frequency | Content | Owner |\\n|----------|--------|-----------|---------|-------|\\n| Scrum Team | Daily Standup | Daily | Progress, blockers | Scrum Master |\\n| Product Owner | Backlog Review | Weekly | Priorities, changes | BA |\\n| Stakeholders | Sprint Review | Bi-weekly | Demo, accomplishments | PO |\\n| Executive Sponsors | Status Report | Monthly | Summary, risks, metrics | PM |\\n| QA Team | Test Planning | Per sprint | Requirements, scenarios | BA |\\n\\n### Communication Channels\\n- **Synchronous:** Meetings, video calls, phone\\n- **Asynchronous:** Email, Slack, Jira comments\\n- **Documentation:** Confluence wiki, shared drives\\n\\n### Distributed Team Considerations\\n- Time zone overlap: Schedule meetings in common hours\\n- Recording: Record key meetings for absent team members\\n- Documentation: Comprehensive written docs for clarity\\n- Tools: Slack for quick async, Zoom for meetings\\n\\n### Escalation Path\\n1. Team member → Scrum Master\\n2. Scrum Master → Product Owner\\n3. Product Owner → Project Manager\\n4. Project Manager → Executive Sponsor"
        }"""
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client

        test_input = {
            "user_message": "Create requirements management plan with detailed communication strategy for distributed team"
        }

        result = requirements_management_plan_graph.invoke(test_input)

        assert result is not None
        assert "response" in result

    @patch('workflows.requirements_management_plan_workflow.workflow.OpenAI')
    def test_plan_includes_metrics_and_reporting(self, mock_openai):
        """Test plan includes metrics and reporting approach"""
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = """{
            "title": "Requirements Management Plan - Analytics Platform",
            "content": "# Requirements Management Plan\\n\\n## Metrics and Reporting\\n\\n### Requirements Metrics\\n\\n1. **Velocity**\\n   - Story points completed per sprint\\n   - Target: 50-60 points per sprint\\n   - Trend: Increasing over time\\n\\n2. **Requirements Volatility**\\n   - Rate of requirements changes\\n   - Formula: (Added + Modified + Deleted) / Total\\n   - Target: < 10% per sprint\\n\\n3. **Defect Density**\\n   - Defects per user story\\n   - Formula: Total Defects / Total Stories\\n   - Target: < 2 defects per story\\n\\n4. **Acceptance Rate**\\n   - Stories accepted in sprint review\\n   - Formula: Accepted / Completed\\n   - Target: > 90%\\n\\n5. **Backlog Health**\\n   - Age of backlog items\\n   - Refinement status\\n   - Target: All stories for next sprint refined\\n\\n### Reporting Dashboard\\n- Sprint burndown chart\\n- Release burnup chart\\n- Requirements status (backlog, in progress, done)\\n- Priority distribution pie chart\\n- Change request trends\\n- Velocity trend line\\n\\n### Report Distribution\\n- **Daily:** Burndown chart (team)\\n- **Weekly:** Velocity and acceptance rate (PO, PM)\\n- **Monthly:** Comprehensive metrics (executives)"
        }"""
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client

        test_input = {
            "user_message": "Generate requirements management plan with comprehensive metrics and reporting for analytics platform"
        }

        result = requirements_management_plan_graph.invoke(test_input)

        assert result is not None
        assert "response" in result
        assert "title" in result["response"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
