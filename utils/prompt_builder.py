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

        {{
            "content": "The complete generated document as a single string. Use valid Markdown syntax inside this string. Use literal \\n for all newlines and escape all quotes.",
            "summary": "A concise, one-line summary of the generated document."
        }}

        ### STRICT FORMATTING RULES
        - Output the raw JSON object ONLY.
        - No conversational text, no explanations, no text before or after the JSON.
        - All JSON keys and values must be valid strings.
        - Ensure all markdown formatting inside "content" is properly escaped to maintain valid JSON.
        """
