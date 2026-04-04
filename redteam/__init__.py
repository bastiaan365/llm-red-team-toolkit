"""LLM Red Team Toolkit - Automated security testing for LLM applications."""

__version__ = "0.1.0"
__author__ = "Bastiaan"

from redteam.core.engine import Engine
from redteam.core.target import Target, TargetConfig
from redteam.attacks.base import AttackResult

__all__ = [
    "Engine",
    "Target",
    "TargetConfig",
    "AttackResult",
]
