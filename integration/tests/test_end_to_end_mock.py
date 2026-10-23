#!/usr/bin/env python3
"""
Integration End-to-End Mock Scenarios Test Suite
Tests all 10 minimum integration scenarios specified in Section 9 of
VENTEK_Consolidated_Architecture_Baseline_and_JSON_Contracts.md:

1. Valid scene -> reachable seam -> collision-free trajectory -> command completed -> Team 1 COMPLETE.
2. No candidate seam -> rescan/human review; no execution.
3. Unverified calibration or low confidence -> block planning or require review.
4. Unreachable seam -> explicit IK failure; no executable trajectory.
5. Clamp collision -> collision failure or validated alternative.
6. Stale Team 3/4 input -> reject/ignore according to policy; never treat as normal.
7. Large deviation -> Team 4 requests replan/pause; Team 6 revalidates.
8. Command acknowledgement timeout -> pause/escalate/fault.
9. E-stop/PLC/robot fault -> independent safety response; AI cannot override.
10. Schema mismatch -> reject, log and stop progression.
"""

import os
import json
import pytest
from jsonschema import validate, ValidationError

from src.team1_autonomy import SupervisorStateMachine, SupervisoryState
from src.team2_orchestration import CellOrchestrator
from src.team3_multimodal import MultimodalAnalytics
from src.team4_adaptive import AdaptiveController
from src.team5_vision import VisionPerception
from src.team6_planning import TrajectoryPlanner
from integration.pipeline import VentekIntegrationPipeline

PKG_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCHEMAS_DIR = os.path.join(PKG_ROOT, "integration", "schemas")

def load_schema(name):
    with open(os.path.join(SCHEMAS_DIR, f"{name}.schema.json"), "r") as f:
        return json.load(f)

class TestMinimumIntegrationScenarios:
    """Implements and validates the 10 baseline integration scenarios."""

    def test_scenario_01_nominal_happy_path(self):
        """Scenario 1: Valid scene -> reachable seam -> collision-free trajectory -> command completed -> Team 1 COMPLETE."""
        pipeline = VentekIntegrationPipeline()
        res = pipeline.run_happy_path()
        assert res["success"] is True, res.get("error")
        assert pipeline.supervisor.state == SupervisoryState.COMPLETE
        assert len(pipeline.supervisor.transition_log) >= 3

        # Validate that all produced decision payloads match schema
        decision_schema = load_schema("decision")
        for evt in res["events"]:
            if "decision" in evt:
                validate(instance=evt["decision"], schema=decision_schema)

    def test_scenario_02_no_candidate_seam(self):
        """Scenario 2: No candidate seam -> rescan/human review; no execution."""
        supervisor = SupervisorStateMachine()
        perception = VisionPerception()
        scene = perception.scan_scene(inject_no_seam=True)
        assert len(scene["candidate_joints"]) == 0

        ok, code, msg = supervisor.evaluate_scene(scene)
        assert ok is False
        assert code == "NO_CANDIDATE_JOINTS"
        # State machine should NOT progress to PLANNING or EXECUTING
        assert supervisor.state == SupervisoryState.SCANNING

    def test_scenario_03_unverified_calibration(self):
        """Scenario 3: Unverified calibration or low confidence -> block planning or require review."""
        supervisor = SupervisorStateMachine()
        perception = VisionPerception(calibration_status="UNVERIFIED")
        scene = perception.scan_scene()
        assert scene["calibration_status"] == "UNVERIFIED"

        ok, code, msg = supervisor.evaluate_scene(scene)
        assert ok is False
        assert code == "CALIBRATION_UNVERIFIED"
        assert supervisor.state == SupervisoryState.SCANNING

    def test_scenario_04_unreachable_seam(self):
        """Scenario 4: Unreachable seam -> explicit IK failure; no executable trajectory."""
        planner = TrajectoryPlanner()
        # Seam located at 1.25m, outside KR 6 R900 reach (0.901m)
        far_candidate = {
            "joint_id": "candidate_far_001",
            "start_point_m": [1.25, 0.0, 0.85],
            "end_point_m": [1.45, 0.0, 0.85]
        }
        trajectory = planner.plan_seam(far_candidate)
        assert trajectory["status"] == "FAILED_VALIDATION"
        assert trajectory["validation"]["ik"] == "FAIL"
        assert trajectory["next_action"] == "REJECTED"
        assert len(trajectory["waypoints"]) == 0

        # Supervisor must reject trajectory
        supervisor = SupervisorStateMachine()
        ok, code, msg = supervisor.evaluate_trajectory(trajectory)
        assert ok is False
        assert code == "TRAJECTORY_REJECTED"

    def test_scenario_05_clamp_collision(self):
        """Scenario 5: Clamp collision -> collision failure or validated alternative."""
        planner = TrajectoryPlanner()
        candidate = {
            "joint_id": "candidate_nominal",
            "start_point_m": [0.442, -0.0525, 0.785],
            "end_point_m": [0.658, -0.0525, 0.785]
        }
        # Injected obstructing clamp right on the seam path
        obstructing_clamp = [[0.550, -0.055, 0.785]]
        trajectory = planner.plan_seam(candidate, clamp_positions=obstructing_clamp)
        assert trajectory["status"] == "FAILED_VALIDATION"
        assert trajectory["validation"]["collision"] == "FAIL"
        assert trajectory["next_action"] == "REJECTED"

        supervisor = SupervisorStateMachine()
        ok, code, msg = supervisor.evaluate_trajectory(trajectory)
        assert ok is False
        assert code == "TRAJECTORY_REJECTED"

    def test_scenario_06_stale_telemetry_input(self):
        """Scenario 6: Stale Team 3/4 input -> reject/ignore according to policy; never treat as normal."""
        analytics = MultimodalAnalytics(max_stale_seconds=5.0)
        # Create cell state with a timestamp from 1 hour ago
        stale_state = {
            "schema_version": "0.1",
            "producer": "team2",
            "timestamp": "2026-10-25T08:00:00.000Z",
            "seq": 1,
            "frame_id": "robot_base",
            "valid": True,
            "process": {"current_A": 220.0, "voltage_V": 24.0, "travel_speed_m_s": 0.008}
        }
        feedback = analytics.analyze(stale_state)
        assert feedback["data_quality"]["status"] == "STALE"
        assert "cell_state_telemetry" in feedback["data_quality"]["stale_channels"]
        assert feedback["supervisory_team1"]["alert"] is True
        assert feedback["supervisory_team1"]["reason_code"] == "DATA_STALE"

    def test_scenario_07_large_deviation_replan_request(self):
        """Scenario 7: Large deviation -> Team 4 requests replan/pause; Team 6 revalidates."""
        adapter = AdaptiveController(max_correction_m=0.0010) # 1.0mm limit
        planned_wp = [0.442, -0.0525, 0.785]
        # Observed point has 3.5mm deviation (exceeds 1.0mm)
        observed_wp = [0.442, -0.0490, 0.785]

        correction = adapter.process_deviation(
            trajectory_id="traj_001",
            trajectory_revision=1,
            joint_id="candidate_001",
            planned_position_m=planned_wp,
            observed_position_m=observed_wp
        )
        assert correction["within_limits"] is False
        assert correction["action_requested"] == "REQUEST_REPLAN"

        supervisor = SupervisorStateMachine(initial_state=SupervisoryState.EXECUTING)
        ok, code, msg = supervisor.evaluate_correction(correction)
        assert ok is False
        assert code == "REPLAN_REQUESTED"

        # Supervisor safely transitions to PAUSED or REPLANNING
        pause_decision = supervisor.build_decision(
            action="pause_execution",
            next_state=SupervisoryState.PAUSED,
            reason_code="EXCESSIVE_DEVIATION",
            reason_text=msg,
            inputs_used={"correction_seq": correction["seq"]},
            requires_human=True
        )
        assert supervisor.state == SupervisoryState.PAUSED
        assert pause_decision["requires_human"] is True

    def test_scenario_08_command_acknowledgement_mismatch_or_timeout(self):
        """Scenario 8: Command acknowledgement timeout or ID mismatch -> pause/escalate/fault."""
        supervisor = SupervisorStateMachine()
        cell_state = {
            "schema_version": "0.1",
            "producer": "team2",
            "timestamp": "2026-10-25T10:00:00.000Z",
            "seq": 10,
            "frame_id": "robot_base",
            "valid": True,
            "last_command": {
                "decision_id": "cmd_0001", # Expecting cmd_0002
                "status": "completed",
                "message": "old command"
            }
        }
        ok, code, msg = supervisor.evaluate_acknowledgement(cell_state, expected_id="cmd_0002")
        assert ok is False
        assert code == "COMMAND_ID_MISMATCH"

    def test_scenario_09_safety_fault_and_estop(self):
        """Scenario 9: E-stop/PLC/robot fault -> independent safety response; AI cannot override."""
        cell = CellOrchestrator()
        supervisor = SupervisorStateMachine()

        # Trigger emergency stop
        cell.trigger_estop("WORKCELL_LIGHT_CURTAIN_BREACH")
        fault_state = cell.get_state_payload()
        assert fault_state["safety"]["estop_active"] is True
        assert fault_state["safety"]["plc_ok"] is False

        # Supervisor must refuse to authorize execution
        ready_ok, r_code, r_msg = supervisor.evaluate_cell_readiness(fault_state)
        assert ready_ok is False
        assert r_code == "SAFETY_INTERLOCK_FAULT"

        # Cell must refuse command execution while E-stop is active
        fake_decision = {"decision_id": "cmd_9999", "action": "execute_weld"}
        res_state = cell.execute_command(fake_decision)
        assert res_state["last_command"]["status"] == "failed"
        assert "Safety fault active" in res_state["last_command"]["message"]

    def test_scenario_10_schema_mismatch_rejection(self):
        """Scenario 10: Schema mismatch -> reject, log and stop progression."""
        scene_schema = load_schema("scene")
        corrupted_scene = {
            "schema_version": "0.0.unknown",
            "producer": "unknown_team",
            "valid": False
        }
        with pytest.raises(ValidationError):
            validate(instance=corrupted_scene, schema=scene_schema)

        # Supervisor checks payload validity flag and stops progression
        supervisor = SupervisorStateMachine()
        ok, code, msg = supervisor.evaluate_scene(corrupted_scene)
        assert ok is False
        assert code == "SCENE_DATA_INVALID"
        assert supervisor.state == SupervisoryState.SCANNING
