# models/hld_cloud.py
from pydantic import BaseModel

class HLDCloudResponse(BaseModel):
    """Response model for Cloud Infrastructure Setup document"""
    title: str
    executive_summary: str
    cloud_provider_selection: str
    infrastructure_components: str
    deployment_architecture: str
    scalability_strategy: str
    security_considerations: str
    cost_estimation: str
    detail: str

class HLDCloudOutput(BaseModel):
    """Output wrapper for Cloud Infrastructure Setup"""
    type: str = "hld-cloud"
    response: HLDCloudResponse
