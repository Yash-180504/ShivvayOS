from datetime import datetime, timezone

from backend.agents.base import BaseAgent
from backend.prompts.registry import prompt_registry
from backend.workflows.context_builder import workflow_context_builder
from backend.workflows.schemas import MarketingOutput, Task, TaskResult, TaskStatus, WorkflowContext


class MarketingAgent(BaseAgent):
    name = "marketing"
    role = "Revenue growth, GTM and campaign strategy"

    async def execute(self, task: Task, context: WorkflowContext) -> TaskResult:
        started_at = datetime.now(timezone.utc)
        prompt_context = workflow_context_builder.build_for_task(context, task)
        prompt = prompt_registry.render("marketing.analysis", goal=context.goal, **prompt_context)
        result = await self.llm_provider.generate(prompt)
        validation = self.response_validator.extract_field(
            raw_text=result.text,
            required_field="growth_hypothesis",
            fallback_value=result.text,
        )

        output = self.response_validator.enforce_schema(
            MarketingOutput,
            {
                "target_segments": ["Mid-market SaaS", "D2C brands with repeat purchase patterns"],
                "campaign_plan": [
                    "Run paid search + retargeting in 2 ICP segments",
                    "Launch problem-solution content series for inbound leads",
                    "Optimize landing page CTA and trial onboarding",
                ],
                "growth_hypothesis": validation.data["growth_hypothesis"],
                "kpis": ["SQL volume", "Landing page conversion", "CAC payback period"],
            },
        )
        scores = self.quality_scorer.score(
            output=output,
            base_confidence=0.81,
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
