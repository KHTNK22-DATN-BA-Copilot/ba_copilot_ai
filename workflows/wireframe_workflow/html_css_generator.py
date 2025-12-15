from models.wireframe import WireframeHTMLCSSResponse
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from connect_model import get_model_client, MODEL

def generate_html_css(description: str, extracted_text: str = '', chat_context: str = '') -> WireframeHTMLCSSResponse:
    """Generate wireframe using OpenRouter AI"""
    model_client = get_model_client()

    # Build context
    context_parts = []
    if chat_context:
        context_parts.append(f"Context from previous conversation:\n{chat_context}\n")
    if extracted_text:
        context_parts.append(f"Extracted content from uploaded files:\n{extracted_text}\n")

    context_str = "\n".join(context_parts)

    prompt = f"""
    {context_str}

    ### ROLE
    You are a Principal Frontend Lead, highly specialized in pure HTML, CSS.

    ### CONTEXT

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
        completion = model_client.chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=MODEL
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
