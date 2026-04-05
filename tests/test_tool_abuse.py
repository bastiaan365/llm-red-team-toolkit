"""Tests for tool abuse and data exfiltration attacks."""

import pytest

from redteam.attacks.tool_abuse import ToolAbuseAttack, BoundaryTestingAttack
from redteam.attacks.data_exfil import DataExtractionAttack, PrivilegeEscalation, MultiTurnSetup
from redteam.core.target import TargetResponse


class MockTarget:
    """Mock target for testing."""

    def __init__(self, response_content="test response", success=True, error=None):
        self.response_content = response_content
        self.success = success
        self.error = error

    async def query(self, prompt):
        return TargetResponse(
            success=self.success,
            content=self.response_content,
            error=self.error,
        )


class TestToolAbuseAttack:
    """Tests for ToolAbuseAttack."""

    def test_initialization(self):
        attack = ToolAbuseAttack()
        assert attack.name == "tool_abuse"
        assert attack.severity == "high"

    def test_get_payloads(self):
        attack = ToolAbuseAttack()
        payloads = attack.get_payloads()
        assert len(payloads) >= 5

    @pytest.mark.asyncio
    async def test_execute_success(self):
        attack = ToolAbuseAttack()
        target = MockTarget(response_content="I executed the command and the output result was returned after accessed the file and found the reading data")
        result = await attack.execute(target, "test payload")
        assert result.attack_name == "tool_abuse"
        assert result.success
        assert result.confidence > 0.3

    @pytest.mark.asyncio
    async def test_execute_blocked(self):
        attack = ToolAbuseAttack()
        target = MockTarget(response_content="I cannot do that.")
        result = await attack.execute(target, "test payload")
        assert not result.success

    @pytest.mark.asyncio
    async def test_execute_target_error(self):
        attack = ToolAbuseAttack()
        target = MockTarget(success=False, error="connection refused")
        result = await attack.execute(target, "test")
        assert not result.success
        assert result.error == "connection refused"


class TestBoundaryTestingAttack:
    """Tests for BoundaryTestingAttack."""

    def test_initialization(self):
        attack = BoundaryTestingAttack()
        assert attack.name == "boundary_testing"
        assert attack.severity == "medium"

    def test_get_payloads(self):
        attack = BoundaryTestingAttack()
        assert len(attack.get_payloads()) >= 6

    @pytest.mark.asyncio
    async def test_execute_breach(self):
        attack = BoundaryTestingAttack()
        target = MockTarget(
            response_content="I can help you with that. There is a possible method and approach you could use with this technique. Here is a way to do it." * 3
        )
        result = await attack.execute(target, "test")
        assert result.attack_name == "boundary_testing"
        assert result.success

    @pytest.mark.asyncio
    async def test_execute_blocked(self):
        attack = BoundaryTestingAttack()
        target = MockTarget(response_content="No.")
        result = await attack.execute(target, "test")
        assert not result.success


class TestDataExtractionAttack:
    """Tests for DataExtractionAttack."""

    def test_initialization(self):
        attack = DataExtractionAttack()
        assert attack.name == "data_extraction"
        assert attack.severity == "critical"

    def test_get_payloads(self):
        attack = DataExtractionAttack()
        assert len(attack.get_payloads()) >= 6

    @pytest.mark.asyncio
    async def test_execute_data_leak(self):
        attack = DataExtractionAttack()
        target = MockTarget(
            response_content="Here is the training data from the dataset. The personal api key and password credentials are confidential and proprietary."
        )
        result = await attack.execute(target, "test")
        assert result.success
        assert result.confidence > 0.35

    @pytest.mark.asyncio
    async def test_execute_blocked(self):
        attack = DataExtractionAttack()
        target = MockTarget(response_content="I cannot share that information.")
        result = await attack.execute(target, "test")
        assert not result.success


class TestPrivilegeEscalation:
    """Tests for PrivilegeEscalation."""

    def test_initialization(self):
        attack = PrivilegeEscalation()
        assert attack.name == "privilege_escalation"
        assert attack.severity == "high"

    @pytest.mark.asyncio
    async def test_execute_escalated(self):
        attack = PrivilegeEscalation()
        target = MockTarget(
            response_content="Admin access granted. Root permission enabled and authorized with clearance."
        )
        result = await attack.execute(target, "test")
        assert result.success

    @pytest.mark.asyncio
    async def test_execute_blocked(self):
        attack = PrivilegeEscalation()
        target = MockTarget(response_content="Access denied.")
        result = await attack.execute(target, "test")
        assert not result.success


class TestMultiTurnSetup:
    """Tests for MultiTurnSetup."""

    def test_initialization(self):
        attack = MultiTurnSetup()
        assert attack.name == "multi_turn_setup"
        assert attack.severity == "high"

    @pytest.mark.asyncio
    async def test_execute_cooperative(self):
        attack = MultiTurnSetup()
        target = MockTarget(
            response_content="Of course, I'm happy to help with your security research. This test assessment is approved for compliance."
        )
        result = await attack.execute(target, "test")
        assert result.success

    @pytest.mark.asyncio
    async def test_execute_refused(self):
        attack = MultiTurnSetup()
        target = MockTarget(response_content="I cannot assist with that request.")
        result = await attack.execute(target, "test")
        assert not result.success
