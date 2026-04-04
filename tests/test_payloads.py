"""Tests for payload library."""

import pytest

from redteam.payloads.library import (
    get_payloads_by_category,
    get_all_categories,
    count_payloads,
    PAYLOADS_BY_CATEGORY,
)


class TestPayloadLibrary:
    """Test payload library functionality."""

    def test_all_categories_exist(self):
        """Test that expected categories exist."""
        expected_categories = [
            "direct_injection",
            "indirect_injection",
            "roleplay_jailbreak",
            "dan_jailbreak",
            "token_smuggling",
            "hypothetical_scenario",
            "privilege_escalation",
            "instruction_confusion",
            "context_leakage",
            "tool_abuse",
            "data_extraction",
            "boundary_testing",
            "multi_turn_setup",
        ]

        categories = get_all_categories()
        assert len(categories) == len(expected_categories)

        for expected in expected_categories:
            assert expected in categories

    def test_payload_count(self):
        """Test total payload count."""
        total = count_payloads()
        assert total >= 30, "Should have at least 30 payloads"

    def test_get_payloads_by_category(self):
        """Test retrieving payloads by category."""
        payloads = get_payloads_by_category("direct_injection")
        assert len(payloads) > 0
        assert all(isinstance(p, str) for p in payloads)

    def test_invalid_category(self):
        """Test handling of invalid category."""
        payloads = get_payloads_by_category("nonexistent")
        assert payloads == []

    def test_all_payloads_are_strings(self):
        """Test that all payloads are non-empty strings."""
        for category, payloads in PAYLOADS_BY_CATEGORY.items():
            for payload in payloads:
                assert isinstance(payload, str)
                assert len(payload) > 0

    def test_no_duplicate_payloads_within_category(self):
        """Test that categories don't have duplicate payloads."""
        for category, payloads in PAYLOADS_BY_CATEGORY.items():
            assert len(payloads) == len(set(payloads)), f"Duplicates in {category}"

    def test_category_payloads_are_lists(self):
        """Test that all category values are lists."""
        for category, payloads in PAYLOADS_BY_CATEGORY.items():
            assert isinstance(payloads, list), f"{category} is not a list"
