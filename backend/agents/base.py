from abc import ABC, abstractmethod

from backend.llm.base import BaseLLMProvider
from backend.validation.quality_scorer import QualityScorer
from backend.validation.response_validator import ResponseValidator
from backend.workflows.schemas import Task, TaskResult, WorkflowContext


class BaseAgent(ABC):
    name: str
    role: str

    def __init__(self, llm_provider: BaseLLMProvider) -> None:
        self.llm_provider = llm_provider
        self.response_validator = ResponseValidator()
        self.quality_scorer = QualityScorer()

    @abstractmethod
    async def execute(self, task: Task, context: WorkflowContext) -> TaskResult:
        """Execute an assigned task and return deterministic structured output."""
