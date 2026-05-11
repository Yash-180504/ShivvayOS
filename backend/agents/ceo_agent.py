from datetime import datetime, timezone

from backend.agents.base import BaseAgent
from backend.prompts.registry import prompt_registry
from backend.workflows.context_builder import workflow_context_builder
from backend.workflows.schemas import (
    CEODirectionOutput,
    CEOSynthesisOutput,
    FinanceOutput,
    MarketingOutput,
    RiskCategory,
    StrategicPriorityScore,
    Task,
    TaskResult,
    TaskStatus,
    TaskType,
    WorkflowContext,
)


class CEOAgent(BaseAgent):
    name = "ceo"
    role = "Strategic planning and executive synthesis"

    async def execute(self, task: Task, context: WorkflowContext) -> TaskResult:
        started_at = datetime.now(timezone.utc)
        prompt_context = workflow_context_builder.build_for_task(context, task)

        if task.task_type == TaskType.CEO_DIRECTION:
            prompt = prompt_registry.render("ceo.direction", goal=context.goal, **prompt_context)
            result = await self.llm_provider.generate(prompt)
            validation = self.response_validator.extract_field(
                raw_text=result.text,
                required_field="strategic_focus",
                fallback_value=result.text,
            )
            output = self.response_validator.enforce_schema(
                CEODirectionOutput,
                {
                    "strategic_focus": validation.data["strategic_focus"],
                    "priority_order": [
                        "Improve marketing funnel conversion",
                        "Protect unit economics and cash flow",
                        "Increase delivery throughput",
                    ],
                    "success_metrics": [
                        "Marketing qualified leads",
                        "Cost per acquisition",
                        "Gross margin",
                    ],
                },
            )
            scores = self.quality_scorer.score(
                output=output,
                base_confidence=0.86,
                schema_validity_score=validation.schema_validity_score,
                used_recovery=validation.used_recovery,
            )
        else:
            marketing = self._extract_marketing_output(context)
            finance = self._extract_finance_output(context)
            prompt = prompt_registry.render(
                "ceo.synthesis",
                goal=context.goal,
                marketing_hypothesis=marketing.growth_hypothesis,
                finance_projection=finance.revenue_projection,
                **prompt_context,
            )
            result = await self.llm_provider.generate(prompt)
            validation = self.response_validator.extract_field(
                raw_text=result.text,
                required_field="executive_summary",
                fallback_value=result.text,
            )
            priorities = [
                "Scale campaigns for high-converting segments",
                "Apply finance guardrails on CAC and channel spend",
                "Coordinate operations capacity for demand increase",
            ]
            output = self.response_validator.enforce_schema(
                CEOSynthesisOutput,
                {
                    "executive_summary": validation.data["executive_summary"],
                    "strategic_priorities": priorities,
                    "strategic_priority_scores": [
                        StrategicPriorityScore(
                            priority=priorities[0],
                            impact_score=0.88,
                            feasibility_score=0.78,
                            rationale="Marketing can test this quickly while preserving a measurable revenue path.",
                        ).model_dump(),
                        StrategicPriorityScore(
                            priority=priorities[1],
                            impact_score=0.82,
                            feasibility_score=0.86,
                            rationale="Finance constraints reduce downside risk while campaigns are learning.",
                        ).model_dump(),
                        StrategicPriorityScore(
                            priority=priorities[2],
                            impact_score=0.74,
                            feasibility_score=0.72,
                            rationale="Operations alignment prevents demand generation from exceeding delivery capacity.",
                        ).model_dump(),
                    ],
                    "combined_insights": [
                        f"Marketing hypothesis: {marketing.growth_hypothesis}",
                        f"Finance projection: {finance.revenue_projection}",
                    ],
                    "departmental_conflicts": self._identify_conflicts(marketing, finance),
                    "risk_categories": [
                        RiskCategory(
                            category="financial",
                            severity="medium",
                            mitigation="Scale spend only when CAC and contribution margin stay inside finance guardrails.",
                        ).model_dump(),
                        RiskCategory(
                            category="execution",
                            severity="medium",
                            mitigation="Review operational capacity before expanding successful campaigns.",
                        ).model_dump(),
                    ],
                    "execution_feasibility_assessment": (
                        "Feasible as a staged 30-day experiment if spend gates, weekly KPI reviews, "
                        "and delivery capacity checks are enforced."
                    ),
                    "next_actions": [
                        "Launch 30-day experiment plan",
                        "Review weekly spend-to-revenue ratio",
                        "Publish monthly executive KPI dashboard",
                    ],
                },
            )
            scores = self.quality_scorer.score(
                output=output,
                base_confidence=0.88,
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

    def _identify_conflicts(self, marketing: MarketingOutput, finance: FinanceOutput) -> list[str]:
        conflicts: list[str] = []
        marketing_text = " ".join(marketing.campaign_plan + [marketing.growth_hypothesis]).lower()
        finance_text = " ".join(finance.budget_guardrails + finance.risk_flags).lower()
        if "paid" in marketing_text and ("cap" in finance_text or "cac" in finance_text):
            conflicts.append("Marketing wants to scale paid acquisition while Finance requires CAC and spend caps.")
        if "discount" in finance_text:
            conflicts.append("Finance flags margin risk if growth relies too heavily on discounting.")
        return conflicts or ["No material departmental conflict detected; recommendations are broadly aligned."]
