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
# SYSTEM ROLE

You are an expert software documentation engineer.

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

<reference_knowledge>
{context}
</reference_knowledge>

---

# ROLE

{role}

---

# TASK

{task}

---

# USER REQUEST

{user_message if user_message else "No additional user request was provided."}

---

# DOCUMENT TEMPLATE

IMPORTANT:

The content between <document_template> and </document_template>
is a DOCUMENT TEMPLATE ONLY. It defines the structure and sections of the Markdown document
that you must generate in the "content" of the final response.

You MUST:
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

Your entire response MUST be exactly ONE valid JSON object.

The JSON object has exactly two fields:

- `content`
- `summary`

The structure is:

{{
    "content": "MARKDOWN_DOCUMENT",
    "summary": "ONE_LINE_SUMMARY"
}}

IMPORTANT:

`content` is a STRING.

The value of `content` must contain the complete generated Markdown document.

`content` must NOT be:
- a JSON object
- a JSON string containing another JSON object
- an object with `content` and `summary`
- an object with `html` and `css`
- wrapped in Markdown code fences

The document template is used to generate the VALUE of `content`.
The document template does NOT define the structure of the outer JSON response.

The ONLY JSON object in the response is the outer response object.

The following conceptual structure MUST be followed:

JSON response
    |
    +-- content: STRING
    |       |
    |       +-- Markdown document
    |
    +-- summary: STRING

Must not create this structure:

JSON response
    |
    +-- content
            |
            +-- content
            +-- summary

Do not create any nested JSON inside `content`.

---

# FINAL RESPONSE REQUIREMENTS

Return ONLY the JSON object.

Requirements:

1. Valid JSON.
2. Exactly two top-level fields: `content` and `summary`.
3. `content` must be a string.
4. `content` must contain only the generated Markdown document.
5. `summary` must be a plain one-line string.
6. No Markdown code fences around the outer JSON.
7. No explanations before or after the JSON.
8. No additional top-level fields.
9. No nested JSON inside `content`.
10. Properly escape characters required for valid JSON.

Return the final JSON object now.
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

        ### OUTPUT CONTRACT

        Return exactly ONE valid JSON object.

        The JSON object MUST have exactly the following structure:

        {{
            "content": {{
                "html": "<complete HTML document>",
                "css": "<complete CSS stylesheet>"
            }},
            "summary": "<one-line summary>"
        }}

        ### STRICT FIELD RULES

        - `content` MUST be a JSON object.
        - `content` MUST contain exactly `html` and `css`.
        - `html` MUST be a string.
        - `css` MUST be a string.
        - `summary` MUST be a string.
        - `summary` MUST contain only a concise one-line summary.

        Do NOT duplicate, nest, or rename fields.

        Do NOT create structures such as:

        - `"content": "content"`
        - `"content": {{"content": {{...}}}}`
        - `"content": {{"content": "..."}}`
        - `"html": {{"html": "..."}}`
        - `"css": {{"css": "..."}}`
        - `"summary": {{"summary": "..."}}`
        - `"summary": "summary"`

        Each field MUST contain its actual generated value,
        NOT the literal name of the field.

        ### NO MARKDOWN CODE FENCE RULE

        The response MUST NOT contain Markdown code fences.

        MUST NOT:
        - Put JSON inside `html`.
        - Put JSON inside `css`.
        - Serialize the `content` object into a JSON string.
        - Create another `content` field inside `content`.
        - Create nested `html` or `css` objects.
        - Add additional top-level fields.
        - Wrap the response in Markdown code fences.
        - Output anything before or after the JSON object.
        """
