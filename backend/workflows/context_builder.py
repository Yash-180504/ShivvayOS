from backend.workflows.schemas import Task, TaskResult, WorkflowContext


class WorkflowContextBuilder:
    """Build compact context packets for agent prompts without exposing full raw state."""

    def build_for_task(self, context: WorkflowContext, task: Task) -> dict[str, object]:
        dependency_results = self._dependency_outputs(context.results, task.dependencies)
        return {
            "execution_history": self._execution_history(context),
            "summarized_context": self._summarize_context(context.results),
            "dependency_outputs": dependency_results,
            "previous_agent_outputs": self._previous_outputs(context.results),
        }

    def _execution_history(self, context: WorkflowContext) -> list[dict[str, str]]:
        return [
            {
                "event_type": event.event_type.value,
                "task_id": event.task_id or "",
                "agent": event.agent or "",
                "status": event.status.value if event.status else "",
                "message": event.message,
            }
            for event in context.timeline[-8:]
        ]

    def _previous_outputs(self, results: list[TaskResult]) -> list[dict[str, object]]:
        return [
            {
                "task_id": result.task_id,
                "agent": result.agent,
                "task_type": result.task_type.value,
                "confidence_score": result.confidence_score,
                "output": result.output.model_dump(mode="json"),
            }
            for result in results[-4:]
        ]

    def _dependency_outputs(self, results: list[TaskResult], dependencies: list[str]) -> list[dict[str, object]]:
        dependency_set = set(dependencies)
        return [
            {
                "task_id": result.task_id,
                "agent": result.agent,
                "task_type": result.task_type.value,
                "output": result.output.model_dump(mode="json"),
            }
            for result in results
            if result.task_id in dependency_set
        ]

    def _summarize_context(self, results: list[TaskResult]) -> str:
        if not results:
            return "No prior agent outputs are available yet."
        parts = []
        for result in results[-4:]:
            output = result.output.model_dump(mode="json")
            key_points = [f"{key}: {value}" for key, value in output.items() if key != "kind"]
            parts.append(f"{result.agent} completed {result.task_type.value}; " + "; ".join(key_points[:3]))
        return "\n".join(parts)


workflow_context_builder = WorkflowContextBuilder()
