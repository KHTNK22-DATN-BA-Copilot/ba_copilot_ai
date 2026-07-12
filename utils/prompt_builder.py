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
    ### REFERENCE KNOWLEDGE
    The following information was retrieved from project documents,
    design specifications, previous documents, and uploaded files.

    Use this information as the primary source of truth whenever possible.
    If multiple retrieved chunks overlap, merge them logically.

    {context}

    ### ROLE
    {role}

    ### TASK
    {task}

    Project / User Request:
    {user_message}

    ### OUTPUT FORMAT
    Return exactly ONE JSON object.
    Schema:
    {{
        "content": "<Markdown document>",
        "summary": "<One-line summary>"
    }}
    Rules:
    - `content` MUST contain the Markdown document directly.
    - `content` MUST NOT contain JSON.
    - `content` MUST NOT contain another object.
    - `content` MUST NOT contain another "content" key.
    - `content` must contain only the Markdown document.
    - Do not embed JSON inside `content`.
    - Do not serialize another JSON object into `content`.
    - Never wrap the response inside Markdown code fences.
    Valid:
    {{
        "content":"# Title\\n\\n## Section\\nText...",
        "summary":"One-line summary of content field"
    }}

    Invalid:

    {{
        "content":"{{\\"content\\":\\"...\\"}}",
        "summary":"..."
    }}

    Invalid:
    {{
        "content":"```json\\n{{...}}\\n```",
        "summary":"..."
    }}

    ### DOCUMENT TEMPLATE (Markdown Only)
    The template below applies ONLY to the value of the `content` field in OUTPUT FORMAT.
    It defines the Markdown document that `content` must contain.
    It does NOT define the JSON response.

    If a document template is provided below, follow it strictly when generating the `content` field.
    Otherwise, generate the Markdown document for the `content` field using standard best practices for the requested document type.
    {document_format}

    ### DOCUMENT GENERATION RULES

    - Keep ALL headings and sections from the template.
    - Fill every section with meaningful professional content.
    - Use clean Markdown.
    - Do not omit required sections.
    - Do not generate placeholder text unless explicitly required.
    {additional_rules}

    ### STRICT FORMATTING RULES

    - Output ONLY the raw JSON object.
    - Escape all special characters so the JSON is valid.
    - Do not include explanations.
    - Do not include notes.
    - Do not include comments.
    - Do not include code fences.
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
        "summary": "A concise, one-line summary of the generated document."
        }}

        Return raw JSON only.
        """
