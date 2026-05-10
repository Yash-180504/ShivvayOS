import pytest

from backend.core.config import Settings
from backend.llm.factory import create_llm_provider
from backend.llm.mock_provider import MockLLMProvider


def test_factory_returns_mock_for_default_settings():
    settings = Settings(default_llm_provider="mock")
    provider = create_llm_provider(settings)
    assert isinstance(provider, MockLLMProvider)


def test_factory_falls_back_to_mock_when_openai_key_missing():
    settings = Settings(default_llm_provider="openai", openai_api_key=None)
    provider = create_llm_provider(settings)
    assert isinstance(provider, MockLLMProvider)


def test_factory_falls_back_to_mock_when_anthropic_key_missing():
    settings = Settings(default_llm_provider="anthropic", anthropic_api_key=None)
    provider = create_llm_provider(settings)
    assert isinstance(provider, MockLLMProvider)


def test_factory_returns_openai_when_configured():
    pytest.importorskip("openai")
    from backend.llm.openai_provider import OpenAILLMProvider

    settings = Settings(
        default_llm_provider="openai",
        openai_api_key="sk-test",
        default_openai_model="gpt-4o-mini",
    )
    provider = create_llm_provider(settings)
    assert isinstance(provider, OpenAILLMProvider)


def test_factory_returns_anthropic_when_configured():
    pytest.importorskip("anthropic")
    from backend.llm.anthropic_provider import AnthropicLLMProvider

    settings = Settings(
        default_llm_provider="anthropic",
        anthropic_api_key="sk-ant-test",
        default_anthropic_model="claude-3-5-sonnet-20240620",
    )
    provider = create_llm_provider(settings)
    assert isinstance(provider, AnthropicLLMProvider)
