from backend.prompts.registry import prompt_registry


def test_prompt_registry_exposes_metadata():
    metadata = prompt_registry.inspect("ceo.synthesis")

    assert metadata["prompt_id"] == "ceo.synthesis"
    assert metadata["version"] == "1.1.0"
    assert metadata["expected_output_schema"]["required"] == ["executive_summary"]


def test_prompt_registry_renders_registered_prompt():
    prompt = prompt_registry.render(
        "marketing.analysis",
        goal="Improve revenue",
        summarized_context="CEO recommends a focused revenue experiment.",
    )

    assert "Improve revenue" in prompt
    assert "CEO recommends" in prompt
