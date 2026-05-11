from datetime import datetime, timezone

from backend.agents.base import BaseAgent
from backend.prompts.registry import prompt_registry
from backend.workflows.context_builder import workflow_context_builder
from backend.workflows.schemas import FinanceOutput, Task, TaskResult, TaskStatus, WorkflowContext


class FinanceAgent(BaseAgent):
    name = "finance"
    role = "Budget analysis, forecasting, and financial risk management"

    async def execute(self, task: Task, context: WorkflowContext) -> TaskResult:
        started_at = datetime.now(timezone.utc)
        prompt_context = workflow_context_builder.build_for_task(context, task)
        prompt = prompt_registry.render("finance.analysis", goal=context.goal, **prompt_context)
        result = await self.llm_provider.generate(prompt)
        validation = self.response_validator.extract_field(
            raw_text=result.text,
            required_field="revenue_projection",
            fallback_value=result.text,
        )

        output = self.response_validator.enforce_schema(
            FinanceOutput,
            {
                "budget_guardrails": [
                    "Channel spend capped at 18% of monthly projected revenue",
                    "Pause campaigns with CAC above target for 2 consecutive weeks",
                ],
                "revenue_projection": validation.data["revenue_projection"],
                "risk_flags": [
                    "Short-term CAC volatility during campaign learning phase",
                    "Margin pressure if discounting is overused",
                ],
                "profitability_actions": [
                    "Track blended CAC weekly",
                    "Enforce contribution-margin threshold before scaling spend",
                ],
            },
        )
        scores = self.quality_scorer.score(
            output=output,
            base_confidence=0.84,
            schema_validity_score=validation.schema_validity_score,
            used_recovery=validation.used_recovery,
        )
        return TaskResult(
            task_id=task.task_id,
            agent=self.name,
            task_type=task.task_type,
            status=TaskStatus.COMPLETED,
            started_at=started_at,
            completed_at=datetime.now(timezone.utc),
            confidence_score=scores.confidence_score,
            reasoning_quality_score=scores.reasoning_quality_score,
            schema_validity_score=scores.schema_validity_score,
            output=output,
        )
