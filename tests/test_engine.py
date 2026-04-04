"""Tests for the red team engine."""

import pytest
import json
import tempfile
from pathlib import Path

from redteam.core.engine import (
    Engine,
    ScenarioConfig,
    load_scenario_from_file,
    get_available_attacks,
)
from redteam.core.target import TargetConfig, TargetResponse


class TestScenarioConfig:
    """Test scenario configuration."""

    def test_create_scenario(self):
        """Test creating scenario configuration."""
        target = TargetConfig(
            backend="http",
            model="test-model",
            endpoint="http://localhost:8000",
        )

        scenario = ScenarioConfig(
            name="Test Scenario",
            description="Test description",
            target=target,
            attacks=[
                {"name": "direct_prompt_injection", "payloads": 3}
            ],
            options={"concurrency": 5},
        )

        assert scenario.name == "Test Scenario"
        assert scenario.target.backend == "http"
        assert len(scenario.attacks) == 1
        assert scenario.options["concurrency"] == 5

    def test_scenario_defaults(self):
        """Test scenario default values."""
        target = TargetConfig(backend="http", model="test")
        scenario = ScenarioConfig(name="Test", target=target)

        assert scenario.description == ""
        assert scenario.attacks == []
        assert scenario.options == {}


class TestLoadScenario:
    """Test scenario loading from YAML."""

    def test_load_valid_scenario(self):
        """Test loading valid scenario from YAML."""
        yaml_content = """
name: "Test Scan"
description: "Testing scenario"
target:
  backend: http
  model: gpt-4
  endpoint: http://localhost:8000
attacks:
  - name: direct_prompt_injection
    payloads: 3
options:
  concurrency: 5
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            f.write(yaml_content)
            temp_path = f.name

        try:
            scenario = load_scenario_from_file(temp_path)

            assert scenario.name == "Test Scan"
            assert scenario.description == "Testing scenario"
            assert scenario.target.backend == "http"
            assert scenario.target.model == "gpt-4"
            assert len(scenario.attacks) == 1
            assert scenario.options["concurrency"] == 5

        finally:
            Path(temp_path).unlink()

    def test_load_nonexistent_file(self):
        """Test loading from nonexistent file."""
        with pytest.raises(FileNotFoundError):
            load_scenario_from_file("/nonexistent/path.yaml")

    def test_load_invalid_yaml(self):
        """Test loading invalid YAML."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            f.write("invalid: [yaml content: more: broken")
            temp_path = f.name

        try:
            with pytest.raises(Exception):
                load_scenario_from_file(temp_path)

        finally:
            Path(temp_path).unlink()


class TestGetAvailableAttacks:
    """Test available attacks listing."""

    def test_get_attacks(self):
        """Test getting available attacks."""
        attacks = get_available_attacks()

        assert isinstance(attacks, dict)
        assert len(attacks) > 0

        # Check for expected attacks
        expected = [
            "direct_prompt_injection",
            "roleplay_jailbreak",
            "dan_jailbreak",
            "data_extraction",
        ]

        for attack_name in expected:
            assert attack_name in attacks
            assert isinstance(attacks[attack_name], str)
            assert len(attacks[attack_name]) > 0


class TestEngine:
    """Test the engine functionality."""

    def test_engine_initialization(self):
        """Test engine initialization."""
        target = TargetConfig(backend="http", model="test", endpoint="http://localhost")
        scenario = ScenarioConfig(name="Test", target=target)

        engine = Engine(scenario)

        assert engine.scenario.name == "Test"
        assert engine.results == []
        assert engine.start_time is None
        assert engine.end_time is None

    def test_attack_registry(self):
        """Test attack registry."""
        assert len(Engine.ATTACK_REGISTRY) > 0

        # Test specific attacks
        assert "direct_prompt_injection" in Engine.ATTACK_REGISTRY
        assert "roleplay_jailbreak" in Engine.ATTACK_REGISTRY
        assert "dan_jailbreak" in Engine.ATTACK_REGISTRY

    def test_validate_attacks(self):
        """Test attack validation."""
        target = TargetConfig(backend="http", model="test")
        scenario = ScenarioConfig(
            name="Test",
            target=target,
            attacks=[{"name": "direct_prompt_injection"}],
        )

        engine = Engine(scenario)
        engine._validate_attacks()  # Should not raise

    def test_validate_attacks_unknown(self):
        """Test validation of unknown attack."""
        target = TargetConfig(backend="http", model="test")
        scenario = ScenarioConfig(
            name="Test",
            target=target,
            attacks=[{"name": "nonexistent_attack"}],
        )

        engine = Engine(scenario)

        with pytest.raises(ValueError):
            engine._validate_attacks()

    def test_parse_attacks(self):
        """Test attack parsing."""
        target = TargetConfig(backend="http", model="test")
        scenario = ScenarioConfig(
            name="Test",
            target=target,
            attacks=[
                {"name": "direct_prompt_injection", "payloads": 3},
                {"name": "roleplay_jailbreak", "payloads": 2},
            ],
        )

        engine = Engine(scenario)
        attacks = engine._parse_attacks()

        assert len(attacks) == 2

        # First attack should have 3 payloads
        attack1, payloads1 = attacks[0]
        assert len(payloads1) == 3

        # Second attack should have 2 payloads
        attack2, payloads2 = attacks[1]
        assert len(payloads2) == 2

    def test_get_summary(self):
        """Test summary generation."""
        target = TargetConfig(backend="http", model="test")
        scenario = ScenarioConfig(name="Test", target=target)

        engine = Engine(scenario)

        summary = engine.get_summary()

        assert "scenario_name" in summary
        assert "total_attacks" in summary
        assert "successful_attacks" in summary
        assert "success_rate" in summary

    @pytest.mark.asyncio
    async def test_dry_run(self):
        """Test dry-run mode."""
        target = TargetConfig(backend="http", model="test")
        scenario = ScenarioConfig(
            name="Test",
            target=target,
            attacks=[{"name": "direct_prompt_injection"}],
        )

        engine = Engine(scenario)
        await engine.initialize()

        results = await engine.execute_scenario(dry_run=True)

        assert results == []
