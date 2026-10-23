#!/usr/bin/env python3
"""
Team 1 - Cognitive Autonomy and Supervisory Logic Tests
Team 1 developers: Update your sequencing logic, deterministic state guards,
and decision transition tests in this file.
"""

import pytest
from jsonschema import validate
from src.team1_autonomy import SupervisorStateMachine, SupervisoryState

class TestTeam1AutonomyLogic:
    """Test suite and logic testbench for Team 1 Supervisor."""

    def test_state_machine_initial_state(self):
        supervisor = SupervisorStateMachine()
        assert supervisor.state == SupervisoryState.SCANNING
        assert supervisor.seq == 0
        assert supervisor.command_counter == 0

    def test_decision_generation_and_schema(self, load_schema):
        decision_schema = load_schema("decision")
        supervisor = SupervisorStateMachine()

        decision = supervisor.build_decision(
            action="request_scan",
            next_state=SupervisoryState.SCANNING,
            reason_code="START_SCAN",
            reason_text="Initiating perception scan",
            inputs_used={}
        )

        validate(instance=decision, schema=decision_schema)
        assert decision["schema_version"] == "0.1"
        assert decision["producer"] == "team1"
        assert decision["decision_id"] == "cmd_0001"
        assert decision["action"] == "request_scan"

    def test_scene_guard_logic(self, load_example):
        supervisor = SupervisorStateMachine()
        scene_ok = load_example("scene_ok")
        ok, code, msg = supervisor.evaluate_scene(scene_ok)
        assert ok is True
        assert code == "SCENE_VALIDATED"

        # Test unverified calibration rejection
        scene_unverified = dict(scene_ok)
        scene_unverified["calibration_status"] = "UNVERIFIED"
        ok_unv, code_unv, _ = supervisor.evaluate_scene(scene_unverified)
        assert ok_unv is False
        assert code_unv == "CALIBRATION_UNVERIFIED"

    def test_cell_readiness_guard(self, load_example):
        supervisor = SupervisorStateMachine()
        cell_ready = load_example("cell_state_ready")
        ok, code, msg = supervisor.evaluate_cell_readiness(cell_ready)
        assert ok is True
        assert code == "CELL_READY"

        # Test clamp not locked
        cell_unlocked = dict(cell_ready)
        cell_unlocked["clamps"] = {"state": "unlocked"}
        ok_clamp, code_clamp, _ = supervisor.evaluate_cell_readiness(cell_unlocked)
        assert ok_clamp is False
        assert code_clamp == "CLAMPS_NOT_LOCKED"

    def test_acknowledgement_lifecycle_check(self, load_example):
        supervisor = SupervisorStateMachine()
        cell_state = load_example("cell_state_ready")
        # Match decision id
        cell_state["last_command"]["decision_id"] = "cmd_0042"
        cell_state["last_command"]["status"] = "completed"

        ok, code, msg = supervisor.evaluate_acknowledgement(cell_state, expected_id="cmd_0042")
        assert ok is True
        assert code == "COMMAND_COMPLETED"

        # Mismatch must fail
        ok_mis, code_mis, _ = supervisor.evaluate_acknowledgement(cell_state, expected_id="cmd_9999")
        assert ok_mis is False
        assert code_mis == "COMMAND_ID_MISMATCH"
