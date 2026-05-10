import logging

from backend.workflows.schemas import Task, TaskStatus, WorkflowContext, WorkflowEvent, WorkflowEventType


class WorkflowLogger:
    """Centralized workflow/task observability hooks."""

    def __init__(self) -> None:
        self._logger = logging.getLogger("shivvayos.workflow")

    def workflow_started(self, context: WorkflowContext) -> None:
        context.status = TaskStatus.RUNNING
        context.add_event(
            WorkflowEvent(
                event_type=WorkflowEventType.WORKFLOW_STARTED,
                status=TaskStatus.RUNNING,
                message=f"Workflow started for goal: {context.goal}",
            )
        )
        self._logger.info("workflow_started run_id=%s goal=%s", context.run_id, context.goal)

    def task_started(self, context: WorkflowContext, task: Task) -> None:
        context.add_event(
            WorkflowEvent(
                event_type=WorkflowEventType.TASK_STARTED,
                task_id=task.task_id,
                agent=task.agent,
                status=TaskStatus.RUNNING,
                message=f"Task started: {task.task_type}",
            )
        )
        self._logger.info("task_started run_id=%s task_id=%s agent=%s", context.run_id, task.task_id, task.agent)

    def task_completed(self, context: WorkflowContext, task: Task) -> None:
        context.add_event(
            WorkflowEvent(
                event_type=WorkflowEventType.TASK_COMPLETED,
                task_id=task.task_id,
                agent=task.agent,
                status=TaskStatus.COMPLETED,
                message=f"Task completed: {task.task_type}",
            )
        )
        self._logger.info("task_completed run_id=%s task_id=%s", context.run_id, task.task_id)

    def task_failed(self, context: WorkflowContext, task: Task, error_message: str) -> None:
        context.add_event(
            WorkflowEvent(
                event_type=WorkflowEventType.TASK_FAILED,
                task_id=task.task_id,
                agent=task.agent,
                status=TaskStatus.FAILED,
                message=f"Task failed: {task.task_type}. Error: {error_message}",
            )
        )
        self._logger.exception(
            "task_failed run_id=%s task_id=%s error=%s",
            context.run_id,
            task.task_id,
            error_message,
        )

    def workflow_completed(self, context: WorkflowContext) -> None:
        context.status = TaskStatus.COMPLETED
        context.add_event(
            WorkflowEvent(
                event_type=WorkflowEventType.WORKFLOW_COMPLETED,
                status=TaskStatus.COMPLETED,
                message="Workflow completed successfully",
            )
        )
        self._logger.info("workflow_completed run_id=%s", context.run_id)

    def workflow_failed(self, context: WorkflowContext, error_message: str) -> None:
        context.status = TaskStatus.FAILED
        context.add_event(
            WorkflowEvent(
                event_type=WorkflowEventType.WORKFLOW_FAILED,
                status=TaskStatus.FAILED,
                message=f"Workflow failed: {error_message}",
            )
        )
        self._logger.exception("workflow_failed run_id=%s error=%s", context.run_id, error_message)
