from dataclasses import dataclass

from pydantic import BaseModel


@dataclass(frozen=True)
class QualityScores:
    confidence_score: float
    reasoning_quality_score: float
    schema_validity_score: float


class QualityScorer:
    def score(
        self,
        *,
        output: BaseModel,
        base_confidence: float,
        schema_validity_score: float,
        used_recovery: bool,
    ) -> QualityScores:
        confidence = self.normalize_confidence(base_confidence)
        reasoning_quality = self._reasoning_quality(output)
        if used_recovery:
            confidence -= 0.08
            reasoning_quality -= 0.05
        return QualityScores(
            confidence_score=self._clamp(confidence),
            reasoning_quality_score=self._clamp(reasoning_quality),
            schema_validity_score=self._clamp(schema_validity_score),
        )

    def normalize_confidence(self, confidence: float | None) -> float:
        if confidence is None:
            return 0.70
        return self._clamp(confidence)

    def _reasoning_quality(self, output: BaseModel) -> float:
        data = output.model_dump(mode="json")
        text_values = [str(value) for value in data.values() if isinstance(value, str)]
        list_values = [value for value in data.values() if isinstance(value, list)]
        score = 0.62
        if any(len(value.split()) >= 10 for value in text_values):
            score += 0.12
        if sum(len(value) for value in list_values) >= 6:
            score += 0.12
        if any("risk" in str(value).lower() or "feasib" in str(value).lower() for value in data.values()):
            score += 0.06
        return score

    def _clamp(self, value: float) -> float:
        return round(max(0.0, min(1.0, value)), 2)
