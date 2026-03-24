import json
import re

def extract_mermaid(text: str) -> str:
    match = re.search(r"```mermaid\s*(.*?)```", text, re.DOTALL)
    return match.group(0) if match else ""

def extract_summary(text: str) -> str:
    match = re.search(r"```mermaid\s*.*?```\s*(.*)", text, re.DOTALL)
    return match.group(1).strip() if match else ""

def extract_json(text: str) -> dict:
    """Extract JSON from text response"""
    try:
        # Find JSON block
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end > start:
            return json.loads(text[start:end])
        return {}
    except Exception as e:
        print(f"Error extracting JSON: {e}")
        return {}
    