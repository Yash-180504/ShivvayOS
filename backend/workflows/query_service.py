from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.repositories.workflow_repository import WorkflowRepository
from backend.workflows.schemas import (
    TaskExecutionRecord,
    TaskStatus,
    WorkflowEventRecord,
    WorkflowRunDetailResponse,
    WorkflowRunListItem,
)


class WorkflowQueryService:
    async def list_workflows(self, session: AsyncSession) -> list[WorkflowRunListItem]:
        repository = WorkflowRepository(session)
        rows = await repository.list_workflows()
        return [
            WorkflowRunListItem(
                id=row.id,
                goal=row.goal,
                status=TaskStatus(row.status),
                started_at=row.started_at,
                completed_at=row.completed_at,
                created_at=row.created_at,
            )
            for row in rows
        ]

    async def get_workflow(self, session: AsyncSession, run_id: str) -> WorkflowRunDetailResponse:
        repository = WorkflowRepository(session)
        row = await repository.get_workflow(run_id)
        return WorkflowRunDetailResponse(
            workflow=WorkflowRunListItem(
                id=row.id,
                goal=row.goal,
                status=TaskStatus(row.status),
                started_at=row.started_at,
                completed_at=row.completed_at,
                created_at=row.created_at,
            ),
            executive_summary=row.executive_summary,
            tasks=[
                TaskExecutionRecord(
                    id=t.id,
                    workflow_run_id=t.workflow_run_id,
                    task_type=t.task_type,
                    assigned_agent=t.assigned_agent,
                    status=TaskStatus(t.status),
                    started_at=t.started_at,
                    completed_at=t.completed_at,
                    output_json=t.output_json,
                    confidence_score=t.confidence_score,
                    error_code=t.error_code,
                    error_message=t.error_message,
                    failed_at=t.failed_at,
                )
                for t in sorted(row.tasks, key=lambda x: (x.started_at is None, x.started_at))
            ],
            timeline=[
                WorkflowEventRecord(
                    id=e.id,
                    workflow_run_id=e.workflow_run_id,
                    event_type=e.event_type,
                    timestamp=e.timestamp,
                    message=e.message,
                )
                for e in sorted(row.events, key=lambda x: x.timestamp)
            ],
        )

    async def get_workflow_timeline(self, session: AsyncSession, run_id: str) -> list[WorkflowEventRecord]:
        repository = WorkflowRepository(session)
        events = await repository.get_workflow_timeline(run_id)
        return [
            WorkflowEventRecord(
                id=e.id,
                workflow_run_id=e.workflow_run_id,
                event_type=e.event_type,
                timestamp=e.timestamp,
                message=e.message,
            )
            for e in events
        ]

    async def get_task(self, session: AsyncSession, task_id: str) -> TaskExecutionRecord:
        repository = WorkflowRepository(session)
        t = await repository.get_task(task_id)
        return TaskExecutionRecord(
            id=t.id,
            workflow_run_id=t.workflow_run_id,
            task_type=t.task_type,
            assigned_agent=t.assigned_agent,
            status=TaskStatus(t.status),
            started_at=t.started_at,
            completed_at=t.completed_at,
            output_json=t.output_json,
            confidence_score=t.confidence_score,
            error_code=t.error_code,
            error_message=t.error_message,
            failed_at=t.failed_at,
        )


def get_workflow_query_service() -> WorkflowQueryService:
    return WorkflowQueryService()
