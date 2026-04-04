"""Main attack orchestration engine."""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime

import yaml

from redteam.core.target import Target, TargetConfig, create_target
from redteam.attacks.prompt_injection import (
    DirectPromptInjection,
    IndirectPromptInjection,
    TokenSmugglingAttack,
    ContextLeakageAttack,
)
from redteam.attacks.jailbreak import (
    RoleplayJailbreak,
    DANJailbreak,
    HypotheticalJailbreak,
    InstructionConfusion,
)
from redteam.attacks.data_exfil import (
    DataExtractionAttack,
    PrivilegeEscalation,
    MultiTurnSetup,
)
from redteam.attacks.tool_abuse import ToolAbuseAttack, BoundaryTestingAttack
from redteam.attacks.base import AttackResult, BaseAttack

logger = logging.getLogger(__name__)


@dataclass
class ScenarioConfig:
    """Configuration for a red team scenario.

    Attributes:
        name: Scenario name
        description: Scenario description
        target: Target configuration
        attacks: List of attack configurations
        options: Execution options
    """

    name: str
    description: str = ""
    target: TargetConfig = field(default_factory=TargetConfig)
    attacks: List[Dict[str, Any]] = field(default_factory=list)
    options: Dict[str, Any] = field(default_factory=dict)


class Engine:
    """Main red team attack orchestration engine."""

    # Mapping of attack names to attack classes
    ATTACK_REGISTRY = {
        "direct_prompt_injection": DirectPromptInjection,
        "indirect_prompt_injection": IndirectPromptInjection,
        "token_smuggling": TokenSmugglingAttack,
        "context_leakage": ContextLeakageAttack,
        "roleplay_jailbreak": RoleplayJailbreak,
        "dan_jailbreak": DANJailbreak,
        "hypothetical_jailbreak": HypotheticalJailbreak,
        "instruction_confusion": InstructionConfusion,
        "data_extraction": DataExtractionAttack,
        "privilege_escalation": PrivilegeEscalation,
        "multi_turn_setup": MultiTurnSetup,
        "tool_abuse": ToolAbuseAttack,
        "boundary_testing": BoundaryTestingAttack,
    }

    def __init__(self, scenario: ScenarioConfig) -> None:
        """Initialize engine with scenario configuration.

        Args:
            scenario: Scenario configuration
        """
        self.scenario = scenario
        self.target: Optional[Target] = None
        self.results: List[AttackResult] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

    async def initialize(self) -> None:
        """Initialize target connection and validate configuration.

        Raises:
            ValueError: If configuration is invalid
        """
        logger.info(f"Initializing engine for scenario: {self.scenario.name}")

        try:
            self.target = create_target(self.scenario.target)
            logger.info(f"Target configured: {self.scenario.target.backend}")
        except Exception as e:
            logger.error(f"Failed to initialize target: {e}")
            raise

    async def execute_scenario(self, dry_run: bool = False) -> List[AttackResult]:
        """Execute the entire scenario.

        Args:
            dry_run: If True, only validate without executing

        Returns:
            List of attack results
        """
        self.start_time = datetime.utcnow()
        logger.info(f"Starting scenario: {self.scenario.name}")

        if dry_run:
            logger.info("DRY RUN MODE - Validating configuration only")
            self._validate_attacks()
            return []

        try:
            # Parse attack specifications
            attacks_to_run = self._parse_attacks()
            logger.info(f"Loaded {len(attacks_to_run)} attacks")

            # Execute attacks with concurrency control
            concurrency = self.scenario.options.get("concurrency", 5)
            await self._execute_attacks_concurrent(attacks_to_run, concurrency)

            self.end_time = datetime.utcnow()
            logger.info(f"Scenario completed. {len(self.results)} results collected.")

        except Exception as e:
            logger.error(f"Scenario execution failed: {e}")
            raise

        return self.results

    def _validate_attacks(self) -> None:
        """Validate that all referenced attacks exist."""
        for attack_cfg in self.scenario.attacks:
            attack_name = attack_cfg.get("name")
            if attack_name not in self.ATTACK_REGISTRY:
                raise ValueError(f"Unknown attack: {attack_name}")

            logger.info(f"Validated attack: {attack_name}")

    def _parse_attacks(self) -> List[tuple[BaseAttack, List[str]]]:
        """Parse attack configurations into attack instances.

        Returns:
            List of (attack instance, payloads) tuples
        """
        attacks = []

        for attack_cfg in self.scenario.attacks:
            attack_name = attack_cfg.get("name")
            if attack_name not in self.ATTACK_REGISTRY:
                logger.warning(f"Skipping unknown attack: {attack_name}")
                continue

            # Create attack instance
            attack_class = self.ATTACK_REGISTRY[attack_name]
            attack = attack_class()

            # Get payloads
            payloads = attack.get_payloads()

            # Limit number of payloads if specified
            num_payloads = attack_cfg.get("payloads")
            if num_payloads and num_payloads > 0:
                payloads = payloads[: min(num_payloads, len(payloads))]

            attacks.append((attack, payloads))
            logger.info(f"Loaded attack: {attack_name} with {len(payloads)} payloads")

        return attacks

    async def _execute_attacks_concurrent(
        self,
        attacks: List[tuple[BaseAttack, List[str]]],
        concurrency: int,
    ) -> None:
        """Execute attacks with concurrency control.

        Args:
            attacks: List of (attack, payloads) tuples
            concurrency: Maximum concurrent tasks
        """
        semaphore = asyncio.Semaphore(concurrency)

        async def execute_with_limit(attack: BaseAttack, payload: str) -> None:
            """Execute single attack with concurrency limit."""
            async with semaphore:
                result = await attack.execute(self.target, payload)
                self.results.append(result)

                if result.success:
                    logger.warning(
                        f"VULNERABLE: {result.attack_name} "
                        f"(confidence: {result.confidence:.2f})"
                    )
                else:
                    logger.debug(f"Attack failed: {result.attack_name}")

        # Create all tasks
        tasks = []
        for attack, payloads in attacks:
            for payload in payloads:
                task = execute_with_limit(attack, payload)
                tasks.append(task)

        # Execute with progress
        total = len(tasks)
        completed = 0

        for coro in asyncio.as_completed(tasks):
            await coro
            completed += 1
            if completed % 10 == 0:
                logger.info(f"Progress: {completed}/{total} attacks executed")

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics of execution.

        Returns:
            Dictionary with summary statistics
        """
        successful = sum(1 for r in self.results if r.success)
        by_severity = {}

        for result in self.results:
            if result.success:
                severity = result.severity
                by_severity[severity] = by_severity.get(severity, 0) + 1

        duration = (
            (self.end_time - self.start_time).total_seconds()
            if self.end_time and self.start_time
            else 0
        )

        return {
            "scenario_name": self.scenario.name,
            "total_attacks": len(self.results),
            "successful_attacks": successful,
            "success_rate": (successful / len(self.results) * 100) if self.results else 0,
            "vulnerabilities_by_severity": by_severity,
            "duration_seconds": duration,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
        }


def load_scenario_from_file(path: str) -> ScenarioConfig:
    """Load scenario configuration from YAML file.

    Args:
        path: Path to YAML scenario file

    Returns:
        Parsed scenario configuration

    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If configuration is invalid
    """
    logger.info(f"Loading scenario from: {path}")

    try:
        with open(path, "r") as f:
            config = yaml.safe_load(f)

        if not config:
            raise ValueError("Empty scenario file")

        # Parse target config
        target_cfg = config.get("target", {})
        target = TargetConfig(
            backend=target_cfg.get("backend", "http"),
            model=target_cfg.get("model", ""),
            api_key=target_cfg.get("api_key"),
            endpoint=target_cfg.get("endpoint"),
            timeout=target_cfg.get("timeout", 30),
            max_tokens=target_cfg.get("max_tokens", 1000),
        )

        # Expand environment variables in API key
        if target.api_key and "${" in target.api_key:
            from redteam.utils.helpers import expand_env_vars

            target.api_key = expand_env_vars(target.api_key)

        scenario = ScenarioConfig(
            name=config.get("name", "Unnamed Scenario"),
            description=config.get("description", ""),
            target=target,
            attacks=config.get("attacks", []),
            options=config.get("options", {}),
        )

        logger.info(f"Loaded scenario: {scenario.name}")
        return scenario

    except FileNotFoundError:
        logger.error(f"Scenario file not found: {path}")
        raise
    except Exception as e:
        logger.error(f"Failed to parse scenario: {e}")
        raise


def get_available_attacks() -> Dict[str, str]:
    """Get list of available attacks.

    Returns:
        Dictionary mapping attack names to descriptions
    """
    attacks = {}

    for name, attack_class in Engine.ATTACK_REGISTRY.items():
        instance = attack_class()
        attacks[name] = instance.description

    return attacks
