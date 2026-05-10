from datetime import datetime, timezone

from backend.agents.base import BaseAgent
from backend.llm.exceptions import LLMInvalidResponseError
from backend.prompts.finance import build_finance_analysis_prompt
from backend.prompts.json_utils import extract_json_object
from backend.workflows.schemas import FinanceOutput, Task, TaskResult, TaskStatus, WorkflowContext


class FinanceAgent(BaseAgent):
    name = "finance"
    role = "Budget analysis, forecasting, and financial risk management"

    async def execute(self, task: Task, context: WorkflowContext) -> TaskResult:
        started_at = datetime.now(timezone.utc)
        prompt = build_finance_analysis_prompt(goal=context.goal)
        result = await self.llm_provider.generate(prompt)
        try:
            data = extract_json_object(result.text)
            projection = data.get("revenue_projection") if isinstance(data.get("revenue_projection"), str) else None
            if not projection or not projection.strip():
                projection = result.text.strip()
        except LLMInvalidResponseError:
            projection = result.text.strip()

        output = FinanceOutput(
            budget_guardrails=[
                "Channel spend capped at 18% of monthly projected revenue",
                "Pause campaigns with CAC above target for 2 consecutive weeks",
            ],
            revenue_projection=projection,
            risk_flags=[
                "Short-term CAC volatility during campaign learning phase",
                "Margin pressure if discounting is overused",
            ],
            profitability_actions=[
                "Track blended CAC weekly",
                "Enforce contribution-margin threshold before scaling spend",
            ],
        )
        return TaskResult(
            task_id=task.task_id,
            agent=self.name,
            task_type=task.task_type,
            status=TaskStatus.COMPLETED,
            started_at=started_at,
            completed_at=datetime.now(timezone.utc),
            confidence_score=0.84,
            output=output,
        )
