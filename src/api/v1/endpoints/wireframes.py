"""
Wireframe endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid

router = APIRouter()

class WireframeComponent(BaseModel):
    """Wireframe component model."""
    type: str
    properties: Dict[str, Any]

class WireframeResponse(BaseModel):
    """Wireframe response model."""
    wireframe_id: str
    preview_url: str
    html_content: str
    css_styles: str
    components_identified: List[WireframeComponent]
    metadata: Dict[str, Any]

class WireframeExportResponse(BaseModel):
    """Wireframe export response model."""
    download_url: str
    expires_at: str
    file_size_bytes: int
    format: str

@router.get("/{wireframe_id}", response_model=WireframeResponse)
async def get_wireframe(wireframe_id: str):
    """
    Retrieve a generated wireframe.
    
    Args:
        wireframe_id: The unique identifier for the wireframe
    
    Returns:
        Wireframe with HTML content, CSS styles, and metadata
    """
    if not wireframe_id.startswith("wf_"):
        raise HTTPException(status_code=400, detail="Invalid wireframe ID format")
    
    mock_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Wireframe</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="dashboard-container">
        <nav class="sidebar">
            <h2>Navigation</h2>
            <ul>
                <li><a href="#dashboard">Dashboard</a></li>
                <li><a href="#analytics">Analytics</a></li>
                <li><a href="#reports">Reports</a></li>
                <li><a href="#settings">Settings</a></li>
            </ul>
        </nav>
        <main class="main-content">
            <header class="top-bar">
                <h1>Dashboard</h1>
                <div class="user-profile">User Profile</div>
            </header>
            <section class="analytics-section">
                <div class="chart-container">
                    <h3>Analytics Chart</h3>
                    <div class="chart-placeholder">[Chart Placeholder]</div>
                </div>
                <div class="stats-cards">
                    <div class="stat-card">
                        <h4>Total Users</h4>
                        <p>1,234</p>
                    </div>
                    <div class="stat-card">
                        <h4>Revenue</h4>
                        <p>$12,345</p>
                    </div>
                </div>
            </section>
        </main>
    </div>
</body>
</html>"""

    mock_css = """/* Generated CSS styles */
.dashboard-container {
    display: flex;
    min-height: 100vh;
    font-family: Arial, sans-serif;
}

.sidebar {
    width: 250px;
    background-color: #f4f4f4;
    padding: 20px;
    border-right: 1px solid #ddd;
}

.sidebar h2 {
    margin-bottom: 20px;
    color: #333;
}

.sidebar ul {
    list-style: none;
    padding: 0;
}

.sidebar li {
    margin-bottom: 10px;
}

.sidebar a {
    text-decoration: none;
    color: #666;
    padding: 10px;
    display: block;
    border-radius: 4px;
    transition: background-color 0.3s;
}

.sidebar a:hover {
    background-color: #e0e0e0;
}

.main-content {
    flex: 1;
    padding: 20px;
}

.top-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
    padding-bottom: 20px;
    border-bottom: 1px solid #eee;
}

.analytics-section {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 20px;
}

.chart-container {
    background-color: #f9f9f9;
    padding: 20px;
    border-radius: 8px;
    border: 1px solid #e0e0e0;
}

.chart-placeholder {
    height: 200px;
    background-color: #e0e0e0;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #666;
    margin-top: 10px;
}

.stats-cards {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.stat-card {
    background-color: #fff;
    padding: 20px;
    border-radius: 8px;
    border: 1px solid #e0e0e0;
    text-align: center;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stat-card h4 {
    margin: 0 0 10px 0;
    color: #333;
    font-size: 14px;
    text-transform: uppercase;
}

.stat-card p {
    margin: 0;
    font-size: 24px;
    font-weight: bold;
    color: #007bff;
}

@media (max-width: 768px) {
    .dashboard-container {
        flex-direction: column;
    }
    
    .sidebar {
        width: 100%;
    }
    
    .analytics-section {
        grid-template-columns: 1fr;
    }
    
    .stats-cards {
        flex-direction: row;
    }
}"""

    return WireframeResponse(
        wireframe_id=wireframe_id,
        preview_url=f"http://localhost:8000/v1/wireframes/{wireframe_id}/preview",
        html_content=mock_html,
        css_styles=mock_css,
        components_identified=[
            WireframeComponent(
                type="navigation",
                properties={"location": "sidebar", "items": 4}
            ),
            WireframeComponent(
                type="header",
                properties={"title": "Dashboard", "has_user_profile": True}
            ),
            WireframeComponent(
                type="chart",
                properties={"type": "analytics", "placeholder": True}
            ),
            WireframeComponent(
                type="stats_cards",
                properties={"count": 2, "metrics": ["users", "revenue"]}
            )
        ],
        metadata={
            "template_used": "dashboard",
            "responsive_breakpoints": ["768px", "1024px", "1200px"],
            "created_at": "2025-09-20T14:30:00Z",
            "updated_at": "2025-09-20T14:30:00Z",
            "status": "generated",
            "target_devices": ["desktop", "tablet", "mobile"]
        }
    )

@router.get("/{wireframe_id}/export", response_model=WireframeExportResponse)
async def export_wireframe(
    wireframe_id: str,
    format: str = Query(..., description="Export format (html, zip, figma)"),
    include_css: bool = Query(True, description="Include CSS files"),
    responsive: bool = Query(True, description="Include responsive breakpoints")
):
    """
    Export wireframe in specified format.
    
    Args:
        wireframe_id: The unique identifier for the wireframe
        format: Export format (html, zip, figma)
        include_css: Whether to include CSS files
        responsive: Whether to include responsive design
    
    Returns:
        Export download information
    """
    if not wireframe_id.startswith("wf_"):
        raise HTTPException(status_code=400, detail="Invalid wireframe ID format")
        
    if format not in ["html", "zip", "figma"]:
        raise HTTPException(status_code=400, detail="Invalid format. Supported: html, zip, figma")
    
    file_sizes = {"html": 8192, "zip": 25600, "figma": 15360}
    
    return WireframeExportResponse(
        download_url=f"http://localhost:8000/exports/{wireframe_id}.{format}",
        expires_at="2025-09-21T14:30:00Z",
        file_size_bytes=file_sizes.get(format, 8192),
        format=format
    )