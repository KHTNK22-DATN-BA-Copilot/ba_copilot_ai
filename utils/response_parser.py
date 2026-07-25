import json
import re
from . import extractor


def process_llm_response(raw_llm_output: str) -> dict:
    """Xử lý output từ LLM để tạo ra JSON object chứa 'content' và 'summary'

    đúng chuẩn format cho cả luồng Document và luồng UI/UX.
    """
    if not isinstance(raw_llm_output, str):
        return {"content": str(raw_llm_output), "summary": "No summary provided."}

    text = raw_llm_output.strip()

    # 1. Bóc tách khối code block nếu LLM cố tình chèn ```html, ```markdown hoặc ```
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n", "", text)
        text = re.sub(r"\n```$", "", text).strip()

    # 2. Tìm nội dung bên trong thẻ <summary>...</summary>
    summary_pattern = r"<summary>(.*?)</summary>"
    summary_match = re.search(summary_pattern, text, flags=re.DOTALL)

    if summary_match:
        summary = summary_match.group(1).strip()
        content = re.sub(summary_pattern, "", text, flags=re.DOTALL).strip()
    else:
        summary = "No summary provided."
        content = text

    return {"content": content, "summary": summary}


def parse_ai_json_response(
    raw_output: str,
    default_summary: str,
):
    """Parse kết quả trả về từ LLM cho cả luồng Document và UI/UX."""
    if not raw_output:
        return {
            "summary": default_summary,
            "content": "",
        }

    # 1. Trích xuất summary từ thẻ <summary> và giữ content nguyên bản (bao gồm HTML + CSS)
    result = process_llm_response(raw_output)

    # 2. Fallback tương thích ngược nếu LLM cũ sinh chuỗi JSON
    if isinstance(result["content"], str) and result["content"].strip().startswith("{") and result["content"].strip().endswith("}"):
        json_data = extractor.extract_json(result["content"])
        if json_data and isinstance(json_data, dict):
            if "summary" in json_data and (not result["summary"] or result["summary"] == "No summary provided."):
                result["summary"] = json_data.get("summary", default_summary)
            if "content" in json_data:
                result["content"] = json_data.get("content")

    if not result["summary"] or result["summary"] == "No summary provided.":
        result["summary"] = default_summary

    return result
