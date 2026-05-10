from datetime import datetime, timezone

from backend.agents.base import BaseAgent
from backend.llm.exceptions import LLMInvalidResponseError
from backend.prompts.json_utils import extract_json_object
from backend.prompts.marketing import build_marketing_analysis_prompt
from backend.workflows.schemas import MarketingOutput, Task, TaskResult, TaskStatus, WorkflowContext


class MarketingAgent(BaseAgent):
    name = "marketing"
    role = "Revenue growth, GTM and campaign strategy"

    async def execute(self, task: Task, context: WorkflowContext) -> TaskResult:
        started_at = datetime.now(timezone.utc)
        prompt = build_marketing_analysis_prompt(goal=context.goal)
        result = await self.llm_provider.generate(prompt)
        try:
            data = extract_json_object(result.text)
            hypothesis = data.get("growth_hypothesis") if isinstance(data.get("growth_hypothesis"), str) else None
            if not hypothesis or not hypothesis.strip():
                hypothesis = result.text.strip()
        except LLMInvalidResponseError:
            hypothesis = result.text.strip()

        output = MarketingOutput(
            target_segments=["Mid-market SaaS", "D2C brands with repeat purchase patterns"],
            campaign_plan=[
                "Run paid search + retargeting in 2 ICP segments",
                "Launch problem-solution content series for inbound leads",
                "Optimize landing page CTA and trial onboarding",
            ],
            growth_hypothesis=hypothesis,
            kpis=["SQL volume", "Landing page conversion", "CAC payback period"],
        )
        return TaskResult(
            task_id=task.task_id,
            agent=self.name,
            task_type=task.task_type,
            status=TaskStatus.COMPLETED,
            started_at=started_at,
            completed_at=datetime.now(timezone.utc),
            confidence_score=0.81,
            output=output,
        )
