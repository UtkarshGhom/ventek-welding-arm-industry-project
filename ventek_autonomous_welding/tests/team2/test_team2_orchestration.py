#!/usr/bin/env python3
"""
Team 2 - Cell Orchestration and Simulation Execution Tests
Team 2 developers: Update your robot motion execution logic, clamp coordination,
PLC safety interfaces, and state publication tests in this file.
"""

import pytest
from jsonschema import validate
from src.team2_orchestration import CellOrchestrator

class TestTeam2OrchestrationLogic:
    """Test suite and logic testbench for Team 2 Cell Orchestration."""

    def test_initial_cell_state_and_schema(self, load_schema):
        cell_state_schema = load_schema("cell_state")
        orchestrator = CellOrchestrator()
        state = orchestrator.get_state_payload()

        validate(instance=state, schema=cell_state_schema)
        assert state["schema_version"] == "0.1"
        assert state["producer"] == "team2"
        assert state["robot"]["robot_state"] == "idle"
        assert state["fixture"]["state"] == "locked"
        assert state["clamps"]["state"] == "locked"
        assert state["safety"]["plc_ok"] is True
        assert state["safety"]["estop_active"] is False

    def test_execute_weld_command_lifecycle(self, load_example):
        orchestrator = CellOrchestrator()
        trajectory = load_example("trajectory_ok")
        decision = {
            "decision_id": "cmd_0100",
            "action": "execute_weld"
        }

        result_state = orchestrator.execute_command(decision, trajectory)
        assert result_state["last_command"]["decision_id"] == "cmd_0100"
        assert result_state["last_command"]["status"] == "completed"
        assert result_state["robot"]["robot_state"] == "idle"

    def test_emergency_stop_tripping_and_refusal(self):
        orchestrator = CellOrchestrator()
        orchestrator.trigger_estop("HARDWARE_PANIC_BUTTON_PRESSED")

        state = orchestrator.get_state_payload()
        assert state["safety"]["estop_active"] is True
        assert state["safety"]["plc_ok"] is False
        assert state["robot"]["robot_state"] == "fault"
        assert "HARDWARE_PANIC_BUTTON_PRESSED" in state["safety"]["faults"]

        # Attempt command execution while E-stopped
        blocked_state = orchestrator.execute_command({"decision_id": "cmd_0101", "action": "execute_weld"})
        assert blocked_state["last_command"]["status"] == "failed"
        assert "Safety fault active" in blocked_state["last_command"]["message"]

    def test_clear_faults_recovery(self):
        orchestrator = CellOrchestrator()
        orchestrator.trigger_estop()
        orchestrator.clear_faults()

        state = orchestrator.get_state_payload()
        assert state["safety"]["estop_active"] is False
        assert state["safety"]["plc_ok"] is True
        assert state["robot"]["robot_state"] == "idle"
