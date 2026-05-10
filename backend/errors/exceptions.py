from datetime import datetime, timezone


class AppError(Exception):
    def __init__(self, error_code: str, error_message: str, status_code: int = 400) -> None:
        super().__init__(error_message)
        self.error_code = error_code
        self.error_message = error_message
        self.status_code = status_code
        self.failed_at = datetime.now(timezone.utc)


class NotFoundError(AppError):
    def __init__(self, entity: str, entity_id: str) -> None:
        super().__init__(
            error_code=f"{entity.upper()}_NOT_FOUND",
            error_message=f"{entity} not found: {entity_id}",
            status_code=404,
        )


class WorkflowExecutionError(AppError):
    def __init__(self, run_id: str, reason: str) -> None:
        super().__init__(
            error_code="WORKFLOW_EXECUTION_FAILED",
            error_message=f"Workflow {run_id} failed: {reason}",
            status_code=500,
        )
