from typing import Optional

from connect_model import (
    get_model_client,
    set_request_model_config,
    reset_request_model_config,
    MODEL,
)

from response import success_response, error_response

from ..utils.context_builder import build_context
from ..utils.prompt_builder import build_document_prompt
from ..utils.response_parser import parse_ai_json_response


def generate_document(
    *,
    state,
    config: Optional[dict],
    role: str,
    task: str,
    default_summary: str,
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

        context_str = build_context(
            extracted_text=state.get("extracted_text", ""),
            chat_context=state.get("chat_context", ""),
        )

        document_format = state.get("document_format", "")

        prompt = build_document_prompt(
            role=role,
            task=task,
            user_message=user_message,
            context=context_str,
            document_format=document_format,
            additional_rules=additional_rules,
        )

        response = model_client.chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=cfg.get("model_name") or MODEL,
        )

        raw_output = response.choices[0].message.content or ""

        parsed = parse_ai_json_response(
            raw_output=raw_output,
            default_summary=default_summary,
        )

        return {
            "response": success_response(
                parsed["summary"],
                parsed["content"],
            )
        }

    except Exception as e:
        print(f"Error generating document: {e}")

        return {
            "response": error_response(
                default_summary,
                f"Error generating document: {str(e)}",
            )
        }

    finally:
        reset_request_model_config(token)
