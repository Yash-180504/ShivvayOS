from dataclasses import dataclass
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from backend.llm.exceptions import LLMInvalidResponseError
from backend.prompts.json_utils import extract_json_object


OutputModel = TypeVar("OutputModel", bound=BaseModel)


@dataclass(frozen=True)
class ValidationOutcome:
    data: dict[str, Any]
    schema_validity_score: float
    used_recovery: bool


class ResponseValidator:
    def extract_field(
        self,
        *,
        raw_text: str,
        required_field: str,
        fallback_value: str,
    ) -> ValidationOutcome:
        try:
            data = extract_json_object(raw_text)
            value = data.get(required_field)
            if isinstance(value, str) and value.strip():
                return ValidationOutcome(
                    data={required_field: value.strip()},
                    schema_validity_score=1.0,
                    used_recovery=False,
                )
            return ValidationOutcome(
                data={required_field: fallback_value.strip()},
                schema_validity_score=0.65,
                used_recovery=True,
            )
        except LLMInvalidResponseError:
            return ValidationOutcome(
                data={required_field: fallback_value.strip()},
                schema_validity_score=0.45,
                used_recovery=True,
            )

    def enforce_schema(self, model_type: type[OutputModel], data: dict[str, Any]) -> OutputModel:
        try:
            return model_type.model_validate(data)
        except ValidationError as exc:
            raise LLMInvalidResponseError(
                f"Validated response does not match {model_type.__name__}.",
                provider="response_validator",
                cause=exc,
            ) from exc
