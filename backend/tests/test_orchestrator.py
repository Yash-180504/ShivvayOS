from dataclasses import dataclass, field

import asyncio

import pytest

from backend.agents.base import BaseAgent
from backend.llm.mock_provider import MockLLMProvider
from backend.orchestrator.service import OrchestratorService
from backend.workflows.schemas import Task, TaskResult, TaskStatus, WorkflowRunRequest


class FakeSession:
    def __init__(self) -> None:
        self.committed = False

    async def commit(self) -> None:
        self.committed = True


@dataclass
class FakeRepository:
    session: FakeSession
    workflow_created: bool = False
    workflow_updates: list[dict] = field(default_factory=list)
    created_tasks: list[str] = field(default_factory=list)
    updated_tasks: list[dict] = field(default_factory=list)
    events: list[str] = field(default_factory=list)

    async def create_workflow_run(self, **kwargs):
        self.workflow_created = True
        return kwargs

    async def create_event(self, run_id, event):
        self.events.append(event.event_type.value)
        return {"run_id": run_id}

    async def create_task_execution(self, run_id, task_id, task_type, assigned_agent, status):
        self.created_tasks.append(task_id)
        return {"id": task_id}

    async def update_task_execution(self, task_id, status, result=None, error_code=None, error_message=None, failed_at=None):
        self.updated_tasks.append(
            {
                "task_id": task_id,
                "status": status.value,
                "has_result": result is not None,
                "error_code": error_code,
            }
        )

    async def update_workflow_status(self, **kwargs):
        self.workflow_updates.append(kwargs)


def test_workflow_execution_ordering():
    session = FakeSession()
    repo = FakeRepository(session)
    orchestrator = OrchestratorService(llm_provider=MockLLMProvider(), repository_factory=lambda _: repo)

    response = asyncio.run(orchestrator.run_workflow(WorkflowRunRequest(goal="Improve revenue"), session))

    assert response.status == TaskStatus.COMPLETED
    assert repo.created_tasks[0].endswith(":ceo-direction")
    assert repo.created_tasks[1].endswith(":marketing")
    assert repo.created_tasks[2].endswith(":finance")
    assert repo.created_tasks[3].endswith(":ceo-synthesis")


def test_ceo_synthesis_contains_marketing_and_finance_insights():
    session = FakeSession()
    repo = FakeRepository(session)
    orchestrator = OrchestratorService(llm_provider=MockLLMProvider(), repository_factory=lambda _: repo)

    response = asyncio.run(orchestrator.run_workflow(WorkflowRunRequest(goal="Improve revenue"), session))

    combined = " ".join(response.executive_summary.combined_insights)
    assert "Marketing hypothesis:" in combined
    assert "Finance projection:" in combined


def test_ceo_synthesis_includes_workflow_intelligence_fields():
    session = FakeSession()
    repo = FakeRepository(session)
    orchestrator = OrchestratorService(llm_provider=MockLLMProvider(), repository_factory=lambda _: repo)

    response = asyncio.run(orchestrator.run_workflow(WorkflowRunRequest(goal="Improve revenue"), session))

    assert response.executive_summary.strategic_priority_scores
    assert response.executive_summary.risk_categories
    assert response.executive_summary.departmental_conflicts
    assert "Feasible" in response.executive_summary.execution_feasibility_assessment


def test_task_results_include_quality_scores():
    session = FakeSession()
    repo = FakeRepository(session)
    orchestrator = OrchestratorService(llm_provider=MockLLMProvider(), repository_factory=lambda _: repo)

    response = asyncio.run(orchestrator.run_workflow(WorkflowRunRequest(goal="Improve revenue"), session))

    assert all(0 <= result.confidence_score <= 1 for result in response.task_results)
    assert all(0 <= result.reasoning_quality_score <= 1 for result in response.task_results)
    assert all(0 <= result.schema_validity_score <= 1 for result in response.task_results)


def test_task_persistence_behavior_updates_each_task():
    session = FakeSession()
    repo = FakeRepository(session)
    orchestrator = OrchestratorService(llm_provider=MockLLMProvider(), repository_factory=lambda _: repo)

    asyncio.run(orchestrator.run_workflow(WorkflowRunRequest(goal="Improve revenue"), session))

    assert len(repo.updated_tasks) == 4
    assert all(item["status"] == TaskStatus.COMPLETED.value for item in repo.updated_tasks)


def test_timeline_event_creation_includes_start_and_completion():
    session = FakeSession()
    repo = FakeRepository(session)
    orchestrator = OrchestratorService(llm_provider=MockLLMProvider(), repository_factory=lambda _: repo)

    asyncio.run(orchestrator.run_workflow(WorkflowRunRequest(goal="Improve revenue"), session))

    assert repo.events[0] == "workflow_started"
    assert repo.events[-1] == "workflow_completed"


class FailingAgent(BaseAgent):
    name = "marketing"
    role = "fails intentionally"

    async def execute(self, task: Task, context) -> TaskResult:
        raise RuntimeError("forced task failure")


def test_failure_state_handling_persists_failure_state():
    session = FakeSession()
    repo = FakeRepository(session)
    orchestrator = OrchestratorService(llm_provider=MockLLMProvider(), repository_factory=lambda _: repo)
    orchestrator._marketing = FailingAgent(MockLLMProvider())

    with pytest.raises(Exception):
        asyncio.run(orchestrator.run_workflow(WorkflowRunRequest(goal="Improve revenue"), session))

    assert any(update.get("status") == TaskStatus.FAILED for update in repo.workflow_updates)
    failed_task_updates = [item for item in repo.updated_tasks if item["status"] == TaskStatus.FAILED.value]
    assert failed_task_updates
    assert failed_task_updates[0]["error_code"] == "TASK_EXECUTION_FAILED"
