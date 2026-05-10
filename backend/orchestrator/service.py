from datetime import datetime, timezone
from functools import lru_cache
from typing import Callable
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from backend.agents.base import BaseAgent
from backend.agents.ceo_agent import CEOAgent
from backend.agents.finance_agent import FinanceAgent
from backend.agents.marketing_agent import MarketingAgent
from backend.database.repositories.workflow_repository import WorkflowRepository
from backend.errors.exceptions import WorkflowExecutionError
from backend.core.config import settings
from backend.llm.base import BaseLLMProvider
from backend.llm.factory import create_llm_provider
from backend.observability.logger import WorkflowLogger
from backend.workflows.schemas import (
    CEOSynthesisOutput,
    Task,
    TaskResult,
    TaskStatus,
    TaskType,
    WorkflowContext,
    WorkflowRunRequest,
    WorkflowRunResponse,
)


class OrchestratorService:
    def __init__(
        self,
        llm_provider: BaseLLMProvider | None = None,
        repository_factory: Callable[[AsyncSession], WorkflowRepository] = WorkflowRepository,
    ) -> None:
        provider = llm_provider or create_llm_provider(settings)
        self._ceo = CEOAgent(provider)
        self._marketing = MarketingAgent(provider)
        self._finance = FinanceAgent(provider)
        self._logger = WorkflowLogger()
        self._repository_factory = repository_factory

    async def run_workflow(self, request: WorkflowRunRequest, session: AsyncSession) -> WorkflowRunResponse:
        run_id = str(uuid4())
        context = WorkflowContext(run_id=run_id, goal=request.goal)
        repository = self._repository_factory(session)

        self._logger.workflow_started(context)
        await repository.create_workflow_run(run_id=run_id, goal=request.goal, status=context.status, started_at=context.started_at)
        await repository.create_event(run_id, context.timeline[-1])

        try:
            ceo_direction_task = Task(
                task_id=f"{run_id}:ceo-direction",
                agent="ceo",
                task_type=TaskType.CEO_DIRECTION,
                objective=request.goal,
                status=TaskStatus.QUEUED,
            )
            await self._execute_task(self._ceo, ceo_direction_task, context, repository)

            marketing_task = Task(
                task_id=f"{run_id}:marketing",
                agent="marketing",
                task_type=TaskType.MARKETING_ANALYSIS,
                objective="Create deterministic growth recommendations aligned with CEO direction",
                status=TaskStatus.QUEUED,
                dependencies=[ceo_direction_task.task_id],
            )
            await self._execute_task(self._marketing, marketing_task, context, repository)

            finance_task = Task(
                task_id=f"{run_id}:finance",
                agent="finance",
                task_type=TaskType.FINANCE_ANALYSIS,
                objective="Provide budget and risk analysis for the proposed growth plan",
                status=TaskStatus.QUEUED,
                dependencies=[ceo_direction_task.task_id, marketing_task.task_id],
            )
            await self._execute_task(self._finance, finance_task, context, repository)

            ceo_synthesis_task = Task(
                task_id=f"{run_id}:ceo-synthesis",
                agent="ceo",
                task_type=TaskType.CEO_SYNTHESIS,
                objective="Synthesize final executive plan from marketing and finance outputs",
                status=TaskStatus.QUEUED,
                dependencies=[marketing_task.task_id, finance_task.task_id],
            )
            synthesis_result = await self._execute_task(self._ceo, ceo_synthesis_task, context, repository)

            context.completed_at = datetime.now(timezone.utc)
            self._logger.workflow_completed(context)
            await repository.create_event(run_id, context.timeline[-1])

            assert isinstance(synthesis_result.output, CEOSynthesisOutput)
            await repository.update_workflow_status(
                run_id=run_id,
                status=TaskStatus.COMPLETED,
                completed_at=context.completed_at,
                executive_summary=synthesis_result.output.model_dump(mode="json"),
            )
            await session.commit()

            return WorkflowRunResponse(
                run_id=run_id,
                goal=request.goal,
                status=context.status,
                started_at=context.started_at,
                completed_at=context.completed_at,
                task_results=context.results,
                timeline=context.timeline,
                executive_summary=synthesis_result.output,
            )
        except Exception as exc:
            context.status = TaskStatus.FAILED
            context.error_code = "WORKFLOW_EXECUTION_FAILED"
            context.error_message = str(exc)
            context.failed_at = datetime.now(timezone.utc)
            context.completed_at = context.failed_at
            self._logger.workflow_failed(context, str(exc))
            await repository.create_event(run_id, context.timeline[-1])
            await repository.update_workflow_status(
                run_id=run_id,
                status=TaskStatus.FAILED,
                completed_at=context.completed_at,
                error_code=context.error_code,
                error_message=context.error_message,
                failed_at=context.failed_at,
            )
            await session.commit()
            raise WorkflowExecutionError(run_id=run_id, reason=str(exc)) from exc

    async def _execute_task(
        self,
        agent: BaseAgent,
        task: Task,
        context: WorkflowContext,
        repository: WorkflowRepository,
    ) -> TaskResult:
        await repository.create_task_execution(
            run_id=context.run_id,
            task_id=task.task_id,
            task_type=task.task_type.value,
            assigned_agent=task.agent,
            status=TaskStatus.QUEUED,
        )

        task.status = TaskStatus.RUNNING
        self._logger.task_started(context, task)
        await repository.create_event(context.run_id, context.timeline[-1])

        try:
            result = await agent.execute(task, context)
            task.status = TaskStatus.COMPLETED
            context.add_result(result)
            self._logger.task_completed(context, task)
            await repository.update_task_execution(task.task_id, TaskStatus.COMPLETED, result=result)
            await repository.create_event(context.run_id, context.timeline[-1])
            return result
        except Exception as exc:  # pragma: no cover
            failed_at = datetime.now(timezone.utc)
            task.status = TaskStatus.FAILED
            self._logger.task_failed(context, task, str(exc))
            await repository.update_task_execution(
                task.task_id,
                TaskStatus.FAILED,
                error_code="TASK_EXECUTION_FAILED",
                error_message=str(exc),
                failed_at=failed_at,
            )
            await repository.create_event(context.run_id, context.timeline[-1])
            raise


@lru_cache(maxsize=1)
def get_orchestrator_service() -> OrchestratorService:
    return OrchestratorService(llm_provider=create_llm_provider(settings))
