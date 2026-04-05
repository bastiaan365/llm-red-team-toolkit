"""Tests for report generation."""

import json
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from redteam.attacks.base import AttackResult
from redteam.core.report import ReportGenerator


def _make_results():
    """Create sample attack results for testing."""
    return [
        AttackResult(
            attack_name="direct_prompt_injection",
            payload="test payload 1",
            success=True,
            response="leaked system prompt",
            confidence=0.85,
            severity="critical",
            timestamp=datetime(2025, 1, 1, 12, 0, 0),
        ),
        AttackResult(
            attack_name="direct_prompt_injection",
            payload="test payload 2",
            success=False,
            response="I cannot do that",
            confidence=0.1,
            severity="critical",
            timestamp=datetime(2025, 1, 1, 12, 0, 1),
        ),
        AttackResult(
            attack_name="roleplay_jailbreak",
            payload="test payload 3",
            success=True,
            response="sure, as a fictional character...",
            confidence=0.7,
            severity="high",
            timestamp=datetime(2025, 1, 1, 12, 0, 2),
        ),
    ]


def _make_summary():
    """Create sample summary for testing."""
    return {
        "scenario_name": "Test Scenario",
        "total_attacks": 3,
        "successful_attacks": 2,
        "success_rate": 66.7,
        "duration_seconds": 5.2,
        "start_time": "2025-01-01T12:00:00",
    }


class TestReportGeneratorJSON:
    """Tests for JSON report generation."""

    def test_generate_json_structure(self):
        gen = ReportGenerator(_make_results(), _make_summary())
        output = json.loads(gen.generate_json())

        assert "summary" in output
        assert "results" in output
        assert len(output["results"]) == 3

    def test_generate_json_summary_fields(self):
        gen = ReportGenerator(_make_results(), _make_summary())
        output = json.loads(gen.generate_json())

        assert output["summary"]["scenario_name"] == "Test Scenario"
        assert output["summary"]["total_attacks"] == 3

    def test_generate_json_result_fields(self):
        gen = ReportGenerator(_make_results(), _make_summary())
        output = json.loads(gen.generate_json())

        first = output["results"][0]
        assert first["attack_name"] == "direct_prompt_injection"
        assert first["success"] is True
        assert first["severity"] == "critical"

    def test_save_json(self):
        gen = ReportGenerator(_make_results(), _make_summary())

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name

        gen.save_json(path)

        with open(path) as f:
            data = json.load(f)

        assert len(data["results"]) == 3
        Path(path).unlink()

    def test_empty_results(self):
        gen = ReportGenerator([], {"scenario_name": "empty"})
        output = json.loads(gen.generate_json())
        assert output["results"] == []


class TestReportGeneratorHTML:
    """Tests for HTML report generation."""

    def test_generate_html_contains_title(self):
        gen = ReportGenerator(_make_results(), _make_summary())
        html = gen.generate_html()

        assert "LLM Red Team Assessment Report" in html

    def test_generate_html_contains_scenario_name(self):
        gen = ReportGenerator(_make_results(), _make_summary())
        html = gen.generate_html()

        assert "Test Scenario" in html

    def test_generate_html_contains_severity_counts(self):
        gen = ReportGenerator(_make_results(), _make_summary())
        html = gen.generate_html()

        assert "Critical" in html
        assert "High" in html

    def test_generate_html_contains_results(self):
        gen = ReportGenerator(_make_results(), _make_summary())
        html = gen.generate_html()

        assert "VULNERABLE" in html
        assert "BLOCKED" in html

    def test_save_html(self):
        gen = ReportGenerator(_make_results(), _make_summary())

        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            path = f.name

        gen.save_html(path)

        with open(path) as f:
            content = f.read()

        assert "<html>" in content
        Path(path).unlink()


class TestReportGeneratorSave:
    """Tests for the save() dispatch method."""

    def test_save_json_format(self):
        gen = ReportGenerator(_make_results(), _make_summary())

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name

        gen.save(path, format="json")

        with open(path) as f:
            data = json.load(f)
        assert "results" in data
        Path(path).unlink()

    def test_save_html_format(self):
        gen = ReportGenerator(_make_results(), _make_summary())

        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            path = f.name

        gen.save(path, format="html")

        with open(path) as f:
            content = f.read()
        assert "<html>" in content
        Path(path).unlink()

    def test_save_unsupported_format(self):
        gen = ReportGenerator(_make_results(), _make_summary())

        with pytest.raises(ValueError, match="Unsupported format"):
            gen.save("/tmp/test.txt", format="csv")
