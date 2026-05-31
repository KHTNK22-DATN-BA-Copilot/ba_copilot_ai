def build_context(
    extracted_text: str = "",
    chat_context: str = "",
):
    context_parts = []

    if chat_context:
        context_parts.append(f"""
        Context from previous conversation:
        {chat_context}
        """)

    if extracted_text:
        context_parts.append(f"""
        Extracted content from uploaded files:
        {extracted_text}
        """)

    return "\n".join(context_parts)
