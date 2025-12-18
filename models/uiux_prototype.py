"""
UI/UX Prototype model for Phase 6 - UI/UX Design Phase
"""

from pydantic import BaseModel
from typing import Optional


class UIUXPrototypeResponse(BaseModel):
    """Response model for UI/UX prototype generation"""
    title: str
    prototype_type: str  # "interactive", "clickable", "animated"
    user_flows: str  # Primary user journeys and flows
    interactions: str  # Click, hover, scroll interactions
    animations: str  # Transitions and micro-interactions
    states: str  # UI states (default, hover, active, disabled, error)
    scenarios: str  # Use case scenarios covered
    accessibility: str  # WCAG compliance and accessibility features
    testing_notes: str  # Usability testing guidelines
    detail: str  # Complete prototype specification


class UIUXPrototypeOutput(BaseModel):
    """Output wrapper for prototype response"""
    type: str = "uiux-prototype"
    response: UIUXPrototypeResponse
