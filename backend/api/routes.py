from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_db_session
from backend.orchestrator.service import OrchestratorService, get_orchestrator_service
from backend.workflows.query_service import WorkflowQueryService, get_workflow_query_service
from backend.workflows.schemas import (
    TaskExecutionRecord,
    WorkflowEventRecord,
    WorkflowRunDetailResponse,
    WorkflowRunListItem,
    WorkflowRunRequest,
    WorkflowRunResponse,
)

router = APIRouter()


@router.post("/workflows/run", response_model=WorkflowRunResponse, tags=["workflows"])
async def run_workflow(
    payload: WorkflowRunRequest,
    session: AsyncSession = Depends(get_db_session),
    orchestrator: OrchestratorService = Depends(get_orchestrator_service),
) -> WorkflowRunResponse:
    return await orchestrator.run_workflow(payload, session)


@router.get("/workflows", response_model=list[WorkflowRunListItem], tags=["workflows"])
async def list_workflows(
    session: AsyncSession = Depends(get_db_session),
    query_service: WorkflowQueryService = Depends(get_workflow_query_service),
) -> list[WorkflowRunListItem]:
    return await query_service.list_workflows(session)


@router.get("/workflows/{run_id}", response_model=WorkflowRunDetailResponse, tags=["workflows"])
async def get_workflow(
    run_id: str,
    session: AsyncSession = Depends(get_db_session),
    query_service: WorkflowQueryService = Depends(get_workflow_query_service),
) -> WorkflowRunDetailResponse:
    return await query_service.get_workflow(session, run_id)


@router.get("/workflows/{run_id}/timeline", response_model=list[WorkflowEventRecord], tags=["workflows"])
async def get_workflow_timeline(
    run_id: str,
    session: AsyncSession = Depends(get_db_session),
    query_service: WorkflowQueryService = Depends(get_workflow_query_service),
) -> list[WorkflowEventRecord]:
    return await query_service.get_workflow_timeline(session, run_id)


@router.get("/tasks/{task_id}", response_model=TaskExecutionRecord, tags=["tasks"])
async def get_task(
    task_id: str,
    session: AsyncSession = Depends(get_db_session),
    query_service: WorkflowQueryService = Depends(get_workflow_query_service),
) -> TaskExecutionRecord:
    return await query_service.get_task(session, task_id)
