"""Tests for utility helper functions."""

import json
import logging
import os

import pytest

from redteam.utils.helpers import (
    expand_env_vars,
    get_severity_color,
    load_json_safe,
    sanitize_for_html,
    setup_logging,
    truncate_string,
)


class TestSetupLogging:
    """Tests for setup_logging."""

    def test_default_level(self):
        root = logging.getLogger()
        root.handlers.clear()
        root.setLevel(logging.NOTSET)
        setup_logging()
        assert root.level == logging.INFO

    def test_debug_level(self):
        root = logging.getLogger()
        root.handlers.clear()
        root.setLevel(logging.NOTSET)
        setup_logging("DEBUG")
        assert root.level == logging.DEBUG

    def test_case_insensitive(self):
        root = logging.getLogger()
        root.handlers.clear()
        root.setLevel(logging.NOTSET)
        setup_logging("warning")
        assert root.level == logging.WARNING


class TestExpandEnvVars:
    """Tests for expand_env_vars."""

    def test_expand_single_var(self, monkeypatch):
        monkeypatch.setenv("TEST_VAR", "hello")
        assert expand_env_vars("${TEST_VAR}") == "hello"

    def test_expand_multiple_vars(self, monkeypatch):
        monkeypatch.setenv("A", "foo")
        monkeypatch.setenv("B", "bar")
        assert expand_env_vars("${A}-${B}") == "foo-bar"

    def test_no_vars(self):
        assert expand_env_vars("plain text") == "plain text"

    def test_missing_var_raises(self, monkeypatch):
        monkeypatch.delenv("NONEXISTENT_VAR_XYZ", raising=False)
        with pytest.raises(ValueError, match="Environment variable not set"):
            expand_env_vars("${NONEXISTENT_VAR_XYZ}")

    def test_empty_string(self):
        assert expand_env_vars("") == ""


class TestLoadJsonSafe:
    """Tests for load_json_safe."""

    def test_valid_json(self):
        assert load_json_safe('{"key": "value"}') == {"key": "value"}

    def test_invalid_json(self):
        assert load_json_safe("not json") == {}

    def test_empty_string(self):
        assert load_json_safe("") == {}

    def test_nested_json(self):
        result = load_json_safe('{"a": {"b": 1}}')
        assert result["a"]["b"] == 1


class TestTruncateString:
    """Tests for truncate_string."""

    def test_short_string_unchanged(self):
        assert truncate_string("hello", 100) == "hello"

    def test_exact_length(self):
        assert truncate_string("hello", 5) == "hello"

    def test_truncation(self):
        result = truncate_string("a" * 200, 100)
        assert len(result) == 100
        assert result.endswith("...")

    def test_default_length(self):
        long_str = "x" * 200
        result = truncate_string(long_str)
        assert len(result) == 100


class TestSanitizeForHtml:
    """Tests for sanitize_for_html."""

    def test_escapes_ampersand(self):
        assert sanitize_for_html("a & b") == "a &amp; b"

    def test_escapes_angle_brackets(self):
        assert sanitize_for_html("<script>") == "&lt;script&gt;"

    def test_escapes_quotes(self):
        assert sanitize_for_html('"hello\'') == "&quot;hello&#39;"

    def test_no_escaping_needed(self):
        assert sanitize_for_html("plain text") == "plain text"

    def test_all_special_chars(self):
        result = sanitize_for_html('<a href="x">&\'')
        assert "&lt;" in result
        assert "&gt;" in result
        assert "&amp;" in result
        assert "&quot;" in result
        assert "&#39;" in result


class TestGetSeverityColor:
    """Tests for get_severity_color."""

    def test_critical(self):
        assert get_severity_color("critical") == "#dc3545"

    def test_high(self):
        assert get_severity_color("high") == "#fd7e14"

    def test_medium(self):
        assert get_severity_color("medium") == "#ffc107"

    def test_low(self):
        assert get_severity_color("low") == "#28a745"

    def test_info(self):
        assert get_severity_color("info") == "#17a2b8"

    def test_unknown_returns_default(self):
        assert get_severity_color("unknown") == "#6c757d"

    def test_case_insensitive(self):
        assert get_severity_color("CRITICAL") == "#dc3545"
