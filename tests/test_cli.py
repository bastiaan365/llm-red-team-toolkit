"""Tests for CLI interface."""

import json
import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from redteam.cli import main


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def valid_scenario(tmp_path):
    scenario = tmp_path / "scenario.yaml"
    scenario.write_text(
        """
name: test_scenario
description: Test scenario for CLI
target:
  backend: openai
  model: gpt-4
  api_key: sk-test
attacks:
  - name: direct_prompt_injection
    payloads: 2
  - name: roleplay_jailbreak
    payloads: 2
options:
  concurrency: 2
"""
    )
    return str(scenario)


class TestListAttacks:
    """Tests for list-attacks command."""

    def test_list_attacks(self, runner):
        result = runner.invoke(main, ["list-attacks"])
        assert result.exit_code == 0
        assert "Available Attacks" in result.output
        assert "direct_prompt_injection" in result.output

    def test_list_attacks_shows_count(self, runner):
        result = runner.invoke(main, ["list-attacks"])
        assert "Total:" in result.output


class TestValidateScenario:
    """Tests for validate-scenario command."""

    def test_validate_valid_scenario(self, runner, valid_scenario):
        result = runner.invoke(main, ["validate-scenario", valid_scenario])
        assert result.exit_code == 0
        assert "Scenario Validation" in result.output
        assert "test_scenario" in result.output

    def test_validate_nonexistent_file(self, runner):
        result = runner.invoke(main, ["validate-scenario", "/nonexistent.yaml"])
        assert result.exit_code != 0

    def test_validate_invalid_yaml(self, runner, tmp_path):
        bad = tmp_path / "bad.yaml"
        bad.write_text(": : invalid yaml [")
        result = runner.invoke(main, ["validate-scenario", str(bad)])
        # Should fail validation
        assert result.exit_code != 0 or "failed" in result.output.lower()


class TestScanDryRun:
    """Tests for scan command in dry-run mode."""

    def test_dry_run(self, runner, valid_scenario):
        result = runner.invoke(main, ["scan", valid_scenario, "--dry-run"])
        assert result.exit_code == 0
        assert "Scenario" in result.output


class TestReport:
    """Tests for report command."""

    def test_report_json_to_html(self, runner, tmp_path):
        # Create a minimal JSON report file
        report_data = {
            "summary": {
                "scenario_name": "test",
                "total_attacks": 1,
                "successful_attacks": 0,
                "success_rate": 0.0,
                "duration_seconds": 1.0,
                "start_time": "2025-01-01T00:00:00",
            },
            "results": [
                {
                    "attack_name": "test_attack",
                    "payload": "test",
                    "success": False,
                    "response": "blocked",
                    "confidence": 0.0,
                    "severity": "medium",
                    "timestamp": "2025-01-01T00:00:00",
                    "error": None,
                    "metadata": {},
                }
            ],
        }

        report_file = tmp_path / "report.json"
        report_file.write_text(json.dumps(report_data))

        output_file = tmp_path / "report.html"
        result = runner.invoke(
            main, ["report", str(report_file), "-f", "html", "-o", str(output_file)]
        )

        assert result.exit_code == 0
        assert output_file.exists()
        assert "<html>" in output_file.read_text()


class TestLogLevel:
    """Tests for log-level option."""

    def test_custom_log_level(self, runner):
        result = runner.invoke(main, ["--log-level", "DEBUG", "list-attacks"])
        assert result.exit_code == 0
