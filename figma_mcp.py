# ai_service/figma_mcp.py
import uuid

def generate_figma_wireframe(description: str):
    figma_id = uuid.uuid4()
    link = f"https://www.figma.com/file/{figma_id}/auto-generated-wireframe"
    return {
        "figma_link": link,
        "editable": True,
        "description": description
    }

def generate_figma_diagram(description: str):
    figma_id = uuid.uuid4()
    link = f"https://www.figma.com/file/{figma_id}/auto-generated-diagram"
    return {
        "figma_link": link,
        "editable": True,
        "description": description
    }
