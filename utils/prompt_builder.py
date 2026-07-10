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

        # ROLE

        {role}

        # PRIMARY INPUT

        The context above contains:

        - Uploaded project documents
        - Software Requirement Specification (SRS)
        - High Level Requirements (HLR)
        - Other generated documents

        Treat these documents as the source of truth.

        If information exists in multiple documents, use the most specific and latest requirement.

        # OPTIONAL USER REQUEST

        {user_message if user_message else "No additional user request."}

        If an additional user request is provided:

        - apply it only when it does not contradict the documented requirements.

        If no additional request is provided:

        - infer the UI completely from the requirements.

        # TASK
        {task}

        Identify:

        - application purpose
        - user roles
        - business flows
        - primary pages
        - required components
        - forms
        - tables
        - navigation
        - dashboards
        - actions
        - validations

        Then design a professional UI mockup representing the application.

        The generated UI should:

        - accurately reflect the documented requirements
        - prioritize usability
        - use proper visual hierarchy
        - include realistic content
        - include responsive layouts
        - include reusable design patterns

        Do not invent business features unless they are required to complete the interface.

        Missing visual details may be reasonably inferred.

        ### UI RULES

        Generate HTML and CSS only.

        HTML and CSS must work together.

        {additional_rules}

        ### OUTPUT

        {{
        "content": {{
            "html": "...",
            "css": "..."
        }},
        "summary": "..."
        }}

        Return raw JSON only.
        """
