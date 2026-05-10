import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.llm.exceptions import LLMInvalidResponseError, LLMTimeoutError
from backend.llm.schemas import LLMGenerationParams


def test_openai_provider_maps_response_text():
    pytest.importorskip("openai")
    from backend.llm.openai_provider import OpenAILLMProvider

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content='{"strategic_focus":"ok"}'))]

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    async def _run():
        with patch("backend.llm.openai_provider.AsyncOpenAI", return_value=mock_client):
            provider = OpenAILLMProvider(
                api_key="sk-test",
                default_model="gpt-4o-mini",
                default_timeout_seconds=30.0,
            )
            return await provider.generate("hello")

    result = asyncio.run(_run())
    assert result.text == '{"strategic_focus":"ok"}'
    assert result.provider == "openai"
    mock_client.chat.completions.create.assert_awaited_once()


def test_openai_provider_empty_completion_raises():
    pytest.importorskip("openai")
    from backend.llm.openai_provider import OpenAILLMProvider

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="  "))]

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    async def _run():
        with patch("backend.llm.openai_provider.AsyncOpenAI", return_value=mock_client):
            provider = OpenAILLMProvider(
                api_key="sk-test",
                default_model="gpt-4o-mini",
                default_timeout_seconds=30.0,
            )
            return await provider.generate("hello")

    with pytest.raises(LLMInvalidResponseError):
        asyncio.run(_run())


def test_openai_provider_wait_for_timeout():
    pytest.importorskip("openai")
    from backend.llm.openai_provider import OpenAILLMProvider

    async def slow(*_args, **_kwargs):
        await asyncio.sleep(10)
        return MagicMock()

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(side_effect=slow)

    async def _run():
        with patch("backend.llm.openai_provider.AsyncOpenAI", return_value=mock_client):
            provider = OpenAILLMProvider(
                api_key="sk-test",
                default_model="gpt-4o-mini",
                default_timeout_seconds=30.0,
            )
            return await provider.generate("hello", params=LLMGenerationParams(timeout_seconds=0.05))

    with pytest.raises(LLMTimeoutError):
        asyncio.run(_run())


def test_anthropic_provider_maps_response_text():
    pytest.importorskip("anthropic")
    from backend.llm.anthropic_provider import AnthropicLLMProvider

    text_block = MagicMock()
    text_block.type = "text"
    text_block.text = '{"growth_hypothesis":"ok"}'

    mock_message = MagicMock()
    mock_message.content = [text_block]

    mock_client = MagicMock()
    mock_client.messages.create = AsyncMock(return_value=mock_message)

    async def _run():
        with patch("backend.llm.anthropic_provider.AsyncAnthropic", return_value=mock_client):
            provider = AnthropicLLMProvider(
                api_key="sk-ant-test",
                default_model="claude-3-5-sonnet-20240620",
                default_timeout_seconds=30.0,
            )
            return await provider.generate("hello")

    result = asyncio.run(_run())
    assert result.text == '{"growth_hypothesis":"ok"}'
    assert result.provider == "anthropic"
