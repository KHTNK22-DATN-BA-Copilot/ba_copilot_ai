from typing import Callable, Optional

from connect_model import (
    get_model_client,
    set_request_model_config,
    reset_request_model_config,
    MODEL,
)

from response import success_response, error_response

from utils.prompt_builder import build_user_message
from utils.response_parser import process_llm_response


def generate_document(
    *,
    state,
    config: Optional[dict],
    role: str,
    task: str,
    default_summary: str,
    default_format: Optional[str] = None,
    prompt_builder: Callable,
    additional_rules: str = "",
):
    model_client = get_model_client()

    cfg = (config or {}).get("configurable", {})

    token = set_request_model_config(
        provider=cfg.get("provider"),
        model_name=cfg.get("model_name"),
        api_key=cfg.get("api_key"),
    )

    try:
        user_message = state["user_message"]

        # RAG / uploaded-file context goes into the final user turn, not the system prompt.
        context_str = state.get("extracted_text", "") or ""

        # chat_context is a list of {"role": "user"|"ai", "message": str} in chronological order.
        chat_context = state.get("chat_context") or []
        if not isinstance(chat_context, list):
            chat_context = []

        document_format = state.get("document_format")
        if document_format is None:
            document_format = default_format if default_format is not None else ""

        system_prompt = prompt_builder(
            role=role,
            task=task,
            document_format=document_format,
            additional_rules=additional_rules,
        )

        user_prompt = build_user_message(
            context=context_str,
            user_message=user_message,
        )

        # System prompt -> prior conversation turns -> current request.
        messages = [{"role": "system", "message": system_prompt}]
        messages.extend(chat_context)
        messages.append({"role": "user", "message": user_prompt})

        response = model_client.chat_completion(
            messages=messages,
            model=cfg.get("model_name") or MODEL,
        )

        raw_output = response.choices[0].message.content or ""

        # parsed = process_llm_response(
        #     raw_output=raw_output,
        # )

        return process_llm_response(
            raw_llm_output=raw_output,
        )

    except Exception as e:
        print(f"Error generating document: {e}")

        return {
            "response": error_response(
                default_summary,
                f"Error generating document {default_summary}: {str(e)}",
            )
        }

    finally:
        reset_request_model_config(token)
