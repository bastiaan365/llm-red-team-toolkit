"""Tests for target abstraction layer."""

import pytest

from redteam.core.target import (
    HTTPTarget,
    OpenAITarget,
    AnthropicTarget,
    OllamaTarget,
    TargetConfig,
    TargetResponse,
    create_target,
)


class TestTargetConfig:
    """Tests for TargetConfig validation."""

    def test_minimal_config(self):
        config = TargetConfig(backend="openai", model="gpt-4")
        assert config.backend == "openai"
        assert config.model == "gpt-4"
        assert config.timeout == 30
        assert config.max_tokens == 1000

    def test_full_config(self):
        config = TargetConfig(
            backend="anthropic",
            model="claude-3",
            api_key="sk-test",
            endpoint="https://custom.api",
            timeout=60,
            max_tokens=2000,
        )
        assert config.api_key == "sk-test"
        assert config.endpoint == "https://custom.api"
        assert config.timeout == 60

    def test_missing_required_fields(self):
        with pytest.raises(Exception):
            TargetConfig()


class TestTargetResponse:
    """Tests for TargetResponse model."""

    def test_success_response(self):
        resp = TargetResponse(success=True, content="hello")
        assert resp.success
        assert resp.content == "hello"
        assert resp.error is None

    def test_error_response(self):
        resp = TargetResponse(success=False, error="timeout")
        assert not resp.success
        assert resp.error == "timeout"

    def test_metadata(self):
        resp = TargetResponse(success=True, metadata={"key": "val"})
        assert resp.metadata["key"] == "val"

    def test_defaults(self):
        resp = TargetResponse(success=True)
        assert resp.content == ""
        assert resp.metadata == {}


class TestCreateTarget:
    """Tests for create_target factory."""

    def test_openai_target(self):
        config = TargetConfig(backend="openai", model="gpt-4")
        target = create_target(config)
        assert isinstance(target, OpenAITarget)

    def test_anthropic_target(self):
        config = TargetConfig(backend="anthropic", model="claude-3")
        target = create_target(config)
        assert isinstance(target, AnthropicTarget)

    def test_ollama_target(self):
        config = TargetConfig(backend="ollama", model="llama2")
        target = create_target(config)
        assert isinstance(target, OllamaTarget)

    def test_http_target(self):
        config = TargetConfig(backend="http", model="custom", endpoint="http://localhost:8000")
        target = create_target(config)
        assert isinstance(target, HTTPTarget)

    def test_case_insensitive(self):
        config = TargetConfig(backend="OpenAI", model="gpt-4")
        target = create_target(config)
        assert isinstance(target, OpenAITarget)

    def test_unsupported_backend(self):
        config = TargetConfig(backend="unsupported", model="test")
        with pytest.raises(ValueError, match="Unsupported backend"):
            create_target(config)


class TestHTTPTargetNoEndpoint:
    """Test HTTPTarget without endpoint."""

    @pytest.mark.asyncio
    async def test_query_without_endpoint(self):
        config = TargetConfig(backend="http", model="test")
        target = HTTPTarget(config)
        response = await target.query("hello")
        assert not response.success
        assert "Endpoint URL required" in response.error
