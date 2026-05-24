from ..utils import extractor


def parse_ai_json_response(
    raw_output: str,
    default_summary: str,
):
    json_data = extractor.extract_json(raw_output)

    if not json_data:
        return {
            "summary": default_summary,
            "content": raw_output,
        }

    return {
        "summary": json_data.get("summary", default_summary),
        "content": json_data.get("content", raw_output),
    }
