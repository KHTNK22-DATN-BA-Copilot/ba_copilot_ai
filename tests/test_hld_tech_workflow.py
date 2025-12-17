import pytest
from workflows.hld_tech_workflow import hld_tech_graph


def test_hld_tech_workflow_basic():
    """Test basic technology stack selection generation."""
    state = {
        "user_message": "Generate technology stack for a web application",
        "content_id": None,
        "storage_paths": []
    }
    
    result = hld_tech_graph.invoke(state)
    
    # Verify result structure
    assert "response" in result
    response = result["response"]
    
    # Verify all required fields are present
    assert "title" in response
    assert "frontend_technologies" in response
    assert "backend_technologies" in response
    assert "database_technologies" in response
    assert "infrastructure_technologies" in response
    assert "integration_technologies" in response
    assert "selection_rationale" in response
    assert "risk_mitigation" in response
    assert "detail" in response
    
    # Verify field types
    assert isinstance(response["title"], str)
    assert isinstance(response["frontend_technologies"], str)
    assert isinstance(response["backend_technologies"], str)
    assert isinstance(response["database_technologies"], str)
    assert isinstance(response["detail"], str)
    
    # Verify non-empty content
    assert len(response["title"]) > 0
    assert len(response["frontend_technologies"]) > 0
    assert len(response["backend_technologies"]) > 0
    assert len(response["detail"]) > 0


def test_hld_tech_workflow_react_node():
    """Test React + Node.js technology stack."""
    state = {
        "user_message": "Create technology stack using React for frontend and Node.js with Express for backend",
        "content_id": "react-node-stack",
        "storage_paths": []
    }
    
    result = hld_tech_graph.invoke(state)
    
    response = result["response"]
    
    # Verify structure
    assert "frontend_technologies" in response
    assert "backend_technologies" in response
    assert "database_technologies" in response
    
    # Content should be meaningful
    assert len(response["frontend_technologies"]) > 30
    assert len(response["backend_technologies"]) > 30


def test_hld_tech_workflow_python_django():
    """Test Python Django technology stack."""
    state = {
        "user_message": "Design tech stack with Django, PostgreSQL, and React for an enterprise application",
        "content_id": None,
        "storage_paths": []
    }
    
    result = hld_tech_graph.invoke(state)
    
    response = result["response"]
    
    # Verify all fields present
    assert "backend_technologies" in response
    assert "database_technologies" in response
    assert "selection_rationale" in response
    assert "risk_mitigation" in response


def test_hld_tech_workflow_microservices():
    """Test microservices technology stack."""
    state = {
        "user_message": "Plan technology stack for microservices architecture with Spring Boot, Docker, Kubernetes",
        "content_id": "microservices-stack",
        "storage_paths": []
    }
    
    result = hld_tech_graph.invoke(state)
    
    response = result["response"]
    
    # Verify complete response
    assert all(key in response for key in [
        "title", "frontend_technologies", "backend_technologies",
        "database_technologies", "infrastructure_technologies",
        "integration_technologies", "selection_rationale", "risk_mitigation", "detail"
    ])


def test_hld_tech_workflow_mobile_app():
    """Test mobile application technology stack."""
    state = {
        "user_message": "Create tech stack for mobile app using React Native, Firebase, and GraphQL",
        "content_id": None,
        "storage_paths": []
    }
    
    result = hld_tech_graph.invoke(state)
    
    response = result["response"]
    
    # Should include mobile-specific technologies
    assert len(response["frontend_technologies"]) > 0
    assert len(response["backend_technologies"]) > 0
    assert len(response["database_technologies"]) > 0


def test_hld_tech_workflow_fullstack_javascript():
    """Test full-stack JavaScript technology stack."""
    state = {
        "user_message": "Design full-stack JavaScript tech stack with Next.js, Node.js, and MongoDB",
        "content_id": "fullstack-js",
        "storage_paths": []
    }
    
    result = hld_tech_graph.invoke(state)
    
    response = result["response"]
    
    # Verify JavaScript stack components
    assert "frontend_technologies" in response
    assert "backend_technologies" in response
    assert len(response["frontend_technologies"]) > 30


def test_hld_tech_workflow_with_storage_paths():
    """Test technology stack with storage path context."""
    state = {
        "user_message": "Generate technology stack for data analytics platform",
        "content_id": "analytics-001",
        "storage_paths": ["/path/to/requirements.json", "/path/to/specs.md"]
    }
    
    result = hld_tech_graph.invoke(state)
    
    response = result["response"]
    
    # Should still generate complete response
    assert "frontend_technologies" in response
    assert "backend_technologies" in response
    assert "integration_technologies" in response


def test_hld_tech_workflow_cloud_native():
    """Test cloud-native technology stack."""
    state = {
        "user_message": "Plan cloud-native tech stack with serverless functions, managed databases, and CDN",
        "content_id": None,
        "storage_paths": []
    }
    
    result = hld_tech_graph.invoke(state)
    
    response = result["response"]
    
    # Verify cloud-native components
    assert len(response["infrastructure_technologies"]) > 0
    assert len(response["backend_technologies"]) > 0


def test_hld_tech_workflow_with_rationale():
    """Test technology stack with detailed selection rationale."""
    state = {
        "user_message": "Create tech stack for high-performance trading platform requiring low latency",
        "content_id": "trading-platform",
        "storage_paths": []
    }
    
    result = hld_tech_graph.invoke(state)
    
    response = result["response"]
    
    # Should include rationale for performance requirements
    assert "selection_rationale" in response
    assert len(response["selection_rationale"]) > 50


def test_hld_tech_workflow_enterprise():
    """Test enterprise-grade technology stack."""
    state = {
        "user_message": "Design enterprise tech stack with Java Spring, Oracle, and Angular for large-scale system",
        "content_id": None,
        "storage_paths": []
    }
    
    result = hld_tech_graph.invoke(state)
    
    response = result["response"]
    
    # Verify enterprise components
    assert len(response["backend_technologies"]) > 0
    assert len(response["database_technologies"]) > 0
    assert len(response["risk_mitigation"]) > 0


def test_hld_tech_workflow_modern_stack():
    """Test modern technology stack with latest frameworks."""
    state = {
        "user_message": "Plan modern tech stack using Vue 3, FastAPI, PostgreSQL, and Redis",
        "content_id": "modern-stack",
        "storage_paths": []
    }
    
    result = hld_tech_graph.invoke(state)
    
    response = result["response"]
    
    # Verify all required fields with content
    assert all(len(response[key]) > 0 for key in [
        "title", "frontend_technologies", "backend_technologies",
        "database_technologies", "detail"
    ])
