from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.database.models.workflow import TaskExecutionModel, WorkflowEventModel, WorkflowRunModel
from backend.errors.exceptions import NotFoundError
from backend.workflows.schemas import TaskResult, TaskStatus, WorkflowEvent


class WorkflowRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_workflow_run(self, run_id: str, goal: str, status: TaskStatus, started_at: datetime) -> WorkflowRunModel:
        run = WorkflowRunModel(id=run_id, goal=goal, status=status.value, started_at=started_at)
        self._session.add(run)
        await self._session.flush()
        return run

    async def update_workflow_status(
        self,
        run_id: str,
        status: TaskStatus,
        completed_at: datetime | None = None,
        executive_summary: dict | None = None,
        error_code: str | None = None,
        error_message: str | None = None,
        failed_at: datetime | None = None,
    ) -> None:
        run = await self._session.get(WorkflowRunModel, run_id)
        if run is None:
            return
        run.status = status.value
        run.completed_at = completed_at
        run.error_code = error_code
        run.error_message = error_message
        run.failed_at = failed_at
        if executive_summary is not None:
            run.executive_summary = executive_summary
        await self._session.flush()

    async def create_task_execution(self, run_id: str, task_id: str, task_type: str, assigned_agent: str, status: TaskStatus) -> TaskExecutionModel:
        task = TaskExecutionModel(
            id=task_id,
            workflow_run_id=run_id,
            task_type=task_type,
            assigned_agent=assigned_agent,
            status=status.value,
        )
        self._session.add(task)
        await self._session.flush()
        return task

    async def update_task_execution(
        self,
        task_id: str,
        status: TaskStatus,
        result: TaskResult | None = None,
        error_code: str | None = None,
        error_message: str | None = None,
        failed_at: datetime | None = None,
    ) -> None:
        task = await self._session.get(TaskExecutionModel, task_id)
        if task is None:
            return
        task.status = status.value
        task.error_code = error_code
        task.error_message = error_message
        task.failed_at = failed_at
        if result is not None:
            task.started_at = result.started_at
            task.completed_at = result.completed_at
            task.output_json = result.output.model_dump(mode="json")
            task.confidence_score = result.confidence_score
        await self._session.flush()

    async def create_event(self, run_id: str, event: WorkflowEvent) -> WorkflowEventModel:
        event_model = WorkflowEventModel(
            workflow_run_id=run_id,
            event_type=event.event_type.value,
            timestamp=event.timestamp,
            message=event.message,
        )
        self._session.add(event_model)
        await self._session.flush()
        return event_model

    async def list_workflows(self) -> list[WorkflowRunModel]:
        stmt = select(WorkflowRunModel).order_by(WorkflowRunModel.created_at.desc())
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_workflow(self, run_id: str) -> WorkflowRunModel:
        stmt = (
            select(WorkflowRunModel)
            .where(WorkflowRunModel.id == run_id)
            .options(selectinload(WorkflowRunModel.tasks), selectinload(WorkflowRunModel.events))
        )
        result = await self._session.execute(stmt)
        run = result.scalar_one_or_none()
        if run is None:
            raise NotFoundError("workflow", run_id)
        return run

    async def get_workflow_timeline(self, run_id: str) -> list[WorkflowEventModel]:
        stmt = select(WorkflowEventModel).where(WorkflowEventModel.workflow_run_id == run_id).order_by(WorkflowEventModel.timestamp.asc())
        result = await self._session.execute(stmt)
        events = list(result.scalars().all())
        if not events:
            run = await self._session.get(WorkflowRunModel, run_id)
            if run is None:
                raise NotFoundError("workflow", run_id)
        return events

    async def get_task(self, task_id: str) -> TaskExecutionModel:
        task = await self._session.get(TaskExecutionModel, task_id)
        if task is None:
            raise NotFoundError("task", task_id)
        return task
