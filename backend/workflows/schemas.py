from datetime import datetime, timezone
from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TaskStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskType(str, Enum):
    CEO_DIRECTION = "ceo_direction"
    MARKETING_ANALYSIS = "marketing_analysis"
    FINANCE_ANALYSIS = "finance_analysis"
    CEO_SYNTHESIS = "ceo_synthesis"


class WorkflowEventType(str, Enum):
    WORKFLOW_STARTED = "workflow_started"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"


class CEODirectionOutput(BaseModel):
    kind: Literal["ceo_direction"] = "ceo_direction"
    strategic_focus: str
    priority_order: list[str]
    success_metrics: list[str]


class MarketingOutput(BaseModel):
    kind: Literal["marketing_analysis"] = "marketing_analysis"
    target_segments: list[str]
    campaign_plan: list[str]
    growth_hypothesis: str
    kpis: list[str]


class FinanceOutput(BaseModel):
    kind: Literal["finance_analysis"] = "finance_analysis"
    budget_guardrails: list[str]
    revenue_projection: str
    risk_flags: list[str]
    profitability_actions: list[str]


class StrategicPriorityScore(BaseModel):
    priority: str
    impact_score: float = Field(ge=0, le=1)
    feasibility_score: float = Field(ge=0, le=1)
    rationale: str


class RiskCategory(BaseModel):
    category: str
    severity: Literal["low", "medium", "high"]
    mitigation: str


class CEOSynthesisOutput(BaseModel):
    kind: Literal["ceo_synthesis"] = "ceo_synthesis"
    executive_summary: str
    strategic_priorities: list[str]
    strategic_priority_scores: list[StrategicPriorityScore] = Field(default_factory=list)
    combined_insights: list[str]
    departmental_conflicts: list[str] = Field(default_factory=list)
    risk_categories: list[RiskCategory] = Field(default_factory=list)
    execution_feasibility_assessment: str = ""
    next_actions: list[str]


AgentOutput = Annotated[
    CEODirectionOutput | MarketingOutput | FinanceOutput | CEOSynthesisOutput,
    Field(discriminator="kind"),
]


class Task(BaseModel):
    task_id: str
    agent: str
    task_type: TaskType
    objective: str
    status: TaskStatus = TaskStatus.QUEUED
    dependencies: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)


class TaskResult(BaseModel):
    task_id: str
    agent: str
    task_type: TaskType
    status: TaskStatus
    started_at: datetime
    completed_at: datetime
    confidence_score: float = Field(ge=0, le=1)
    reasoning_quality_score: float = Field(default=0.0, ge=0, le=1)
    schema_validity_score: float = Field(default=0.0, ge=0, le=1)
    output: AgentOutput
    error_code: str | None = None
    error_message: str | None = None
    failed_at: datetime | None = None


class WorkflowEvent(BaseModel):
    event_type: WorkflowEventType
    task_id: str | None = None
    agent: str | None = None
    status: TaskStatus | None = None
    timestamp: datetime = Field(default_factory=utc_now)
    message: str


class WorkflowContext(BaseModel):
    run_id: str
    goal: str
    status: TaskStatus = TaskStatus.QUEUED
    started_at: datetime = Field(default_factory=utc_now)
    completed_at: datetime | None = None
    results: list[TaskResult] = Field(default_factory=list)
    timeline: list[WorkflowEvent] = Field(default_factory=list)
    error_code: str | None = None
    error_message: str | None = None
    failed_at: datetime | None = None

    def add_event(self, event: WorkflowEvent) -> None:
        self.timeline.append(event)

    def add_result(self, result: TaskResult) -> None:
        self.results.append(result)


class WorkflowRunRequest(BaseModel):
    goal: str = Field(min_length=3, description="High-level business goal from user")


class WorkflowRunResponse(BaseModel):
    run_id: str
    goal: str
    status: TaskStatus
    started_at: datetime
    completed_at: datetime
    task_results: list[TaskResult]
    timeline: list[WorkflowEvent]
    executive_summary: CEOSynthesisOutput


class WorkflowRunListItem(BaseModel):
    id: str
    goal: str
    status: TaskStatus
    started_at: datetime
    completed_at: datetime | None
    created_at: datetime


class TaskExecutionRecord(BaseModel):
    id: str
    workflow_run_id: str
    task_type: str
    assigned_agent: str
    status: TaskStatus
    started_at: datetime | None
    completed_at: datetime | None
    output_json: dict | None
    confidence_score: float | None
    reasoning_quality_score: float | None = None
    schema_validity_score: float | None = None
    error_code: str | None
    error_message: str | None
    failed_at: datetime | None


class WorkflowEventRecord(BaseModel):
    id: str
    workflow_run_id: str
    event_type: str
    timestamp: datetime
    message: str


class WorkflowRunDetailResponse(BaseModel):
    workflow: WorkflowRunListItem
    executive_summary: dict | None
    tasks: list[TaskExecutionRecord]
    timeline: list[WorkflowEventRecord]
