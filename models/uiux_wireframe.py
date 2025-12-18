"""
UI/UX Wireframe model for Phase 6 - UI/UX Design Phase
"""

from pydantic import BaseModel
from typing import Optional


class UIUXWireframeResponse(BaseModel):
    """Response model for UI/UX wireframe generation"""
    title: str
    wireframe_type: str  # "low-fidelity", "high-fidelity", "interactive"
    screens: str  # List of screens/pages
    layout_structure: str  # Layout grid and structure
    components: str  # UI components used
    navigation_flow: str  # Navigation between screens
    annotations: str  # Design annotations and notes
    responsive_behavior: str  # Mobile/tablet/desktop considerations
    detail: str  # Complete wireframe specification or HTML/CSS


class UIUXWireframeOutput(BaseModel):
    """Output wrapper for wireframe response"""
    type: str = "uiux-wireframe"
    response: UIUXWireframeResponse
