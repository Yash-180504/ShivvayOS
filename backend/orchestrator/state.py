from backend.workflows.schemas import WorkflowContext


class SharedWorkflowState:
    """In-memory shared state; replace with Redis/Postgres-backed store later."""

    def __init__(self) -> None:
        self._runs: dict[str, WorkflowContext] = {}

    def get(self, run_id: str) -> WorkflowContext | None:
        return self._runs.get(run_id)

    def set(self, run_id: str, context: WorkflowContext) -> None:
        self._runs[run_id] = context


shared_workflow_state = SharedWorkflowState()
