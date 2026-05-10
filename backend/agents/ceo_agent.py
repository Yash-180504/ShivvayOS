from datetime import datetime, timezone

from backend.agents.base import BaseAgent
from backend.llm.exceptions import LLMInvalidResponseError
from backend.prompts.ceo import build_ceo_direction_prompt, build_ceo_synthesis_prompt
from backend.prompts.json_utils import extract_json_object
from backend.workflows.schemas import (
    CEODirectionOutput,
    CEOSynthesisOutput,
    FinanceOutput,
    MarketingOutput,
    Task,
    TaskResult,
    TaskStatus,
    TaskType,
    WorkflowContext,
)


def _parse_str_field(data: dict, key: str, raw_fallback: str) -> str:
    value = data.get(key)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return raw_fallback.strip()


class CEOAgent(BaseAgent):
    name = "ceo"
    role = "Strategic planning and executive synthesis"

    async def execute(self, task: Task, context: WorkflowContext) -> TaskResult:
        started_at = datetime.now(timezone.utc)

        if task.task_type == TaskType.CEO_DIRECTION:
            prompt = build_ceo_direction_prompt(goal=context.goal)
            result = await self.llm_provider.generate(prompt)
            try:
                data = extract_json_object(result.text)
                strategy = _parse_str_field(data, "strategic_focus", result.text)
            except LLMInvalidResponseError:
                strategy = result.text.strip()
            output = CEODirectionOutput(
                strategic_focus=strategy,
                priority_order=[
                    "Improve marketing funnel conversion",
                    "Protect unit economics and cash flow",
                    "Increase delivery throughput",
                ],
                success_metrics=[
                    "Marketing qualified leads",
                    "Cost per acquisition",
                    "Gross margin",
                ],
            )
            confidence = 0.86
        else:
            marketing = self._extract_marketing_output(context)
            finance = self._extract_finance_output(context)
            prompt = build_ceo_synthesis_prompt(
                goal=context.goal,
                marketing_hypothesis=marketing.growth_hypothesis,
                finance_projection=finance.revenue_projection,
            )
            result = await self.llm_provider.generate(prompt)
            try:
                data = extract_json_object(result.text)
                summary_text = _parse_str_field(data, "executive_summary", result.text)
            except LLMInvalidResponseError:
                summary_text = result.text.strip()
            output = CEOSynthesisOutput(
                executive_summary=summary_text,
                strategic_priorities=[
                    "Scale campaigns for high-converting segments",
                    "Apply finance guardrails on CAC and channel spend",
                    "Coordinate operations capacity for demand increase",
                ],
                combined_insights=[
                    f"Marketing hypothesis: {marketing.growth_hypothesis}",
                    f"Finance projection: {finance.revenue_projection}",
                ],
                next_actions=[
                    "Launch 30-day experiment plan",
                    "Review weekly spend-to-revenue ratio",
                    "Publish monthly executive KPI dashboard",
                ],
            )
            confidence = 0.88

        return TaskResult(
            task_id=task.task_id,
            agent=self.name,
            task_type=task.task_type,
            status=TaskStatus.COMPLETED,
            started_at=started_at,
            completed_at=datetime.now(timezone.utc),
            confidence_score=confidence,
            output=output,
        )

    def _extract_marketing_output(self, context: WorkflowContext) -> MarketingOutput:
        for res in reversed(context.results):
            if isinstance(res.output, MarketingOutput):
                return res.output
        raise ValueError("Marketing output is required for CEO synthesis")

    def _extract_finance_output(self, context: WorkflowContext) -> FinanceOutput:
        for res in reversed(context.results):
            if isinstance(res.output, FinanceOutput):
                return res.output
        raise ValueError("Finance output is required for CEO synthesis")
