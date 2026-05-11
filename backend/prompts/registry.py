from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Callable


PromptRenderer = Callable[..., str]


@dataclass(frozen=True)
class PromptMetadata:
    prompt_id: str
    version: str
    role: str
    description: str
    expected_output_schema: dict[str, Any]
    renderer: PromptRenderer


class PromptRegistry:
    def __init__(self, prompts: list[PromptMetadata]) -> None:
        self._prompts: dict[tuple[str, str], PromptMetadata] = {
            (prompt.prompt_id, prompt.version): prompt for prompt in prompts
        }
        self._latest_versions: dict[str, str] = {}
        for prompt in prompts:
            current = self._latest_versions.get(prompt.prompt_id)
            if current is None or prompt.version > current:
                self._latest_versions[prompt.prompt_id] = prompt.version

    def get(self, prompt_id: str, version: str | None = None) -> PromptMetadata:
        selected_version = version or self._latest_versions.get(prompt_id)
        if selected_version is None:
            raise KeyError(f"Prompt not found: {prompt_id}")
        try:
            return self._prompts[(prompt_id, selected_version)]
        except KeyError as exc:
            raise KeyError(f"Prompt not found: {prompt_id}@{selected_version}") from exc

    def render(self, prompt_id: str, version: str | None = None, **kwargs: Any) -> str:
        prompt = self.get(prompt_id, version)
        return prompt.renderer(**kwargs)

    def inspect(self, prompt_id: str, version: str | None = None) -> dict[str, Any]:
        prompt = self.get(prompt_id, version)
        return {
            "prompt_id": prompt.prompt_id,
            "version": prompt.version,
            "role": prompt.role,
            "description": prompt.description,
            "expected_output_schema": prompt.expected_output_schema,
        }

    def list_metadata(self) -> list[dict[str, Any]]:
        return [self.inspect(prompt_id, version) for prompt_id, version in self._prompts]


def _schema(*fields: str) -> dict[str, Any]:
    return MappingProxyType(
        {
            "type": "object",
            "required": list(fields),
            "properties": {field: {"type": "string"} for field in fields},
            "additionalProperties": False,
        }
    )


from backend.prompts.ceo.direction import build_ceo_direction_prompt
from backend.prompts.ceo.synthesis import build_ceo_synthesis_prompt
from backend.prompts.finance.analysis import build_finance_analysis_prompt
from backend.prompts.marketing.analysis import build_marketing_analysis_prompt


prompt_registry = PromptRegistry(
    prompts=[
        PromptMetadata(
            prompt_id="ceo.direction",
            version="1.1.0",
            role="CEO Agent",
            description="Creates strategic direction and measurable executive priorities.",
            expected_output_schema=dict(_schema("strategic_focus")),
            renderer=build_ceo_direction_prompt,
        ),
        PromptMetadata(
            prompt_id="marketing.analysis",
            version="1.1.0",
            role="Sales & Marketing Agent",
            description="Creates a growth hypothesis informed by CEO direction and prior workflow context.",
            expected_output_schema=dict(_schema("growth_hypothesis")),
            renderer=build_marketing_analysis_prompt,
        ),
        PromptMetadata(
            prompt_id="finance.analysis",
            version="1.1.0",
            role="Finance & Accounting Agent",
            description="Creates a conservative revenue outlook informed by current strategic context.",
            expected_output_schema=dict(_schema("revenue_projection")),
            renderer=build_finance_analysis_prompt,
        ),
        PromptMetadata(
            prompt_id="ceo.synthesis",
            version="1.1.0",
            role="CEO Agent",
            description="Synthesizes departmental outputs into prioritized strategy, risks, and feasibility.",
            expected_output_schema=dict(_schema("executive_summary")),
            renderer=build_ceo_synthesis_prompt,
        ),
    ]
)
