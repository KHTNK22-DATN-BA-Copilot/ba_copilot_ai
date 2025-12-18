"""
UI/UX Mockup model for Phase 6 - UI/UX Design Phase
"""

from pydantic import BaseModel
from typing import Optional


class UIUXMockupResponse(BaseModel):
    """Response model for UI/UX mockup generation"""
    title: str
    mockup_type: str  # "visual-design", "high-fidelity", "pixel-perfect"
    design_system: str  # Colors, typography, spacing guidelines
    visual_hierarchy: str  # Visual weight and hierarchy
    color_palette: str  # Primary, secondary, accent colors with hex codes
    typography: str  # Font families, sizes, weights
    iconography: str  # Icon set and style
    imagery_style: str  # Photography/illustration style
    ui_elements: str  # Buttons, forms, cards specifications
    detail: str  # Complete mockup specification


class UIUXMockupOutput(BaseModel):
    """Output wrapper for mockup response"""
    type: str = "uiux-mockup"
    response: UIUXMockupResponse
