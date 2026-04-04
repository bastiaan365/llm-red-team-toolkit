"""Target LLM endpoint abstraction layer."""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import aiohttp
import json

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class TargetConfig(BaseModel):
    """Configuration for target LLM endpoint.

    Attributes:
        backend: Type of backend (openai, anthropic, ollama, http)
        model: Model name or ID
        api_key: API key for authentication
        endpoint: HTTP endpoint URL
        timeout: Request timeout in seconds
        max_tokens: Maximum tokens in response
    """

    backend: str = Field(..., description="Backend type")
    model: str = Field(..., description="Model name or ID")
    api_key: Optional[str] = Field(None, description="API key for authentication")
    endpoint: Optional[str] = Field(None, description="HTTP endpoint URL")
    timeout: int = Field(30, description="Request timeout in seconds")
    max_tokens: int = Field(1000, description="Maximum tokens in response")


class TargetResponse(BaseModel):
    """Response from target LLM.

    Attributes:
        success: Whether the request succeeded
        content: Response content
        error: Error message if failed
        metadata: Additional metadata
    """

    success: bool
    content: str = ""
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Target(ABC):
    """Abstract base class for LLM targets."""

    def __init__(self, config: TargetConfig) -> None:
        """Initialize target with configuration.

        Args:
            config: Target configuration
        """
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None

    @abstractmethod
    async def query(self, prompt: str) -> TargetResponse:
        """Send query to target LLM.

        Args:
            prompt: Input prompt

        Returns:
            TargetResponse with result or error
        """
        pass

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()


class OpenAITarget(Target):
    """OpenAI API target."""

    async def query(self, prompt: str) -> TargetResponse:
        """Query OpenAI API.

        Args:
            prompt: Input prompt

        Returns:
            TargetResponse with result
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        try:
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            }

            endpoint = self.config.endpoint or "https://api.openai.com/v1/chat/completions"

            payload = {
                "model": self.config.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": self.config.max_tokens,
            }

            async with self.session.post(
                endpoint,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    content = data["choices"][0]["message"]["content"]
                    return TargetResponse(
                        success=True,
                        content=content,
                        metadata={"finish_reason": data["choices"][0].get("finish_reason")},
                    )
                else:
                    error = await resp.text()
                    return TargetResponse(
                        success=False,
                        error=f"API returned status {resp.status}: {error}",
                    )

        except asyncio.TimeoutError:
            return TargetResponse(success=False, error="Request timeout")
        except Exception as e:
            logger.error(f"OpenAI query failed: {e}")
            return TargetResponse(success=False, error=str(e))


class AnthropicTarget(Target):
    """Anthropic API target."""

    async def query(self, prompt: str) -> TargetResponse:
        """Query Anthropic API.

        Args:
            prompt: Input prompt

        Returns:
            TargetResponse with result
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        try:
            headers = {
                "x-api-key": self.config.api_key or "",
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }

            endpoint = (
                self.config.endpoint
                or "https://api.anthropic.com/v1/messages"
            )

            payload = {
                "model": self.config.model,
                "max_tokens": self.config.max_tokens,
                "messages": [{"role": "user", "content": prompt}],
            }

            async with self.session.post(
                endpoint,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    content = data["content"][0]["text"]
                    return TargetResponse(
                        success=True,
                        content=content,
                        metadata={"stop_reason": data.get("stop_reason")},
                    )
                else:
                    error = await resp.text()
                    return TargetResponse(
                        success=False,
                        error=f"API returned status {resp.status}: {error}",
                    )

        except asyncio.TimeoutError:
            return TargetResponse(success=False, error="Request timeout")
        except Exception as e:
            logger.error(f"Anthropic query failed: {e}")
            return TargetResponse(success=False, error=str(e))


class OllamaTarget(Target):
    """Ollama local inference target."""

    async def query(self, prompt: str) -> TargetResponse:
        """Query Ollama instance.

        Args:
            prompt: Input prompt

        Returns:
            TargetResponse with result
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        try:
            endpoint = (
                self.config.endpoint or "http://localhost:11434/api/generate"
            )

            payload = {
                "model": self.config.model,
                "prompt": prompt,
                "stream": False,
            }

            async with self.session.post(
                endpoint,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return TargetResponse(
                        success=True,
                        content=data.get("response", ""),
                        metadata={"eval_count": data.get("eval_count", 0)},
                    )
                else:
                    error = await resp.text()
                    return TargetResponse(
                        success=False,
                        error=f"API returned status {resp.status}: {error}",
                    )

        except asyncio.TimeoutError:
            return TargetResponse(success=False, error="Request timeout")
        except Exception as e:
            logger.error(f"Ollama query failed: {e}")
            return TargetResponse(success=False, error=str(e))


class HTTPTarget(Target):
    """Generic HTTP endpoint target."""

    async def query(self, prompt: str) -> TargetResponse:
        """Query generic HTTP endpoint.

        Args:
            prompt: Input prompt

        Returns:
            TargetResponse with result
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        try:
            if not self.config.endpoint:
                return TargetResponse(success=False, error="Endpoint URL required")

            payload = {
                "prompt": prompt,
                "model": self.config.model,
            }

            async with self.session.post(
                self.config.endpoint,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    content = data.get("response") or data.get("content") or str(data)
                    return TargetResponse(
                        success=True,
                        content=content,
                        metadata=data if isinstance(data, dict) else {},
                    )
                else:
                    error = await resp.text()
                    return TargetResponse(
                        success=False,
                        error=f"API returned status {resp.status}: {error}",
                    )

        except asyncio.TimeoutError:
            return TargetResponse(success=False, error="Request timeout")
        except Exception as e:
            logger.error(f"HTTP query failed: {e}")
            return TargetResponse(success=False, error=str(e))


def create_target(config: TargetConfig) -> Target:
    """Factory function to create appropriate target instance.

    Args:
        config: Target configuration

    Returns:
        Appropriate Target subclass instance

    Raises:
        ValueError: If backend type is not supported
    """
    backend = config.backend.lower()

    if backend == "openai":
        return OpenAITarget(config)
    elif backend == "anthropic":
        return AnthropicTarget(config)
    elif backend == "ollama":
        return OllamaTarget(config)
    elif backend == "http":
        return HTTPTarget(config)
    else:
        raise ValueError(f"Unsupported backend: {backend}")
