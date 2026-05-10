import json
import re
from typing import Any

from backend.llm.exceptions import LLMInvalidResponseError


def extract_json_object(text: str) -> dict[str, Any]:
    """Parse a single JSON object from model output (raw or fenced)."""
    stripped = text.strip()
    fence = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", stripped)
    if fence:
        stripped = fence.group(1).strip()
    try:
        data = json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start >= 0 and end > start:
            try:
                data = json.loads(stripped[start : end + 1])
            except json.JSONDecodeError as exc:
                raise LLMInvalidResponseError(
                    "Model output is not valid JSON.",
                    provider="json_parser",
                    cause=exc,
                ) from exc
        else:
            raise LLMInvalidResponseError("No JSON object found in model output.", provider="json_parser")
    if not isinstance(data, dict):
        raise LLMInvalidResponseError("Expected a JSON object at the top level.", provider="json_parser")
    return data
