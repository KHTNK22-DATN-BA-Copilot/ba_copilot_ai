from openai import OpenAI
from models.wireframe import WireframeHTMLCSSResponse
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Load API key from environment
OPENROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY", "")

def generate_html_css(description: str, extracted_text: str = "", chat_context: str = "") -> WireframeHTMLCSSResponse:
    """Generate wireframe using OpenRouter AI"""
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

    # Build comprehensive prompt with context
    context_parts = []
    if chat_context:
        context_parts.append(f"Context from previous conversation:\n{chat_context}\n")
    if extracted_text:
        context_parts.append(f"Extracted content from uploaded files:\n{extracted_text}\n")

    context_str = "\n".join(context_parts)

    prompt = f"""
    ### ROLE
    You are a Principal Frontend Lead, highly specialized in pure HTML, CSS.

    ### CONTEXT
    {context_str}

    We need to create a wireframe to satisfy all requirements specified by "{description}", using only plain HTML and CSS

    ### INSTRUCTION
    1. Analyze the given **CONTEXT**, prepare a detailed implementation list
    2. Generate main structure with HTML
    3. Add CSS to style, color, applying best practices and industry standards

    ### OUTPUT
    - Plain HTML and CSS code for the wireframe in JSON format
    - Ensure correct syntax, precise tags are used for semantic
    - Only return the plain HTML and CSS code, do not include comments, even comments in the code
    """

    try:
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "BA-Copilot",
            },
            model="tngtech/deepseek-r1t2-chimera:free",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        html_css_generated = completion.choices[0].message.content

        # Create response with diagram type and markdown detail
        wireframe_html_css_response = WireframeHTMLCSSResponse(
            content = str(html_css_generated)
        )
        print("HTML CSS Response created:", wireframe_html_css_response)
        
        return wireframe_html_css_response

    except Exception as e:
        print(f"Error generating HTML-CSS from text input: {e}")
        # Fallback response
        return WireframeHTMLCSSResponse(
            content = str("Fallback response for HTML-CSS wireframe generation")
        )