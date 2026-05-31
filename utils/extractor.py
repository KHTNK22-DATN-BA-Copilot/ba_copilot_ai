import json
import re

def extract_mermaid(text: str) -> str:
    match = re.search(r"```mermaid\s*(.*?)```", text, re.DOTALL)
    return match.group(0) if match else ""

def extract_summary(text: str) -> str:
    match = re.search(r"```mermaid\s*.*?```\s*(.*)", text, re.DOTALL)
    return match.group(1).strip() if match else ""

# def extract_json(text: str) -> dict:
#     """Extract JSON from text response"""
#     try:
#         # Find JSON block
#         start = text.find('{')
#         end = text.rfind('}') + 1
#         if start != -1 and end > start:
#             return json.loads(text[start:end])
#         return {}
#     except Exception as e:
#         print(f"Error extracting JSON: {e}")
#         return {}

def extract_json(text: str) -> dict:
    """Robust JSON extractor (handles LLM malformed escapes safely)"""
    if not text:
        return {}

    try:
        # Step 1: extract JSON block
        start = text.find('{')
        end = text.rfind('}') + 1
        if start == -1 or end <= start:
            return {}

        json_str = text[start:end]

        # Step 2: try normal parse first
        try:
            return json.loads(json_str)
        except:
            pass

        # Step 3: fix common escape issues
        fixed = json_str

        # Fix invalid backslashes (VERY IMPORTANT)
        fixed = re.sub(r'\\(?!["\\/bfnrt])', r'\\\\', fixed)

        # Normalize newlines
        fixed = fixed.replace('\r', '')
        
        # Fix unescaped newlines inside strings
        fixed = fixed.replace('\n', '\\n')

        # Step 4: retry parsing
        try:
            return json.loads(fixed)
        except Exception as e:
            print(f"Error extracting JSON after fix: {e}")
            return {}

    except Exception as e:
        print(f"Error extracting JSON: {e}")
        return {}
