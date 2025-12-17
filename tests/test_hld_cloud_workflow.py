import pytest
from workflows.hld_cloud_workflow import hld_cloud_graph


def test_hld_cloud_workflow_basic():
    """Test basic cloud infrastructure document generation."""
    state = {
        "user_message": "Generate cloud infrastructure setup for a web application",
        "content_id": None,
        "storage_paths": []
    }
    
    result = hld_cloud_graph.invoke(state)
    
    # Verify result structure
    assert "response" in result
    response = result["response"]
    
    # Verify all required fields are present
    assert "title" in response
    assert "cloud_provider" in response
    assert "infrastructure_components" in response
    assert "deployment_architecture" in response
    assert "scaling_strategy" in response
    assert "security_measures" in response
    assert "monitoring_logging" in response
    assert "cost_estimation" in response
    assert "detail" in response
    
    # Verify field types
    assert isinstance(response["title"], str)
    assert isinstance(response["cloud_provider"], str)
    assert isinstance(response["infrastructure_components"], str)
    assert isinstance(response["detail"], str)
    
    # Verify non-empty content
    assert len(response["title"]) > 0
    assert len(response["cloud_provider"]) > 0
    assert len(response["detail"]) > 0


def test_hld_cloud_workflow_aws():
    """Test cloud infrastructure for AWS platform."""
    state = {
        "user_message": "Create AWS cloud infrastructure for microservices application with ECS, RDS, and S3",
        "content_id": "aws-microservices",
        "storage_paths": []
    }
    
    result = hld_cloud_graph.invoke(state)
    
    response = result["response"]
    
    # Verify structure
    assert "cloud_provider" in response
    assert "infrastructure_components" in response
    assert "deployment_architecture" in response
    
    # Content should be meaningful
    assert len(response["infrastructure_components"]) > 50
    assert len(response["deployment_architecture"]) > 50


def test_hld_cloud_workflow_azure():
    """Test cloud infrastructure for Azure platform."""
    state = {
        "user_message": "Design Azure cloud infrastructure with AKS, Azure SQL, and Azure Storage",
        "content_id": None,
        "storage_paths": []
    }
    
    result = hld_cloud_graph.invoke(state)
    
    response = result["response"]
    
    # Verify all fields present
    assert "cloud_provider" in response
    assert "scaling_strategy" in response
    assert "security_measures" in response
    assert "monitoring_logging" in response
    assert "cost_estimation" in response


def test_hld_cloud_workflow_gcp():
    """Test cloud infrastructure for Google Cloud Platform."""
    state = {
        "user_message": "Plan GCP infrastructure using GKE, Cloud SQL, and Cloud Storage for data analytics platform",
        "content_id": "gcp-analytics",
        "storage_paths": []
    }
    
    result = hld_cloud_graph.invoke(state)
    
    response = result["response"]
    
    # Verify complete response
    assert all(key in response for key in [
        "title", "cloud_provider", "infrastructure_components",
        "deployment_architecture", "scaling_strategy", "security_measures",
        "monitoring_logging", "cost_estimation", "detail"
    ])


def test_hld_cloud_workflow_multi_region():
    """Test multi-region cloud deployment."""
    state = {
        "user_message": "Create multi-region cloud infrastructure with global load balancing and data replication",
        "content_id": None,
        "storage_paths": []
    }
    
    result = hld_cloud_graph.invoke(state)
    
    response = result["response"]
    
    # Should include scaling strategy for multi-region
    assert len(response["scaling_strategy"]) > 0
    assert len(response["deployment_architecture"]) > 0


def test_hld_cloud_workflow_serverless():
    """Test serverless cloud infrastructure."""
    state = {
        "user_message": "Design serverless architecture using AWS Lambda, API Gateway, DynamoDB, and S3",
        "content_id": "serverless-app",
        "storage_paths": []
    }
    
    result = hld_cloud_graph.invoke(state)
    
    response = result["response"]
    
    # Verify serverless components
    assert "infrastructure_components" in response
    assert len(response["infrastructure_components"]) > 50


def test_hld_cloud_workflow_with_storage_paths():
    """Test cloud infrastructure with storage path context."""
    state = {
        "user_message": "Generate cloud infrastructure for e-commerce platform",
        "content_id": "ecommerce-001",
        "storage_paths": ["/path/to/requirements.json", "/path/to/architecture.md"]
    }
    
    result = hld_cloud_graph.invoke(state)
    
    response = result["response"]
    
    # Should still generate complete response
    assert "cloud_provider" in response
    assert "security_measures" in response
    assert "monitoring_logging" in response


def test_hld_cloud_workflow_hybrid_cloud():
    """Test hybrid cloud infrastructure."""
    state = {
        "user_message": "Design hybrid cloud setup with on-premise datacenter and AWS integration",
        "content_id": None,
        "storage_paths": []
    }
    
    result = hld_cloud_graph.invoke(state)
    
    response = result["response"]
    
    # Verify all required fields
    assert len(response["deployment_architecture"]) > 0
    assert len(response["security_measures"]) > 0


def test_hld_cloud_workflow_cost_optimization():
    """Test cloud infrastructure with cost optimization focus."""
    state = {
        "user_message": "Create cost-optimized cloud infrastructure with auto-scaling and spot instances",
        "content_id": "cost-optimized",
        "storage_paths": []
    }
    
    result = hld_cloud_graph.invoke(state)
    
    response = result["response"]
    
    # Should include cost estimation
    assert "cost_estimation" in response
    assert len(response["cost_estimation"]) > 0
    assert "scaling_strategy" in response
    assert len(response["scaling_strategy"]) > 0


def test_hld_cloud_workflow_security_focused():
    """Test cloud infrastructure with security emphasis."""
    state = {
        "user_message": "Design highly secure cloud infrastructure with encryption, VPC, WAF, and DDoS protection",
        "content_id": None,
        "storage_paths": []
    }
    
    result = hld_cloud_graph.invoke(state)
    
    response = result["response"]
    
    # Should have detailed security measures
    assert "security_measures" in response
    assert len(response["security_measures"]) > 50
