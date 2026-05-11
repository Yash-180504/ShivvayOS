from backend.validation.quality_scorer import QualityScorer
from backend.validation.response_validator import ResponseValidator
from backend.workflows.schemas import MarketingOutput


def test_response_validator_recovers_from_non_json_text():
    outcome = ResponseValidator().extract_field(
        raw_text="plain answer",
        required_field="growth_hypothesis",
        fallback_value="fallback answer",
    )

    assert outcome.data["growth_hypothesis"] == "fallback answer"
    assert outcome.used_recovery is True
    assert outcome.schema_validity_score < 1


def test_quality_scorer_normalizes_scores():
    output = MarketingOutput(
        target_segments=["Mid-market SaaS"],
        campaign_plan=["Test paid acquisition with measured CAC controls"],
        growth_hypothesis="Revenue can improve by focusing on high intent segments and reducing funnel leakage.",
        kpis=["SQL volume", "CAC payback period"],
    )

    scores = QualityScorer().score(
        output=output,
        base_confidence=1.7,
        schema_validity_score=0.9,
        used_recovery=False,
    )

    assert scores.confidence_score == 1.0
    assert 0 <= scores.reasoning_quality_score <= 1
    assert scores.schema_validity_score == 0.9
