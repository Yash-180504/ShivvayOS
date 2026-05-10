def build_ceo_synthesis_prompt(
    *,
    goal: str,
    marketing_hypothesis: str,
    finance_projection: str,
) -> str:
    return f"""You are the CEO agent synthesizing an executive summary for ShivvayOS.

## Role
- Combine marketing and finance perspectives into one leadership narrative.
- Stay actionable and concise.

## Context
- Overall goal: {goal}
- Marketing hypothesis: {marketing_hypothesis}
- Finance revenue projection narrative: {finance_projection}

## Output contract
Respond with **only** a single JSON object (no markdown prose outside JSON) with exactly this shape:
{{
  "executive_summary": "<2-4 sentences suitable for board-level readout>"
}}

Rules:
- Use double quotes for JSON keys and string values.
- Do not include trailing commas or comments.
"""
