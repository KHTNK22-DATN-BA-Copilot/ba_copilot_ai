def build_document_prompt(
    *,
    role: str,
    task: str,
    user_message: str,
    context: str,
    document_format: str,
    additional_rules: str = "",
):
    return f"""
        {context}

        ### ROLE
        {role}

        ### TASK
        {task}

        Project / User Request:
        {user_message}

        ### TARGET DOCUMENT STRUCTURE (MARKDOWN)
        This is the structure you must generate inside the JSON "content" field:
        {document_format}

        ### DOCUMENT GENERATION RULES
        - The generated document must keep ALL headings and sections from the TARGET DOCUMENT STRUCTURE.
        - Fill all sections with meaningful professional content.
        - Write the document content using clean Markdown syntax.

        {additional_rules}

        ### OUTPUT FORMAT SPECIFICATION

        You must return a raw JSON object matching the schema below. Do not wrap the JSON in markdown code blocks (e.g., do not use ```json).
        The response must contain exactly one top-level `content` field and one top-level `summary` field.

        - `content` must contain the actual generated document directly.
        - Never include `content` or `summary` inside the `content` field.
        - Never wrap the actual content inside another object with `content` or `summary` keys.

        Schema:
        {{
            "content": "<Markdown string>",
            "summary": "A concise, one-line summary of the generated document."
        }}


        ### STRICT FORMATTING RULES
        - Output the raw JSON object ONLY.
        - No conversational text, no explanations, no text before or after the JSON.
        - "content" must be a valid JSON string containing the generated Markdown.
        - "summary" must be a valid JSON string.
        - Escape special characters inside the Markdown so the JSON remains valid.
        """


def build_uiux_prompt(
    *,
    role: str,
    task: str,
    user_message: str,
    context: str,
    document_format=None,
    additional_rules: str = "",
):
    return f"""
        {context}

        ### ROLE
        {role}

        ### TASK
        {task}

        Project / User Request:
        {user_message}

        ### UI GENERATION RULES
        - Design the UI based on the user's request.
        - Generate HTML and CSS separately.
        - Ensure the HTML and CSS work together correctly.

        {additional_rules}

       ### OUTPUT FORMAT SPECIFICATION

        You must return a raw JSON object matching the schema below. Do not wrap the JSON in Markdown code blocks (e.g. ```json).

        The response must contain exactly one top-level `content` field and one top-level `summary` field.

        - Never include `content` or `summary` inside the `content` field.
        - Never wrap the generated HTML/CSS inside another object.

        Schema:
        {{
            "content": {{
                "html": "<html code>",
                "css": "<css code>"
            }},
            "summary": "A concise, one-line summary of the generated UI."
        }}

        ### STRICT FORMATTING RULES
        - Output the raw JSON object ONLY.
        - No conversational text.
        - No explanations.
        - No text before or after the JSON.
        - Escape quotation marks, backslashes, newlines, and other special characters inside the HTML and CSS strings so the JSON remains valid.
        """
