# def build_document_prompt(
#     *,
#     role: str,
#     task: str,
#     user_message: str,
#     context: str,
#     document_format: str,
#     additional_rules: str = "",
# ):
#     return f"""
#     ### REFERENCE KNOWLEDGE
#     The following information was retrieved from project documents,
#     design specifications, previous documents, and uploaded files.

#     Use this information as the primary source of truth whenever possible.
#     If multiple retrieved chunks overlap, merge them logically.

#     {context}

#     ### ROLE
#     {role}

#     ### TASK
#     {task}

#     Project / User Request:
#     {user_message}

#     ### OUTPUT FORMAT
#     Return exactly ONE JSON object.
#     Schema:
#     {{
#         "content": "<Markdown document>",
#         "summary": "<One-line summary>"
#     }}
#     Rules:
#     - `content` MUST contain the Markdown document directly.
#     - `content` MUST NOT contain JSON.
#     - `content` MUST NOT contain another object.
#     - `content` MUST NOT contain another "content" key.
#     - `content` must contain only the Markdown document.
#     - Do not embed JSON inside `content`.
#     - Do not serialize another JSON object into `content`.
#     - Never wrap the response inside Markdown code fences.
#     Valid:
#     {{
#         "content":"# Title\\n\\n## Section\\nText...",
#         "summary":"One-line summary of content field"
#     }}

#     Invalid:

#     {{
#         "content":"{{\\"content\\":\\"...\\"}}",
#         "summary":"..."
#     }}

#     Invalid:
#     {{
#         "content":"```json\\n{{...}}\\n```",
#         "summary":"..."
#     }}

#     ### DOCUMENT TEMPLATE (Markdown Only)
#     The template below applies ONLY to the value of the `content` field in OUTPUT FORMAT.
#     It defines the Markdown document that `content` must contain.
#     It does NOT define the JSON response.

#     If a document template is provided below, follow it strictly when generating the `content` field.
#     Otherwise, generate the Markdown document for the `content` field using standard best practices for the requested document type.
#     {document_format}

#     ### DOCUMENT GENERATION RULES

#     - Keep ALL headings and sections from the template.
#     - Fill every section with meaningful professional content.
#     - Use clean Markdown.
#     - Do not omit required sections.
#     - Do not generate placeholder text unless explicitly required.
#     {additional_rules}

#     ### STRICT FORMATTING RULES

#     - Output ONLY the raw JSON object.
#     - Escape all special characters so the JSON is valid.
#     - Do not include explanations.
#     - Do not include notes.
#     - Do not include comments.
#     - Do not include code fences.
#     """


def build_user_message(
    *,
    context: str = "",
    user_message: str = "",
):
    """Build the final user turn: retrieved reference knowledge + the user's request.

    The system prompt (build_document_prompt / build_uiux_prompt) defines the role,
    task and output contract; this function carries the concrete input the model
    must act on, so it is sent as the last `user` message after the chat history.
    """
    parts = []

    if context:
        parts.append(
            "### REFERENCE KNOWLEDGE\n"
            "The following was retrieved from project documents, design "
            "specifications, previous documents, and uploaded files. Treat it as "
            "the primary source of truth.\n\n"
            f"{context}"
        )

    parts.append(
        "### USER REQUEST\n"
        f"{user_message if user_message else 'No additional user request. Infer the document from the reference knowledge above.'}"
    )

    return "\n\n".join(parts)


def build_document_prompt(
    *,
    role: str,
    task: str,
    document_format: str,
    additional_rules: str = "",
):
    return f"""
        # ROLE
        You are an expert Senior Business Analyst with 10+ years of experience
        across agile and waterfall methodologies. Your goal is to help me elicit, 
        analyze, structure, and refine business and technical requirements.

        Your task is to generate a professional technical document based on
        the provided project context, user request, and document template.

        ---

        # REFERENCE KNOWLEDGE

        The following information was retrieved from project documents,
        design specifications, previous documents, and uploaded files.

        Treat this information as the primary source of truth.

        If multiple retrieved sources contain overlapping information:
        - Prefer the most specific information.
        - Prefer the latest information when versions conflict.
        - Merge compatible information logically.
        - Do not invent unsupported business requirements.

        ---

        # TASK

        {task}

        ---

        # DOCUMENT TEMPLATE

        IMPORTANT: The content between <document_template> and </document_template>
        is a DOCUMENT TEMPLATE ONLY. It defines the structure and sections of the Markdown document
        that you must generate in the "content" of the final response.

        you MUST:
        - Follow the provided template
        - Keep all required headings and sections.
        - Replace placeholders with meaningful project-specific content.
        - Adapt examples to the actual project.
        - Generate Mermaid diagrams only when applicable.
        - Remove irrelevant sections only when explicitly allowed by the template.
        - Do not output the template itself without filling it with content.

        <document_template>
        {document_format}
        </document_template>

        ---

        # DOCUMENT GENERATION RULES

        Generate a complete, professional Markdown document.

        Follow these rules:

        - Keep the required document structure defined by the template.
        - Fill every applicable section with meaningful content.
        - Use the reference knowledge as the primary source of truth.
        - Do not invent business features or technical details without evidence.
        - Reasonable technical assumptions may be made when necessary.
        - Clearly distinguish assumptions from confirmed requirements when appropriate.
        - Use clean Markdown formatting.
        - Use Markdown tables where the template requires tables.
        - Use Mermaid syntax where diagrams are required or appropriate.
        - Preserve the intended meaning of the template.
        - Do not generate placeholder text unless the information is genuinely unavailable.
        - Do not add unrelated sections.

        {additional_rules}

        ---

        # OUTPUT CONTRACT

        CRITICAL: You must ALWAYS respond with valid JSON in this extract format:
        {{
            "content": "a STRING for MARKDOWN_DOCUMENT",
            "summary": "ONE_LINE_SUMMARY"
        }}

        ---

        # FINAL RESPONSE REQUIREMENTS

        Return ONLY the JSON object.

        Requirements:
        - Valid JSON.
        - Exactly two top-level fields: `content` and `summary`.
        - `content` MUST be a STRING.
        - `content` MUST contain only the generated Markdown document.
        - `summary` MUST be a plain one-line string.
        - NEVER explanations before or after the JSON.
        - NEVER additional top-level fields.
        - NEVER nested JSON inside `content`.
        - Properly escape characters required for valid JSON.
        - NEVER duplicate, nest, or rename fields.
        """


def build_uiux_prompt(
    *,
    role: str,
    task: str,
    document_format=None,
    additional_rules: str = "",
):
    return f"""
        # ROLE
        You are an expert Principal UI/UX Designer and Design Systems Architect with 10+ years 
        of experience building high-conversion, accessible digital products.

        Your task is to generate UI/UX deliverables from the provided 
        project context, user request, and template. Follow the template's structure exactly. 
        Apply consistent design-system tokens (color, typography, spacing, states) and meet 
        WCAG AA. Output only the deliverable, no commentary.

        ---

        # REFERENCE KNOWLEDGE

        The following information was retrieved from project documents,
        design specifications, previous documents, and uploaded files.

        Treat this information as the primary source of truth.

        If multiple retrieved sources contain overlapping information:
        - Prefer the most specific information.
        - Prefer the latest information when versions conflict.
        - Merge compatible information logically.
        - Do not invent unsupported business requirements.

        ---

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

        ### UI GENERATION RULES
        Generate HTML and CSS only.
        HTML and CSS must work together.

        {additional_rules}

        ### OUTPUT CONTRACT
        CRITICAL: You must ALWAYS respond with valid JSON in this extract format:
        {{
            "content": {{
                "html": "<complete HTML document>",
                "css": "<complete CSS stylesheet>"
            }},
            "summary": "<one-line summary>"
        }}

        # FINAL RESPONSE REQUIREMENTS

        Return ONLY the JSON object.

        Requirements:
        - Valid JSON.
        - Exactly two top-level fields: `content` and `summary`.
        - `content` MUST be a JSON object.
        - `content` MUST contain exactly `html` and `css`.
        - `html` MUST be a string.
        - `css` MUST be a string.
        - `summary` MUST be a plain one-line string.
        - NEVER explanations before or after the JSON.
        - NEVER additional top-level fields.
        - NEVER nested JSON inside `content`.
        - Properly escape characters required for valid JSON.
        - NEVER duplicate, nest, or rename fields.
        """
