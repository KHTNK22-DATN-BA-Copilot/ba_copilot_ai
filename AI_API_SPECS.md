# AI API Specifications - Document Generation Services

## Overview

This document defines the API specifications for AI-powered document generation services in the BA Copilot AI system. These services generate various business analysis artifacts using LLM APIs.

**Version:** 2.0
**Last Updated:** December 16, 2025
**Repository:** ba_copilot_ai

---

## Unified Request Format

All API endpoints use a **unified request format** (`AIRequest`):

```json
{
  "message": "string",           // Required: User message/prompt describing what to generate
  "content_id": "string | null", // Optional: Content ID for chat history context
  "storage_paths": ["string"]    // Optional: List of file paths in Supabase Storage
}
```

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `message` | string | Yes | The user's prompt/description for document generation |
| `content_id` | string \| null | No | UUID linking to conversation history in database |
| `storage_paths` | string[] \| null | No | Array of file paths in Supabase Storage to extract context from |

### Example Request

```json
{
  "message": "Create a stakeholder register for an E-commerce Platform project involving retail customers, business administrators, and external payment vendors",
  "content_id": "123e4567-e89b-12d3-a456-426614174000",
  "storage_paths": ["uploads/project_brief.pdf", "uploads/team_org_chart.xlsx"]
}
```

### Context Enrichment

The system automatically enriches requests with:
1. **Chat History**: Previous conversation context retrieved via `content_id`
2. **File Content**: Text extracted from files specified in `storage_paths`

This context is passed to the LLM along with the user's message for more accurate and relevant document generation.

---

## Response Pattern

All services in this document follow a **consistent response pattern**:

```json
{
  "type": "string",     // Service identifier (e.g., "stakeholder-register", "business-case")
  "response": {}        // Service-specific response body
}
```

### Response Types

- **Markdown Documents** (`type: "markdown"`): The `response` field contains plain text/markdown content
- **Diagram Documents** (`type: "diagram"`): The `response` field contains mermaid diagram code
- **Mermaid Documents** (`type: "mermaid"`): The `response` field contains mermaid-specific diagrams (ERDs, flowcharts)

---

## Common Response Structures

### Markdown Response

For services returning markdown documents:

```json
{
  "type": "stakeholder-register",  // Document type identifier
  "response": {
    "title": "Stakeholder Register",
    "content": "# Stakeholder Register\n\n## Overview\n..."  // Full markdown content
  }
}
```

### Diagram Response (Mermaid)

For services returning diagrams:

```json
{
  "type": "product-roadmap",  // Document type identifier
  "response": {
    "type": "product-roadmap",
    "detail": "```mermaid\ngraph TD\n  A[Start] --> B[End]\n```"  // Mermaid code
  }
}
```

---

## Authentication

All API endpoints require JWT Bearer token authentication (provided by the main backend repository):

```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

---

# API Endpoints

## 1. Project Initiation Phase

### 1.1 Stakeholder Register Generation

**Endpoint:** `POST /api/v1/generate/stakeholder-register`

**Description:** Generates a comprehensive stakeholder register document identifying all project stakeholders, their roles, interests, and influence levels.

**Request Body:**

```json
{
  "message": "Create a stakeholder register for E-commerce Platform Development project. Building a new online marketplace for retail products. Known stakeholders include John Smith (Product Owner, Product Management), Sarah Johnson (Development Team Lead, Engineering). Project involves multiple departments and external vendors.",
  "content_id": "123e4567-e89b-12d3-a456-426614174000",
  "storage_paths": ["uploads/project_charter.pdf"]
}
```

**Response (200 OK):**

```json
{
  "type": "stakeholder-register",
  "response": {
    "title": "Stakeholder Register - E-commerce Platform Development",
    "content": "# Stakeholder Register\n\n## Project: E-commerce Platform Development\n\n### Document Information\n- **Date:** 2025-12-11\n- **Version:** 1.0\n- **Prepared by:** BA Copilot AI\n\n## Executive Summary\nThis document identifies and analyzes all stakeholders involved in the E-commerce Platform Development project...\n\n## Stakeholder List\n\n### Internal Stakeholders\n\n#### 1. Product Owner - John Smith\n- **Department:** Product Management\n- **Role:** Decision maker and product vision owner\n- **Interest Level:** High\n- **Influence Level:** High\n- **Engagement Strategy:** Weekly status meetings and milestone reviews\n- **Communication Preferences:** Email, Slack, In-person meetings\n- **Key Concerns:** Product-market fit, feature prioritization, launch timeline\n\n#### 2. Development Team Lead - Sarah Johnson\n- **Department:** Engineering\n- **Role:** Technical lead and team coordinator\n- **Interest Level:** High\n- **Influence Level:** Medium-High\n- **Engagement Strategy:** Daily standups, technical reviews\n- **Communication Preferences:** Slack, Jira, Technical documentation\n- **Key Concerns:** Technical feasibility, resource allocation, code quality\n\n### External Stakeholders\n\n#### 3. End Users - Retail Customers\n- **Category:** Primary users\n- **Interest Level:** High\n- **Influence Level:** Medium\n- **Engagement Strategy:** User research, beta testing, feedback surveys\n- **Key Concerns:** User experience, product availability, pricing\n\n#### 4. External Vendors - Payment Gateway Providers\n- **Category:** Technical partners\n- **Interest Level:** Medium\n- **Influence Level:** Medium\n- **Engagement Strategy:** API integration meetings, SLA reviews\n- **Key Concerns:** Integration requirements, transaction volume, security\n\n## Stakeholder Analysis Matrix\n\n| Stakeholder | Power | Interest | Strategy |\n|-------------|-------|----------|----------|\n| Product Owner | High | High | Manage Closely |\n| Development Team Lead | High | High | Manage Closely |\n| End Users | Medium | High | Keep Informed |\n| Payment Vendors | Medium | Medium | Keep Satisfied |\n| Executive Sponsors | High | Medium | Keep Satisfied |\n| Marketing Team | Low | High | Keep Informed |\n\n## Communication Plan\n\n### High-Priority Stakeholders (Weekly Updates)\n- Product Owner\n- Development Team Lead\n- Executive Sponsors\n\n### Medium-Priority Stakeholders (Bi-weekly Updates)\n- Marketing Team\n- QA Team\n- Security Team\n\n### Low-Priority Stakeholders (Monthly Updates)\n- Support Team\n- Training Team\n\n## Engagement Activities\n\n1. **Kick-off Meeting:** Initial stakeholder alignment meeting\n2. **Requirements Workshops:** Collaborative requirement gathering sessions\n3. **Sprint Reviews:** Regular demonstration of completed features\n4. **User Acceptance Testing:** Stakeholder validation of deliverables\n5. **Go-Live Support:** Transition planning and support\n\n## Risk Assessment\n\n- **Conflicting Interests:** Product Owner may prioritize features differently than end users\n- **Communication Gaps:** Multiple departments require coordinated messaging\n- **Decision Delays:** Multiple approval layers may slow down project progress\n\n## Conclusion\n\nEffective stakeholder management is critical for project success. This register should be reviewed and updated throughout the project lifecycle as new stakeholders are identified or stakeholder dynamics change."
  }
}
```

**Example LLM Prompt Pattern:**

```
You are a professional Business Analyst. Create a comprehensive Stakeholder Register document for the following project:

Project Name: {project_name}
Project Context: {project_context}
Known Stakeholders: {known_stakeholders}
Additional Context: {additional_context}

Return the response in JSON format with this structure:
{
  "title": "Stakeholder Register - {project_name}",
  "content": "Complete markdown document with sections:
    1. Document Information
    2. Executive Summary
    3. Stakeholder List (Internal and External)
    4. Stakeholder Analysis Matrix
    5. Communication Plan
    6. Engagement Activities
    7. Risk Assessment
    8. Conclusion"
}

For each stakeholder include: role, department, interest level, influence level, engagement strategy, communication preferences, and key concerns.

Return only JSON, no additional text.
```

---

### 1.2 High-Level Requirements Generation

**Endpoint:** `POST /api/v1/generate/high-level-requirements`

**Description:** Generates high-level business and system requirements document.

**Request Body:**

```json
{
  "message": "Create high-level requirements for E-commerce Platform. Business objectives: Increase online sales by 30%, Improve customer experience, Reduce operational costs. Target users: Retail customers, Business administrators, Customer support agents. Constraints: Budget $500K, Timeline 6 months, Must integrate with existing ERP. Platform must support multi-currency and multiple payment methods.",
  "content_id": "123e4567-e89b-12d3-a456-426614174000",
  "storage_paths": ["uploads/business_requirements.docx"]
}
```

**Response (200 OK):**

```json
{
  "type": "high-level-requirements",
  "response": {
    "title": "High-Level Requirements - E-commerce Platform",
    "content": "# High-Level Requirements Document\n\n## Project: E-commerce Platform\n\n### Document Control\n- **Version:** 1.0\n- **Date:** 2025-12-11\n- **Status:** Draft\n\n## 1. Introduction\n\n### 1.1 Purpose\nThis document outlines the high-level requirements for the E-commerce Platform project. It serves as a foundation for detailed requirements analysis and system design.\n\n### 1.2 Scope\nThe E-commerce Platform will provide an online marketplace for retail products with integrated payment processing, inventory management, and customer relationship management capabilities.\n\n### 1.3 Business Objectives\n- Increase online sales by 30% within the first year\n- Improve customer experience through intuitive interface and personalized recommendations\n- Reduce operational costs by automating order processing and inventory management\n\n## 2. Stakeholder Requirements\n\n### 2.1 Retail Customers\n- Browse and search product catalog\n- Add items to shopping cart\n- Complete secure checkout process\n- Track order status\n- Manage account and preferences\n\n### 2.2 Business Administrators\n- Manage product catalog and inventory\n- Process and fulfill orders\n- Generate sales and analytics reports\n- Configure system settings and business rules\n\n### 2.3 Customer Support Agents\n- Access customer information and order history\n- Process returns and refunds\n- Respond to customer inquiries\n- Escalate complex issues\n\n## 3. Functional Requirements\n\n### 3.1 User Management (FR-UM)\n- **FR-UM-001:** System shall support user registration and authentication\n- **FR-UM-002:** System shall maintain user profiles with personal and shipping information\n- **FR-UM-003:** System shall support role-based access control (Customer, Admin, Support)\n\n### 3.2 Product Catalog (FR-PC)\n- **FR-PC-001:** System shall display product listings with images, descriptions, and pricing\n- **FR-PC-002:** System shall support product search and filtering by category, price, brand\n- **FR-PC-003:** System shall maintain real-time inventory levels\n- **FR-PC-004:** System shall support product recommendations based on browsing history\n\n### 3.3 Shopping Cart & Checkout (FR-SC)\n- **FR-SC-001:** System shall allow users to add/remove items from shopping cart\n- **FR-SC-002:** System shall calculate total cost including taxes and shipping\n- **FR-SC-003:** System shall support multiple payment methods (credit card, PayPal, etc.)\n- **FR-SC-004:** System shall support multi-currency transactions\n- **FR-SC-005:** System shall send order confirmation emails\n\n### 3.4 Order Management (FR-OM)\n- **FR-OM-001:** System shall process and track orders through fulfillment lifecycle\n- **FR-OM-002:** System shall integrate with existing ERP for order processing\n- **FR-OM-003:** System shall support order cancellation and returns\n- **FR-OM-004:** System shall generate shipping labels and tracking information\n\n### 3.5 Reporting & Analytics (FR-RA)\n- **FR-RA-001:** System shall provide sales reports and dashboards\n- **FR-RA-002:** System shall track key performance indicators (conversion rate, average order value)\n- **FR-RA-003:** System shall generate inventory reports\n\n## 4. Non-Functional Requirements\n\n### 4.1 Performance (NFR-P)\n- **NFR-P-001:** Page load time shall not exceed 2 seconds\n- **NFR-P-002:** System shall support 10,000 concurrent users\n- **NFR-P-003:** Checkout process shall complete within 5 seconds\n\n### 4.2 Security (NFR-S)\n- **NFR-S-001:** System shall encrypt sensitive data (passwords, payment information)\n- **NFR-S-002:** System shall comply with PCI-DSS standards\n- **NFR-S-003:** System shall implement secure authentication (OAuth 2.0, JWT)\n\n### 4.3 Usability (NFR-U)\n- **NFR-U-001:** System shall be accessible on desktop, tablet, and mobile devices\n- **NFR-U-002:** System shall support multiple languages\n- **NFR-U-003:** System shall follow WCAG 2.1 accessibility guidelines\n\n### 4.4 Reliability (NFR-R)\n- **NFR-R-001:** System uptime shall be 99.9%\n- **NFR-R-002:** System shall implement automated backup and disaster recovery\n\n## 5. Constraints\n\n### 5.1 Budget\n- Total project budget: $500,000\n- Allocated for development, infrastructure, and third-party integrations\n\n### 5.2 Timeline\n- Project duration: 6 months from kickoff to launch\n- Key milestones: Requirements (1 month), Development (3 months), Testing (1 month), Deployment (1 month)\n\n### 5.3 Technical\n- Must integrate with existing ERP system via REST APIs\n- Must support multi-currency transactions\n- Must be cloud-hosted for scalability\n\n### 5.4 Regulatory\n- Must comply with PCI-DSS for payment processing\n- Must comply with GDPR for customer data protection\n- Must comply with local e-commerce regulations\n\n## 6. Assumptions\n\n- Third-party payment gateway APIs will be available and stable\n- Existing ERP system provides documented REST APIs\n- Sufficient cloud infrastructure resources can be provisioned\n- Product catalog data will be migrated from existing system\n\n## 7. Dependencies\n\n- Payment gateway provider integration\n- ERP system API availability\n- Cloud infrastructure provisioning\n- SSL certificate procurement\n- Domain name and hosting setup\n\n## 8. Acceptance Criteria\n\n- All functional requirements implemented and tested\n- Performance benchmarks met under load testing\n- Security audit passed with no critical vulnerabilities\n- User acceptance testing completed successfully\n- Integration with ERP system validated\n- Multi-currency transactions working correctly\n\n## 9. Next Steps\n\n1. Stakeholder review and approval of high-level requirements\n2. Detailed requirements analysis and documentation\n3. System architecture and design\n4. Development and testing\n5. Deployment and launch\n\n## 10. Approval\n\n| Role | Name | Signature | Date |\n|------|------|-----------|------|\n| Product Owner | | | |\n| Business Analyst | | | |\n| Technical Lead | | | |\n| Project Manager | | | |"
  }
}
```

---

### 1.3 Requirements Management Plan Generation

**Endpoint:** `POST /api/v1/generate/requirements-management-plan`

**Description:** Generates a requirements management plan detailing how requirements will be gathered, documented, analyzed, prioritized, and tracked throughout the project.

**Request Body:**

```json
{
  "message": "Create a requirements management plan for E-commerce Platform. Project phase: Initiation. Team size: 15. Methodology: Agile Scrum. Distributed team across multiple time zones.",
  "content_id": "123e4567-e89b-12d3-a456-426614174000",
  "storage_paths": null
}
```

**Response (200 OK):**

```json
{
  "type": "requirements-management-plan",
  "response": {
    "title": "Requirements Management Plan - E-commerce Platform",
    "content": "# Requirements Management Plan\n\n## Project: E-commerce Platform\n\n### Document Control\n- **Version:** 1.0\n- **Date:** 2025-12-11\n- **Project Phase:** Initiation\n- **Methodology:** Agile Scrum\n\n## 1. Introduction\n\n### 1.1 Purpose\nThis Requirements Management Plan defines the processes, tools, and responsibilities for managing requirements throughout the E-commerce Platform project lifecycle.\n\n### 1.2 Scope\nThis plan covers all aspects of requirements management including elicitation, analysis, specification, validation, and change control.\n\n### 1.3 Objectives\n- Establish consistent requirements processes\n- Ensure requirements traceability\n- Manage requirements changes effectively\n- Facilitate stakeholder communication\n- Support Agile methodology practices\n\n## 2. Requirements Management Approach\n\n### 2.1 Methodology Alignment\n- **Framework:** Agile Scrum with 2-week sprints\n- **Requirements Format:** User Stories, Acceptance Criteria, Definition of Done\n- **Backlog Management:** Product Backlog (prioritized list of user stories)\n- **Refinement:** Backlog grooming sessions twice per sprint\n\n### 2.2 Requirements Levels\n\n1. **Epic:** Large feature or capability (e.g., \"Product Catalog Management\")\n2. **User Story:** Specific user need (e.g., \"As a customer, I want to search products...\")\n3. **Task:** Implementation unit (e.g., \"Create search API endpoint\")\n4. **Acceptance Criteria:** Testable conditions for story completion\n\n## 3. Requirements Elicitation\n\n### 3.1 Elicitation Techniques\n\n#### Workshops\n- **Frequency:** Bi-weekly requirements workshops\n- **Participants:** Product Owner, BA, stakeholders, SMEs\n- **Duration:** 2-3 hours\n- **Output:** Documented requirements, user stories\n\n#### Interviews\n- **Target:** Key stakeholders and subject matter experts\n- **Format:** One-on-one or small group sessions\n- **Duration:** 1-2 hours per session\n- **Documentation:** Interview notes, requirements draft\n\n#### User Research\n- **Methods:** Surveys, user testing, analytics review\n- **Participants:** End users, customer focus groups\n- **Output:** User personas, journey maps, pain points\n\n#### Document Analysis\n- **Sources:** Existing system documentation, business process documents\n- **Activities:** Review, extract, and document relevant requirements\n\n#### Prototyping\n- **Type:** Wireframes, mockups, interactive prototypes\n- **Tool:** Figma, Adobe XD, or similar\n- **Purpose:** Visualize requirements, gather feedback\n\n### 3.2 Elicitation Schedule\n\n| Activity | Frequency | Duration | Participants |\n|----------|-----------|----------|---------------|\n| Requirements Workshop | Bi-weekly | 2-3 hours | PO, BA, Stakeholders |\n| Stakeholder Interviews | As needed | 1-2 hours | BA, Stakeholder |\n| Sprint Planning | Every 2 weeks | 2 hours | Scrum Team |\n| Backlog Refinement | Twice per sprint | 1 hour | Scrum Team |\n| Sprint Review | End of sprint | 1-2 hours | Team, Stakeholders |\n\n## 4. Requirements Analysis\n\n### 4.1 Analysis Techniques\n- **Feasibility Analysis:** Assess technical, operational, and economic viability\n- **Gap Analysis:** Compare current state vs. desired state\n- **Impact Analysis:** Evaluate effects of requirements on system and processes\n- **Risk Analysis:** Identify requirements-related risks\n- **Dependency Analysis:** Map dependencies between requirements\n\n### 4.2 Requirements Prioritization\n\n#### MoSCoW Method\n- **Must Have:** Critical requirements for MVP\n- **Should Have:** Important but not critical\n- **Could Have:** Desirable but not necessary\n- **Won't Have:** Excluded from current scope\n\n#### Priority Factors\n1. Business value\n2. Technical complexity\n3. Dependencies\n4. Risk level\n5. Stakeholder importance\n\n## 5. Requirements Documentation\n\n### 5.1 Documentation Standards\n\n#### User Story Format\n```\nAs a [user role]\nI want to [action]\nSo that [business value]\n\nAcceptance Criteria:\n- Given [context]\n- When [action]\n- Then [expected outcome]\n\nDefinition of Done:\n- Code implemented and reviewed\n- Unit tests written and passing\n- Integration tests passing\n- Documentation updated\n- Accepted by Product Owner\n```\n\n### 5.2 Documentation Tools\n- **Primary Tool:** Jira (user stories, epics, tasks)\n- **Collaboration:** Confluence (detailed specifications, diagrams)\n- **Version Control:** Git (technical documentation)\n- **Communication:** Slack (team discussions), Email (formal communications)\n\n### 5.3 Requirements Attributes\n\nEach requirement shall include:\n- **ID:** Unique identifier (e.g., US-001)\n- **Title:** Brief description\n- **Description:** Detailed user story\n- **Priority:** MoSCoW classification\n- **Status:** Backlog, In Progress, Done, Blocked\n- **Sprint:** Assigned sprint number\n- **Estimation:** Story points\n- **Acceptance Criteria:** Testable conditions\n- **Dependencies:** Related requirements\n- **Stakeholder:** Requesting party\n\n## 6. Requirements Validation\n\n### 6.1 Validation Techniques\n\n#### Sprint Review\n- **Frequency:** End of each sprint\n- **Purpose:** Demo completed stories to stakeholders\n- **Outcome:** Accept/reject stories based on acceptance criteria\n\n#### User Acceptance Testing (UAT)\n- **Phase:** Before production release\n- **Participants:** End users, Product Owner\n- **Criteria:** All acceptance criteria met\n\n#### Peer Review\n- **Frequency:** Continuous during refinement\n- **Reviewers:** Team members, BA, technical lead\n- **Focus:** Clarity, completeness, testability\n\n### 6.2 Acceptance Criteria Checklist\n- [ ] Requirement is clear and unambiguous\n- [ ] Acceptance criteria are testable\n- [ ] Dependencies are identified\n- [ ] Non-functional requirements specified\n- [ ] Stakeholder approval obtained\n\n## 7. Requirements Traceability\n\n### 7.1 Traceability Matrix\n\nMaintain traceability from business objectives to implementation:\n\n| Epic | User Story | Task | Test Case | Status |\n|------|------------|------|-----------|--------|\n| E-001 | US-001 | T-001, T-002 | TC-001 | Done |\n| E-001 | US-002 | T-003 | TC-002 | In Progress |\n\n### 7.2 Traceability Tool\n- **Primary:** Jira linking (epic → story → task)\n- **Testing:** Link user stories to test cases\n- **Documentation:** Reference requirements in technical docs\n\n## 8. Requirements Change Management\n\n### 8.1 Change Request Process\n\n1. **Request Submission:** Stakeholder submits change request\n2. **Impact Analysis:** BA assesses impact on scope, timeline, budget\n3. **Prioritization:** Product Owner evaluates and prioritizes\n4. **Approval:** Change Control Board reviews and approves/rejects\n5. **Implementation:** Approved changes added to backlog\n6. **Communication:** Stakeholders notified of decision\n\n### 8.2 Change Control Board\n- Product Owner (Chair)\n- Business Analyst\n- Technical Lead\n- Project Manager\n- Key Stakeholder Representative\n\n### 8.3 Change Criteria\n- **Low Impact:** Product Owner approval only\n- **Medium Impact:** CCB review, documented decision\n- **High Impact:** Executive sponsor approval required\n\n## 9. Communication Plan\n\n### 9.1 Requirements Communication\n\n| Audience | Method | Frequency | Content |\n|----------|--------|-----------|----------|\n| Scrum Team | Daily Standup | Daily | Status updates |\n| Stakeholders | Sprint Review | Bi-weekly | Demo, progress |\n| Product Owner | Backlog Review | Weekly | Priorities, changes |\n| Executive Sponsors | Status Report | Monthly | Summary, risks |\n\n### 9.2 Distributed Team Considerations\n- **Time Zones:** Schedule meetings in overlapping hours\n- **Tools:** Slack for async communication, Zoom for meetings\n- **Documentation:** Comprehensive written documentation for clarity\n- **Recording:** Record key meetings for team members in different zones\n\n## 10. Roles and Responsibilities\n\n### 10.1 Product Owner\n- Define and prioritize product backlog\n- Accept/reject completed user stories\n- Make final decisions on requirements changes\n- Represent stakeholder interests\n\n### 10.2 Business Analyst\n- Facilitate requirements elicitation sessions\n- Document and analyze requirements\n- Maintain requirements traceability\n- Support change impact analysis\n\n### 10.3 Scrum Master\n- Facilitate sprint planning and reviews\n- Remove impediments to requirements delivery\n- Coach team on Agile practices\n\n### 10.4 Development Team\n- Participate in refinement and estimation\n- Implement user stories\n- Provide technical input on feasibility\n\n### 10.5 Stakeholders\n- Provide input during elicitation\n- Review and validate requirements\n- Participate in sprint reviews\n\n## 11. Tools and Techniques\n\n### 11.1 Requirements Management Tools\n- **Jira:** User story management, sprint planning\n- **Confluence:** Documentation, specifications\n- **Figma:** Wireframes, prototypes\n- **Miro:** Collaborative workshops, brainstorming\n- **Excel/Google Sheets:** Traceability matrix, tracking\n\n### 11.2 Modeling Techniques\n- User story mapping\n- Process flow diagrams\n- Entity relationship diagrams\n- Use case diagrams\n- Wireframes and mockups\n\n## 12. Metrics and Reporting\n\n### 12.1 Requirements Metrics\n- **Velocity:** Story points completed per sprint\n- **Requirements Volatility:** Rate of requirements changes\n- **Defect Density:** Defects per user story\n- **Acceptance Rate:** Stories accepted in sprint review\n- **Backlog Health:** Age of stories, refinement status\n\n### 12.2 Reporting Dashboard\n- Sprint burndown chart\n- Release burnup chart\n- Requirements status (backlog, in progress, done)\n- Priority distribution\n- Change request trends\n\n## 13. Quality Assurance\n\n### 13.1 Requirements Quality Criteria\n- **Complete:** All necessary information included\n- **Consistent:** No conflicts with other requirements\n- **Clear:** Unambiguous, easy to understand\n- **Testable:** Can be validated through testing\n- **Traceable:** Linked to business objectives\n- **Feasible:** Technically and operationally achievable\n\n### 13.2 Review Process\n- Peer review of all user stories before sprint planning\n- BA sign-off on requirements quality\n- Product Owner approval of acceptance criteria\n\n## 14. Training and Support\n\n- Team training on Agile requirements practices\n- Tool training (Jira, Confluence)\n- Requirements writing workshops\n- BA available for consultation during sprints\n\n## 15. Appendices\n\n### Appendix A: User Story Template\n### Appendix B: Requirements Change Request Form\n### Appendix C: Traceability Matrix Template\n### Appendix D: Glossary of Terms\n\n---\n\n## Document Approval\n\n| Role | Name | Signature | Date |\n|------|------|-----------|------|\n| Product Owner | | | |\n| Business Analyst | | | |\n| Project Manager | | | |\n| Scrum Master | | | |"
  }
}
```

---

## 2. Business Planning Phase

### 2.1 Business Case Document Generation

**Endpoint:** `POST /api/v1/generate/business-case`

**Description:** Generates a comprehensive business case document justifying the project investment with cost-benefit analysis, ROI projections, and strategic alignment.

**Request Body:**

```json
{
  "message": "Create a business case for E-commerce Platform. Problem: Current manual ordering process is inefficient and limiting business growth. Solution: Develop automated e-commerce platform with integrated payment and inventory management. Investment: $500,000. Expected benefits: 30% increase in sales revenue, 40% reduction in order processing time, Improved customer satisfaction. Timeline: 6 months. Strategic alignment: Digital transformation initiative, Customer experience improvement.",
  "content_id": "123e4567-e89b-12d3-a456-426614174000",
  "storage_paths": ["uploads/financial_projections.xlsx", "uploads/market_analysis.pdf"]
}
```

**Response (200 OK):**

```json
{
  "type": "business-case",
  "response": {
    "title": "Business Case - E-commerce Platform",
    "content": "# Business Case Document\n\n## Project: E-commerce Platform\n\n### Executive Summary\n\nThis business case proposes the development of an automated e-commerce platform to address inefficiencies in the current manual ordering process. The project requires an investment of $500,000 and is expected to deliver a 30% increase in sales revenue and 40% reduction in order processing time within the first year.\n\n**Recommendation:** Approve and proceed with project implementation.\n\n### Document Control\n- **Version:** 1.0\n- **Date:** 2025-12-11\n- **Project Timeline:** 6 months\n\n---\n\n## 1. Business Problem\n\n### 1.1 Problem Statement\nThe current manual ordering process is inefficient and limiting business growth. Key issues include:\n\n- **Process Inefficiency:** Manual order entry requires significant staff time and is error-prone\n- **Limited Scalability:** Current system cannot handle increasing order volumes\n- **Customer Experience:** Customers lack self-service capabilities and real-time order visibility\n- **Revenue Limitations:** Manual process constrains ability to capture additional sales opportunities\n- **Competitive Disadvantage:** Competitors with modern e-commerce platforms are gaining market share\n\n### 1.2 Impact Analysis\n\n**Current State Challenges:**\n- Average order processing time: 45 minutes per order\n- Order error rate: 8-10%\n- Customer service calls: 500+ per week related to order status\n- Lost sales opportunities: ~15% due to limited ordering hours and channel access\n- Staff overtime: 20 hours per week to handle backlog\n\n**Business Impact:**\n- Annual revenue loss: ~$750,000 (15% of potential sales)\n- Additional operational costs: $150,000 annually (overtime, error correction)\n- Customer satisfaction scores declining (current: 3.2/5)\n- Staff burnout and high turnover in order processing team\n\n---\n\n## 2. Proposed Solution\n\n### 2.1 Solution Overview\nDevelop an automated e-commerce platform with integrated payment processing and inventory management capabilities.\n\n**Key Components:**\n- Customer-facing web application with product catalog and shopping cart\n- Secure payment gateway integration supporting multiple payment methods\n- Real-time inventory management system\n- Order management and fulfillment workflow automation\n- Customer portal for order tracking and account management\n- Admin dashboard for business operations and analytics\n- Integration with existing ERP system\n\n### 2.2 Solution Features\n\n**Customer Features:**\n- 24/7 online product browsing and ordering\n- Real-time product availability and pricing\n- Multiple payment options (credit card, PayPal, etc.)\n- Order history and tracking\n- Personalized product recommendations\n- Multi-device access (desktop, tablet, mobile)\n\n**Business Features:**\n- Automated order processing workflow\n- Real-time inventory synchronization\n- Sales analytics and reporting\n- Customer relationship management\n- Marketing campaign management\n- Integration with existing systems\n\n### 2.3 Technology Approach\n- Cloud-hosted SaaS architecture for scalability\n- Modern web technologies (React, Node.js, PostgreSQL)\n- API-first design for integration flexibility\n- Responsive design for multi-device support\n- Industry-standard security protocols (PCI-DSS, OAuth 2.0)\n\n---\n\n## 3. Cost Analysis\n\n### 3.1 Initial Investment\n\n| Category | Description | Cost |\n|----------|-------------|------|\n| **Development** | Software development team (6 months) | $300,000 |\n| **Infrastructure** | Cloud hosting setup, domains, SSL | $20,000 |\n| **Integrations** | Payment gateway, ERP integration | $50,000 |\n| **Design & UX** | UI/UX design, branding | $30,000 |\n| **Testing & QA** | Quality assurance, security audit | $40,000 |\n| **Project Management** | PM and BA resources | $40,000 |\n| **Training** | Staff training and documentation | $20,000 |\n| **Total Initial Investment** | | **$500,000** |\n\n### 3.2 Ongoing Costs (Annual)\n\n| Category | Description | Annual Cost |\n|----------|-------------|-------------|\n| **Hosting** | Cloud infrastructure (AWS/Azure) | $24,000 |\n| **Licenses** | Third-party services, tools | $12,000 |\n| **Maintenance** | Bug fixes, updates, support | $60,000 |\n| **Payment Processing** | Transaction fees (estimated) | $30,000 |\n| **Support** | Customer support enhancements | $20,000 |\n| **Total Annual Cost** | | **$146,000** |\n\n---\n\n## 4. Benefits Analysis\n\n### 4.1 Quantifiable Benefits\n\n#### Revenue Increase\n- **30% sales growth** from expanded access and improved conversion\n- Current annual revenue: $5,000,000\n- Projected increase: $1,500,000 annually\n\n#### Operational Efficiency\n- **40% reduction in order processing time**\n  - Current: 45 minutes per order\n  - Future: 27 minutes per order (automated workflow)\n  - Staff time saved: 1,500 hours annually\n  - Cost savings: $75,000 annually (at $50/hour loaded cost)\n\n#### Error Reduction\n- **Reduce order errors from 10% to 2%**\n  - Current error correction cost: $80,000 annually\n  - Projected savings: $64,000 annually\n\n#### Customer Service Efficiency\n- **50% reduction in order status inquiries**\n  - Self-service order tracking reduces support calls\n  - Support cost savings: $40,000 annually\n\n### 4.2 Intangible Benefits\n\n- **Improved Customer Satisfaction:** Modern shopping experience, 24/7 access\n- **Enhanced Brand Image:** Professional online presence, competitive positioning\n- **Market Expansion:** Ability to reach new customer segments and geographic markets\n- **Data-Driven Decisions:** Analytics and insights for business optimization\n- **Staff Morale:** Elimination of repetitive manual tasks, focus on value-added activities\n- **Scalability:** Platform can grow with business without linear cost increase\n- **Innovation Platform:** Foundation for future digital initiatives (mobile app, AI recommendations)\n\n### 4.3 Total Benefits Summary (5-Year)\n\n| Year | Revenue Increase | Cost Savings | Total Benefits |\n|------|------------------|--------------|----------------|\n| Year 1 | $1,500,000 | $179,000 | $1,679,000 |\n| Year 2 | $1,650,000 | $179,000 | $1,829,000 |\n| Year 3 | $1,815,000 | $179,000 | $1,994,000 |\n| Year 4 | $1,997,000 | $179,000 | $2,176,000 |\n| Year 5 | $2,197,000 | $179,000 | $2,376,000 |\n| **Total** | **$9,159,000** | **$895,000** | **$10,054,000** |\n\n---\n\n## 5. Financial Analysis\n\n### 5.1 Return on Investment (ROI)\n\n**5-Year ROI Calculation:**\n- Total Benefits (5 years): $10,054,000\n- Total Costs (initial + 5 years operation): $1,230,000\n- Net Benefit: $8,824,000\n- **ROI: 717%**\n\n**Formula:** ROI = (Net Benefit / Total Investment) × 100\n\n### 5.2 Payback Period\n\n- Initial Investment: $500,000\n- Year 1 Net Benefit: $1,679,000 - $146,000 = $1,533,000\n- **Payback Period: ~4 months**\n\nThe initial investment will be recovered in approximately 4 months of operation.\n\n### 5.3 Net Present Value (NPV)\n\n**Assumptions:**\n- Discount rate: 10%\n- Project lifespan: 5 years\n\n| Year | Cash Flow | Discount Factor | Present Value |\n|------|-----------|-----------------|---------------|\n| 0 | -$500,000 | 1.000 | -$500,000 |\n| 1 | $1,533,000 | 0.909 | $1,393,497 |\n| 2 | $1,683,000 | 0.826 | $1,390,158 |\n| 3 | $1,848,000 | 0.751 | $1,387,848 |\n| 4 | $2,030,000 | 0.683 | $1,386,490 |\n| 5 | $2,230,000 | 0.621 | $1,384,830 |\n| **NPV** | | | **$6,442,823** |\n\n**Interpretation:** Positive NPV of $6.4M indicates the project creates significant value.\n\n### 5.4 Break-Even Analysis\n\n- Monthly fixed costs (ongoing): $12,167\n- Variable costs per transaction: ~$0.50 (payment processing)\n- Average order value: $75\n- Contribution margin: $74.50 per order\n\n**Break-even point:** ~163 orders per month to cover ongoing costs\n\n**Current volume:** ~2,000 orders per month\n**Projected volume:** ~2,600 orders per month\n\n---\n\n## 6. Risk Assessment\n\n### 6.1 Identified Risks\n\n| Risk | Probability | Impact | Mitigation Strategy |\n|------|-------------|--------|---------------------|\n| **Project delays** | Medium | High | Agile methodology, experienced team, clear milestones |\n| **Budget overrun** | Medium | Medium | Detailed planning, contingency reserve (10%) |\n| **Technical challenges** | Low | Medium | Proven technology stack, experienced architects |\n| **Integration issues** | Medium | Medium | Early API testing, dedicated integration phase |\n| **User adoption** | Low | High | Change management, training, intuitive UX |\n| **Security breach** | Low | High | Security audit, PCI-DSS compliance, penetration testing |\n| **Vendor dependency** | Low | Medium | Multiple payment gateway options, cloud vendor flexibility |\n| **Scope creep** | Medium | Medium | Change control process, prioritized backlog |\n\n### 6.2 Risk Mitigation Budget\n\n- Contingency reserve: $50,000 (10% of initial investment)\n- Allocated for addressing unforeseen challenges\n\n---\n\n## 7. Strategic Alignment\n\n### 7.1 Organizational Strategy\n\nThis project aligns with key strategic initiatives:\n\n**Digital Transformation Initiative:**\n- Modernizes customer-facing operations\n- Enables data-driven decision making\n- Builds foundation for future digital services\n\n**Customer Experience Improvement:**\n- Provides 24/7 self-service capabilities\n- Improves order accuracy and fulfillment speed\n- Enables personalized shopping experiences\n\n### 7.2 Competitive Positioning\n\n- **Market Requirement:** E-commerce is now table stakes in retail industry\n- **Competitive Parity:** Matches capabilities of primary competitors\n- **Differentiation Opportunity:** Platform enables rapid feature innovation\n\n### 7.3 Future Opportunities\n\nThe platform creates foundation for:\n- Mobile application development\n- AI-powered product recommendations\n- International market expansion\n- B2B wholesale portal\n- Subscription services\n- Omnichannel integration (online + physical stores)\n\n---\n\n## 8. Implementation Approach\n\n### 8.1 Project Timeline\n\n**Total Duration:** 6 months\n\n| Phase | Duration | Key Activities |\n|-------|----------|----------------|\n| **Requirements** | 1 month | Stakeholder interviews, requirements documentation |\n| **Design** | 1 month | Architecture design, UI/UX design, prototyping |\n| **Development** | 3 months | Iterative development in 2-week sprints |\n| **Testing** | 0.5 month | QA, security audit, performance testing |\n| **Deployment** | 0.5 month | Production deployment, training, go-live |\n\n### 8.2 Success Criteria\n\n- System launched within 6-month timeline and $500K budget\n- All critical features implemented and operational\n- Performance benchmarks met (page load, concurrent users)\n- Security audit passed with no critical vulnerabilities\n- User acceptance testing completed successfully\n- Staff trained and proficient in system operation\n\n---\n\n## 9. Alternatives Considered\n\n### 9.1 Option 1: Off-the-Shelf E-commerce Platform (e.g., Shopify, Magento)\n\n**Pros:**\n- Faster time to market (2-3 months)\n- Lower initial cost ($50K-$100K)\n- Proven, stable platform\n\n**Cons:**\n- Limited customization for unique business processes\n- ERP integration challenges\n- Higher ongoing costs ($3K-$10K/month)\n- Vendor lock-in\n- Less control over features and roadmap\n\n**Decision:** Not selected due to integration requirements and long-term cost\n\n### 9.2 Option 2: Enhance Existing System\n\n**Pros:**\n- Lowest initial cost ($100K-$200K)\n- Familiar to staff\n\n**Cons:**\n- Limited scalability of legacy architecture\n- Poor user experience difficult to improve\n- Technical debt accumulation\n- May not achieve desired business outcomes\n\n**Decision:** Not selected due to limited potential and poor long-term value\n\n### 9.3 Option 3: Do Nothing\n\n**Pros:**\n- No investment required\n\n**Cons:**\n- Continued operational inefficiency\n- Loss of competitive position\n- Missed revenue opportunities ($750K+ annually)\n- Staff frustration and turnover\n- Customer satisfaction decline\n\n**Decision:** Not viable due to significant opportunity cost and competitive risk\n\n---\n\n## 10. Recommendation\n\n**Recommendation:** **APPROVE** the E-commerce Platform development project\n\n### 10.1 Justification\n\n1. **Strong Financial Case:** 717% ROI, 4-month payback period, $6.4M NPV\n2. **Strategic Imperative:** Essential for digital transformation and competitive positioning\n3. **Manageable Risk:** Risks are identifiable and mitigatable with proper planning\n4. **Clear Benefits:** Quantifiable revenue increase and cost savings\n5. **Customer Value:** Significant improvement in customer experience and satisfaction\n\n### 10.2 Next Steps\n\n1. **Immediate:**\n   - Obtain executive approval and funding authorization\n   - Assign project sponsor and project manager\n   - Assemble project team\n\n2. **Month 1:**\n   - Conduct project kickoff\n   - Begin requirements gathering\n   - Finalize vendor selections (payment gateway, hosting)\n\n3. **Month 2-6:**\n   - Execute project per implementation plan\n   - Regular steering committee updates\n   - Go-live preparation\n\n---\n\n## 11. Approval\n\n| Role | Name | Recommendation | Signature | Date |\n|------|------|----------------|-----------|------|\n| **Business Analyst** | | Approve | | |\n| **Finance Director** | | Approve | | |\n| **IT Director** | | Approve | | |\n| **Executive Sponsor** | | Approve | | |\n| **CEO** | | [Decision] | | |\n\n---\n\n## Appendices\n\n### Appendix A: Detailed Cost Breakdown\n### Appendix B: Market Research and Competitor Analysis\n### Appendix C: Technical Architecture Overview\n### Appendix D: Stakeholder Analysis\n### Appendix E: Risk Register"
  }
}
```

---



### 2.2 Scope Statement Document Generation

**Endpoint:** `POST /api/v1/generate/scope-statement`

**Description:** Generates a detailed project scope statement defining what is included and excluded from the project.

**Request Body:**

```json
{
  "message": "Create a scope statement for E-commerce Platform. Define in-scope: product catalog, shopping cart, payment processing, user management. Out-of-scope: mobile app, international shipping. Timeline: 6 months. Budget: $500K.",
  "content_id": "123e4567-e89b-12d3-a456-426614174000",
  "storage_paths": ["uploads/project_requirements.pdf"]
}
```

**Response:** Similar structure to business case with comprehensive scope definition including in-scope, out-of-scope, deliverables, constraints, assumptions, dependencies, and approval sections.

---

### 2.3 Product Roadmap Document Generation

**Endpoint:** `POST /api/v1/generate/product-roadmap`

**Description:** Generates a product roadmap diagram showing timeline and milestones.

**Request Body:**

```json
{
  "message": "Create a product roadmap for E-commerce Platform. Phases: Planning (Jan), Design (Feb), Development (Mar-May), Testing (Jun), Deployment (Jul). Include milestones for MVP, beta release, and production launch.",
  "content_id": "123e4567-e89b-12d3-a456-426614174000",
  "storage_paths": null
}
```

**Response Type:** Diagram (Mermaid gantt chart)

---

## 3. Feasibility & Risk Analysis Phase

### 3.1 Feasibility Study Report Generation

**Endpoint:** `POST /api/v1/generate/feasibility-study`

**Description:** Analyzes technical, operational, economic, schedule, and legal feasibility.

### 3.2 Cost-Benefit Analysis Document Generation

**Endpoint:** `POST /api/v1/generate/cost-benefit-analysis`

**Description:** Detailed financial analysis with ROI, NPV, payback period calculations.

### 3.3 Risk Register Document Generation

**Endpoint:** `POST /api/v1/generate/risk-register`

**Description:** Comprehensive risk identification, assessment, and mitigation planning.

### 3.4 Compliance Document Generation

**Endpoint:** `POST /api/v1/generate/compliance`

**Description:** Legal and regulatory compliance requirements documentation.

---

## 4. High-Level Design Phase

### 4.1 System Architecture Diagram Generation

**Endpoint:** `POST /api/v1/generate/hld-arch`

**Description:** High-level system architecture diagram (Mermaid).

**Response Type:** Diagram

### 4.2 Cloud Infrastructure Setup Generation

**Endpoint:** `POST /api/v1/generate/hld-cloud`

**Description:** Cloud infrastructure setup documentation.

### 4.3 Tech Stack Selection Generation

**Endpoint:** `POST /api/v1/generate/hld-tech`

**Description:** Technology stack selection with justification.

---

## 5. Low-Level Design Phase

### 5.1 Architecture Diagrams Generation

**Endpoint:** `POST /api/v1/generate/lld-arch`

**Description:** Detailed architecture diagrams (component, deployment).

**Response Type:** Diagram (Mermaid)

### 5.2 Database Schemas Generation

**Endpoint:** `POST /api/v1/generate/lld-db`

**Description:** Database entity relationship diagrams and schema definitions.

**Response Type:** Mermaid ERD

**Example Response:**

```json
{
  "type": "lld-db",
  "response": {
    "type": "database-schema",
    "detail": "```mermaid\nerDiagram\n  CUSTOMER ||--o{ ORDER : places\n  CUSTOMER {\n    uuid id PK\n    string email\n    string name\n  }\n  ORDER ||--|{ ORDER_ITEM : contains\n  ORDER {\n    uuid id PK\n    uuid customer_id FK\n    decimal total\n    timestamp created_at\n  }\n```"
  }
}
```

### 5.3 API Specifications Generation

**Endpoint:** `POST /api/v1/generate/lld-api`

**Description:** Detailed API endpoint specifications (OpenAPI/Swagger format).

### 5.4 Pseudocode Generation

**Endpoint:** `POST /api/v1/generate/lld-pseudo`

**Description:** Algorithm pseudocode and logic flow documentation.

---

## 6. UI/UX Design Phase

### 6.1 Wireframes Generation

**Endpoint:** `POST /api/v1/generate/uiux-wireframe`

**Description:** UI wireframes with layout and component specifications.

**Note:** Uses existing wireframe workflow patterns.

### 6.2 Mockups Generation

**Endpoint:** `POST /api/v1/generate/uiux-mockup`

**Description:** High-fidelity UI mockups with design specifications.

### 6.3 Prototypes Generation

**Endpoint:** `POST /api/v1/generate/uiux-prototype`

**Description:** Interactive prototype specifications and user flow documentation.

---

## 7. Testing & Quality Assurance Phase

### 7.1 Requirements Traceability Matrix (RTM) Generation

**Endpoint:** `POST /api/v1/generate/rtm`

**Description:** Maps requirements to tests and implementation status.

**Request Body:**

```json
{
  "message": "Create a requirements traceability matrix for E-commerce Platform. Requirements: FR-001 (User registration, High priority), FR-002 (Product search, High priority). Test cases: TC-001 (FR-001, Passed), TC-002 (FR-002, Pending).",
  "content_id": "123e4567-e89b-12d3-a456-426614174000",
  "storage_paths": ["uploads/requirements_spec.xlsx", "uploads/test_results.csv"]
}
```

**Response:**

```json
{
  "type": "rtm",
  "response": {
    "title": "Requirements Traceability Matrix - E-commerce Platform",
    "content": "# Requirements Traceability Matrix\n\n## Overview\n\nThis matrix tracks the relationship between requirements, design, implementation, and testing.\n\n## Traceability Matrix\n\n| Req ID | Requirement | Priority | Design Doc | Implementation | Test Cases | Status |\n|--------|-------------|----------|------------|----------------|------------|--------|\n| FR-001 | User registration | High | DD-001 | Implemented | TC-001 |  Passed |\n| FR-002 | Product search | High | DD-002 | In Progress | TC-002 | Pending |\n...\n\n## Coverage Analysis\n\n- Total Requirements: 45\n- Implemented: 38 (84%)\n- Tested: 35 (78%)\n- Passed: 33 (73%)\n\n## Gaps and Action Items\n\n1. FR-010: Missing test coverage - Assign to QA team\n2. FR-015: Implementation pending - Scheduled for Sprint 8\n..."
  }
}
```

---

## 8. Common Request/Response Patterns

### 8.1 Unified Request Format (AIRequest)

All endpoints use the same request format:

```json
{
  "message": "string",           // Required: Description of what to generate
  "content_id": "string | null", // Optional: Content ID for chat history
  "storage_paths": ["string"]    // Optional: File paths in Supabase Storage
}
```

### 8.2 Standard Markdown Document Response

```json
{
  "type": "document-type-id",
  "response": {
    "title": "Document Title",
    "content": "# Full Markdown Content\n\n..."
  }
}
```

### 8.3 Standard Diagram Response

```json
{
  "type": "diagram-type-id",
  "response": {
    "type": "diagram-type",
    "detail": "```mermaid\n...\n```"
  }
}
```

### 8.4 HTML/CSS Wireframe Response

```json
{
  "type": "wireframe",
  "response": {
    "content": "<html>...</html>"
  }
}
```

---

## 9. LLM Prompt Guidelines

### 9.1 Prompt Structure with Context Enrichment

All prompts now include context enrichment from chat history and uploaded files:

```
{context_from_chat_history}

{extracted_content_from_uploaded_files}

You are a professional Business Analyst. Create a comprehensive {DOCUMENT_TYPE} for:

{user_message}

Return JSON format:
{
  "title": "{document_title}",
  "content": "Complete markdown with sections: {section_list}"
}

Include: {specific_requirements}
Format: Professional BA documentation standards
Return only JSON, no additional text.
```

### 9.2 Prompt Structure for Diagrams

```
{context_from_chat_history}

{extracted_content_from_uploaded_files}

Create a detailed {DIAGRAM_TYPE} in Mermaid markdown format for:

{user_message}

Include:
- {diagram_specific_elements}

IMPORTANT: Return ONLY the Mermaid code block starting with ```mermaid and ending with ```
No explanatory text before or after.
```

### 9.3 Context Sources

The system enriches prompts with context from two sources:

1. **Chat History** (`content_id`):
   - Retrieved from database via `get_chat_history` node
   - Provides conversation continuity
   - Format: "Context from previous conversation:\n{chat_context}"

2. **Uploaded Files** (`storage_paths`):
   - Retrieved from Supabase Storage via `get_content_file` node
   - Extracts text from PDF, DOCX, TXT, CSV, XLSX files
   - Format: "Extracted content from uploaded files:\n{extracted_text}"

---

## 10. Error Handling

All endpoints follow standard error response format:

```json
{
  "type": "error",
  "response": {
    "error_code": "string",
    "message": "string",
    "details": "string"
  }
}
```

**Common Error Codes:**
- `INVALID_INPUT`: Request validation failed
- `LLM_ERROR`: LLM API call failed
- `TIMEOUT`: Request processing timeout
- `RATE_LIMIT`: Rate limit exceeded

---

## 11. Implementation Notes

### 11.1 Workflow Integration

Each document type is implemented as a LangGraph workflow in `ba_copilot_ai/workflows/` following this standard pattern:

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, List
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client, MODEL

class DocumentState(TypedDict):
    user_message: str
    response: dict
    content_id: Optional[str]
    storage_paths: Optional[List]
    extracted_text: Optional[str]
    chat_context: Optional[str]

def generate_document(state: DocumentState) -> DocumentState:
    model_client = get_model_client()

    # Build context from chat history and uploaded files
    user_message = state.get('user_message', '')
    extracted_text = state.get('extracted_text', '')
    chat_context = state.get('chat_context', '')

    context_parts = []
    if chat_context:
        context_parts.append(f"Context from previous conversation:\n{chat_context}\n")
    if extracted_text:
        context_parts.append(f"Extracted content from uploaded files:\n{extracted_text}\n")

    context_str = "\n".join(context_parts)

    prompt = f"""
    {context_str}

    You are a professional Business Analyst. Create a comprehensive document for:

    {user_message}

    Return JSON format with title and content fields.
    """

    completion = model_client.chat_completion(
        messages=[{"role": "user", "content": prompt}],
        model=MODEL
    )

    # Process response and return
    return {"response": {...}}

# Build workflow with standard node sequence
workflow = StateGraph(DocumentState)
workflow.add_node("get_content_file", get_content_file)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_document", generate_document)

workflow.set_entry_point("get_content_file")
workflow.add_edge("get_content_file", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_document")
workflow.add_edge("generate_document", END)

document_graph = workflow.compile()
```

### 11.2 Standard Workflow Node Sequence

All workflows follow this node sequence:

1. **get_content_file** - Extracts text from files in `storage_paths` via Supabase Storage
2. **get_chat_history** - Retrieves conversation context via `content_id`
3. **generate_**** - Main generation node that uses context + user message

### 11.3 Model Definitions

Create Pydantic models in `ba_copilot_ai/models/` for each document type:

```python
from pydantic import BaseModel

class DocumentResponse(BaseModel):
    title: str
    content: str  # Markdown content

class DocumentOutput(BaseModel):
    type: str  # Document identifier
    response: DocumentResponse
```

### 11.4 Centralized Model Connection

All workflows use the centralized `connect_model.py` module:

```python
from connect_model import get_model_client, MODEL

model_client = get_model_client()  # Singleton pattern
completion = model_client.chat_completion(messages=[...], model=MODEL)
```

---

## 12. Summary of All Document Types

| ID | Document Name | Type | Endpoint |
|----|---------------|------|----------|
| stakeholder-register | Stakeholder Register | markdown | `/generate/stakeholder-register` |
| high-level-requirements | High-level Requirements | markdown | `/generate/high-level-requirements` |
| requirements-management-plan | Requirements Management Plan | markdown | `/generate/requirements-management-plan` |
| business-case | Business Case Document | markdown | `/generate/business-case` |
| scope-statement | Scope Statement Document | markdown | `/generate/scope-statement` |
| product-roadmap | Product Roadmap Document | diagram | `/generate/product-roadmap` |
| feasibility-study | Feasibility Study Report | markdown | `/generate/feasibility-study` |
| cost-benefit-analysis | Cost-Benefit Analysis | markdown | `/generate/cost-benefit-analysis` |
| risk-register | Risk Register Document | markdown | `/generate/risk-register` |
| compliance | Compliance Document | markdown | `/generate/compliance` |
| hld-arch | System Architecture Diagram | diagram | `/generate/hld-arch` |
| hld-cloud | Cloud Infrastructure Setup | markdown | `/generate/hld-cloud` |
| hld-tech | Tech Stack Selection | markdown | `/generate/hld-tech` |
| lld-arch | Architecture Diagrams | diagram | `/generate/lld-arch` |
| lld-db | Database Schemas | mermaid | `/generate/lld-db` |
| lld-api | API Specifications | markdown | `/generate/lld-api` |
| lld-pseudo | Pseudocode | markdown | `/generate/lld-pseudo` |
| uiux-wireframe | Wireframes | markdown | `/generate/uiux-wireframe` |
| uiux-mockup | Mockups | markdown | `/generate/uiux-mockup` |
| uiux-prototype | Prototypes | markdown | `/generate/uiux-prototype` |
| rtm | Requirements Traceability Matrix | markdown | `/generate/rtm` |

---

## 13. Consistency Guidelines

### 13.1 Response Format

**ALL services must return:**
- `type`: String identifier matching the document ID
- `response`: Object containing document-specific data

### 13.2 Content Format

- **Markdown documents**: `response` contains `title` and `content` (full markdown)
- **Diagrams**: `response` contains `type` and `detail` (mermaid code)

### 13.3 Quality Standards

All generated documents should include:
- Professional formatting and structure
- Clear section headings
- Comprehensive content appropriate to document type
- Examples, tables, and diagrams where relevant
- Approval/sign-off sections for governance documents

---

## 14. Changelog

### Version 2.0 (December 16, 2025)
- **Breaking Change**: Unified all endpoints to use `AIRequest` format with `message`, `content_id`, `storage_paths`
- Added context enrichment from chat history and uploaded files
- Standardized workflow pattern with `get_content_file` -> `get_chat_history` -> `generate_*` nodes
- Centralized AI model connection via `connect_model.py` module
- Updated all request body examples to use new format

### Version 1.0 (December 11, 2025)
- Initial specification document
- Defined response patterns for markdown and diagram documents
- Documented all API endpoints for document generation

---

**Document Version:** 2.0
**Last Updated:** December 16, 2025
**Status:** Complete
