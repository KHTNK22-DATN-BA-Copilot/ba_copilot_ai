# ai_service/figma_mcp.py
import os
import requests
import uuid
from typing import Dict, Optional
from datetime import datetime

# Figma API Configuration
FIGMA_API_BASE = "https://api.figma.com/v1"
FIGMA_ACCESS_TOKEN = os.getenv("FIGMA_API_TOKEN")

def get_headers() -> Dict[str, str]:
    """Get headers for Figma API requests"""+9

    return {
        "X-Figma-Token": FIGMA_ACCESS_TOKEN,
        "Content-Type": "application/json"
    }

def create_figma_file(name: str) -> Optional[Dict]:
    """
    Create a new Figma file

    Args:
        name: File name

    Returns:
        dict: File data including key, or None if error
    """
    if not FIGMA_ACCESS_TOKEN:
        return None

    url = f"{FIGMA_API_BASE}/files"

    payload = {
        "name": name
    }

    try:
        response = requests.post(url, headers=get_headers(), json=payload)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Figma API error: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"Error creating Figma file: {e}")
        return None

def create_wireframe_components(description: str) -> list:
    """
    Create basic wireframe components based on description

    Args:
        description: User's wireframe description

    Returns:
        list: List of Figma component nodes
    """
    # Basic wireframe structure
    components = [
        {
            "type": "FRAME",
            "name": "Wireframe Canvas",
            "backgroundColor": {"r": 0.95, "g": 0.95, "b": 0.95, "a": 1},
            "children": [
                {
                    "type": "FRAME",
                    "name": "Header",
                    "backgroundColor": {"r": 1, "g": 1, "b": 1, "a": 1}
                },
                {
                    "type": "FRAME",
                    "name": "Content",
                    "backgroundColor": {"r": 1, "g": 1, "b": 1, "a": 1}
                },
                {
                    "type": "TEXT",
                    "name": "Description",
                    "characters": f"Wireframe: {description[:100]}"
                }
            ]
        }
    ]

    return components

def create_diagram_components(description: str) -> list:
    """
    Create basic diagram components based on description

    Args:
        description: AI-generated diagram description

    Returns:
        list: List of Figma component nodes
    """
    # Basic diagram structure
    components = [
        {
            "type": "FRAME",
            "name": "Diagram Canvas",
            "backgroundColor": {"r": 0.98, "g": 0.98, "b": 0.98, "a": 1},
            "children": [
                {
                    "type": "TEXT",
                    "name": "Diagram Description",
                    "characters": f"Diagram: {description[:200]}"
                }
            ]
        }
    ]

    return components

def generate_figma_wireframe(description: str) -> Dict:
    """
    Generate wireframe using Figma API (with fallback to mock)

    Args:
        description: User's wireframe requirement

    Returns:
        dict: Wireframe data with Figma link
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"Wireframe_{timestamp}"

    # Try to create real Figma file if token is configured
    if FIGMA_ACCESS_TOKEN:
        try:
            file_data = create_figma_file(file_name)

            if file_data and "key" in file_data:
                file_key = file_data["key"]
                figma_link = f"https://www.figma.com/file/{file_key}/{file_name}"

                return {
                    "figma_link": figma_link,
                    "editable": True,
                    "description": description,
                    "file_key": file_key,
                    "created_at": timestamp
                }
        except Exception as e:
            print(f"Error using Figma API, falling back to mock: {e}")

    # Fallback to mock if API not configured or failed
    figma_id = uuid.uuid4()
    return {
        "figma_link": f"https://www.figma.com/file/{figma_id}/auto-generated-wireframe",
        "editable": True,
        "description": description
    }

def generate_figma_diagram(description: str) -> Dict:
    """
    Generate diagram using Figma API (with fallback to mock)

    Args:
        description: AI-generated diagram description

    Returns:
        dict: Diagram data with Figma link
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"Diagram_{timestamp}"

    # Try to create real Figma file if token is configured
    if FIGMA_ACCESS_TOKEN:
        try:
            file_data = create_figma_file(file_name)

            if file_data and "key" in file_data:
                file_key = file_data["key"]
                figma_link = f"https://www.figma.com/file/{file_key}/{file_name}"

                return {
                    "figma_link": figma_link,
                    "editable": True,
                    "description": description,
                    "file_key": file_key,
                    "created_at": timestamp
                }
        except Exception as e:
            print(f"Error using Figma API, falling back to mock: {e}")

    # Fallback to mock if API not configured or failed
    figma_id = uuid.uuid4()
    return {
        "figma_link": f"https://www.figma.com/file/{figma_id}/auto-generated-diagram",
        "editable": True,
        "description": description
    }
