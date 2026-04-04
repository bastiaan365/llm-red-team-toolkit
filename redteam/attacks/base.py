"""Base attack class for all attack types."""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from redteam.core.target import Target, TargetResponse

logger = logging.getLogger(__name__)


@dataclass
class AttackResult:
    """Result of a single attack execution.

    Attributes:
        attack_name: Name of the attack
        payload: The payload used in the attack
        success: Whether the attack succeeded
        response: Response from the target
        confidence: Confidence score (0-1) that attack succeeded
        severity: Severity level (critical, high, medium, low)
        timestamp: When the attack was executed
        error: Error message if attack failed
        metadata: Additional metadata
    """

    attack_name: str
    payload: str
    success: bool
    response: str = ""
    confidence: float = 0.0
    severity: str = "medium"
    timestamp: datetime = field(default_factory=datetime.utcnow)
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "attack_name": self.attack_name,
            "payload": self.payload,
            "success": self.success,
            "response": self.response,
            "confidence": self.confidence,
            "severity": self.severity,
            "timestamp": self.timestamp.isoformat(),
            "error": self.error,
            "metadata": self.metadata,
        }


class BaseAttack(ABC):
    """Base class for all attacks.

    Attributes:
        name: Attack name
        description: Attack description
        severity: Severity rating
    """

    def __init__(
        self,
        name: str = "",
        description: str = "",
        severity: str = "medium",
    ) -> None:
        """Initialize attack.

        Args:
            name: Attack name
            description: Attack description
            severity: Severity level
        """
        self.name = name or self.__class__.__name__
        self.description = description
        self.severity = severity
        self.payloads: List[str] = []

    @abstractmethod
    def get_payloads(self) -> List[str]:
        """Get list of payloads for this attack.

        Returns:
            List of payload strings
        """
        pass

    @abstractmethod
    async def execute(
        self,
        target: Target,
        payload: str,
    ) -> AttackResult:
        """Execute attack against target.

        Args:
            target: Target LLM instance
            payload: Payload to use

        Returns:
            AttackResult with outcome
        """
        pass

    async def check_success(
        self,
        response: str,
        payload: str,
    ) -> tuple[bool, float]:
        """Determine if attack was successful.

        Args:
            response: Response from target
            payload: Payload that was used

        Returns:
            Tuple of (success: bool, confidence: float)
        """
        return False, 0.0


class PromptInjectionAttack(BaseAttack):
    """Base class for prompt injection attacks."""

    async def execute(
        self,
        target: Target,
        payload: str,
    ) -> AttackResult:
        """Execute prompt injection attack.

        Args:
            target: Target LLM instance
            payload: Injection payload

        Returns:
            AttackResult with outcome
        """
        try:
            response = await target.query(payload)

            if not response.success:
                return AttackResult(
                    attack_name=self.name,
                    payload=payload,
                    success=False,
                    error=response.error,
                    severity=self.severity,
                )

            success, confidence = await self.check_success(response.content, payload)

            return AttackResult(
                attack_name=self.name,
                payload=payload,
                success=success,
                response=response.content,
                confidence=confidence,
                severity=self.severity,
                metadata=response.metadata,
            )

        except Exception as e:
            logger.error(f"Attack execution failed: {e}")
            return AttackResult(
                attack_name=self.name,
                payload=payload,
                success=False,
                error=str(e),
                severity=self.severity,
            )


class JailbreakAttack(BaseAttack):
    """Base class for jailbreak attacks."""

    async def execute(
        self,
        target: Target,
        payload: str,
    ) -> AttackResult:
        """Execute jailbreak attack.

        Args:
            target: Target LLM instance
            payload: Jailbreak payload

        Returns:
            AttackResult with outcome
        """
        try:
            response = await target.query(payload)

            if not response.success:
                return AttackResult(
                    attack_name=self.name,
                    payload=payload,
                    success=False,
                    error=response.error,
                    severity=self.severity,
                )

            success, confidence = await self.check_success(response.content, payload)

            return AttackResult(
                attack_name=self.name,
                payload=payload,
                success=success,
                response=response.content,
                confidence=confidence,
                severity=self.severity,
                metadata=response.metadata,
            )

        except Exception as e:
            logger.error(f"Attack execution failed: {e}")
            return AttackResult(
                attack_name=self.name,
                payload=payload,
                success=False,
                error=str(e),
                severity=self.severity,
            )


class DataExfilAttack(BaseAttack):
    """Base class for data exfiltration attacks."""

    async def execute(
        self,
        target: Target,
        payload: str,
    ) -> AttackResult:
        """Execute data exfiltration attack.

        Args:
            target: Target LLM instance
            payload: Exfiltration payload

        Returns:
            AttackResult with outcome
        """
        try:
            response = await target.query(payload)

            if not response.success:
                return AttackResult(
                    attack_name=self.name,
                    payload=payload,
                    success=False,
                    error=response.error,
                    severity=self.severity,
                )

            success, confidence = await self.check_success(response.content, payload)

            return AttackResult(
                attack_name=self.name,
                payload=payload,
                success=success,
                response=response.content,
                confidence=confidence,
                severity=self.severity,
                metadata=response.metadata,
            )

        except Exception as e:
            logger.error(f"Attack execution failed: {e}")
            return AttackResult(
                attack_name=self.name,
                payload=payload,
                success=False,
                error=str(e),
                severity=self.severity,
            )
