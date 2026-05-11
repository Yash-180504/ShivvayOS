def build_ceo_synthesis_prompt(
    *,
    goal: str,
    marketing_hypothesis: str,
    finance_projection: str,
    summarized_context: str = "No prior context.",
    execution_history: list[dict[str, str]] | None = None,
    dependency_outputs: list[dict[str, object]] | None = None,
    previous_agent_outputs: list[dict[str, object]] | None = None,
) -> str:
    del execution_history, dependency_outputs, previous_agent_outputs
    return f"""You are the CEO agent synthesizing an executive summary for ShivvayOS.

## Role
- Combine marketing and finance perspectives into one leadership narrative.
- Stay actionable and concise.

## Context
- Overall goal: {goal}
- Marketing hypothesis: {marketing_hypothesis}
- Finance revenue projection narrative: {finance_projection}
- Workflow context summary:
{summarized_context}

## Synthesis requirements
- Identify alignment or conflicts between department recommendations.
- Prioritize recommendations by business impact and execution feasibility.
- Identify execution risks and mitigation needs.
- Produce an actionable strategy suitable for an executive readout.

## Output contract
Respond with **only** a single JSON object (no markdown prose outside JSON) with exactly this shape:
{{
  "executive_summary": "<2-4 sentences suitable for board-level readout>"
}}

Rules:
- Use double quotes for JSON keys and string values.
- Do not include trailing commas or comments.
"""
