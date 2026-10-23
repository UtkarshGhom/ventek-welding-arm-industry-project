#!/usr/bin/env python3
"""
Team 1 - Cognitive Autonomy and Supervisory Decisions
Deterministic state machine and rule-based weld sequencing.
Follows VENTEK Consolidated Architecture Baseline v0.1.
"""

from enum import Enum
import datetime
import uuid
from typing import Dict, Any, Optional, Tuple

class SupervisoryState(str, Enum):
    SCANNING = "SCANNING"
    PLANNING = "PLANNING"
    VALIDATING = "VALIDATING"
    READY = "READY"
    EXECUTING = "EXECUTING"
    PAUSED = "PAUSED"
    REPLANNING = "REPLANNING"
    FAULT = "FAULT"
    COMPLETE = "COMPLETE"

class SupervisorStateMachine:
    """
    Deterministic supervisor for VENTEK cell.
    Coordinates workflow across Teams 2-6, evaluates deterministic guards,
    enforces safety, produces unique decision IDs, and logs transitions.
    """

    def __init__(self, initial_state: SupervisoryState = SupervisoryState.SCANNING):
        self.state = initial_state
        self.seq = 0
        self.command_counter = 0
        self.active_decision_id: Optional[str] = None
        self.active_trajectory_id: Optional[str] = None
        self.active_joint_id: Optional[str] = None
        self.transition_log = []

    def get_timestamp_utc(self) -> str:
        return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")

    def next_decision_id(self) -> str:
        self.command_counter += 1
        return f"cmd_{self.command_counter:04d}"

    def build_decision(
        self,
        action: str,
        next_state: SupervisoryState,
        reason_code: str,
        reason_text: str,
        inputs_used: Dict[str, Any],
        target_joint: Optional[str] = None,
        target_traj: Optional[str] = None,
        fixture_angle: Optional[float] = None,
        requires_human: bool = False,
        timeout_s: float = 60.0
    ) -> Dict[str, Any]:
        self.seq += 1
        decision_id = self.next_decision_id()
        self.active_decision_id = decision_id

        decision_payload = {
            "schema_version": "0.1",
            "producer": "team1",
            "timestamp": self.get_timestamp_utc(),
            "seq": self.seq,
            "frame_id": "robot_base",
            "valid": True,
            "decision_id": decision_id,
            "state": self.state.value,
            "next_state": next_state.value,
            "action": action,
            "target": {
                "joint_id": target_joint,
                "trajectory_ref": target_traj,
                "fixture_angle_rad": fixture_angle
            },
            "reason_code": reason_code,
            "reason_text": reason_text,
            "inputs_used": inputs_used,
            "requires_human": requires_human,
            "timeout_s": timeout_s
        }

        self.transition_log.append({
            "from_state": self.state.value,
            "to_state": next_state.value,
            "decision_id": decision_id,
            "reason_code": reason_code,
            "timestamp": decision_payload["timestamp"]
        })
        self.state = next_state
        return decision_payload

    def evaluate_scene(self, scene: Dict[str, Any]) -> Tuple[bool, str, str]:
        """
        Guard: Team 5 scene validation.
        Requires valid schema, verified calibration, and candidate joints.
        """
        if not scene.get("valid", False):
            return False, "SCENE_DATA_INVALID", "Scene payload marked invalid by producer"
        
        if scene.get("calibration_status") != "VERIFIED":
            return False, "CALIBRATION_UNVERIFIED", f"Camera calibration is {scene.get('calibration_status')}; cannot plan on unverified frame"

        candidate_joints = scene.get("candidate_joints", [])
        if not candidate_joints:
            return False, "NO_CANDIDATE_JOINTS", "Vision pipeline returned zero candidate weld joints"

        # Check candidate confidence
        best_candidate = candidate_joints[0]
        if best_candidate.get("confidence", 0.0) < 0.60:
            return False, "LOW_GEOMETRY_CONFIDENCE", f"Best candidate confidence {best_candidate.get('confidence')} is below 0.60 threshold"

        return True, "SCENE_VALIDATED", "Valid candidate seam found with verified calibration"

    def evaluate_trajectory(self, trajectory: Dict[str, Any]) -> Tuple[bool, str, str]:
        """
        Guard: Team 6 trajectory validation.
        Requires VALIDATED_CANDIDATE status, IK PASS, and Collision PASS.
        """
        if trajectory.get("status") != "VALIDATED_CANDIDATE":
            reason = trajectory.get("failure_reason") or "Trajectory not validated"
            return False, "TRAJECTORY_REJECTED", reason

        val = trajectory.get("validation", {})
        if val.get("ik") != "PASS":
            return False, "IK_VALIDATION_FAILED", "Inverse kinematics check failed for waypoints"

        if val.get("collision") != "PASS":
            return False, "COLLISION_CHECK_FAILED", "Collision check failed against cell obstacles or clamps"

        if trajectory.get("next_action") != "READY_FOR_SIMULATION":
            return False, "NOT_READY_FOR_SIM", f"Trajectory next_action is {trajectory.get('next_action')}"

        return True, "TRAJECTORY_VALIDATED", "Feasible, collision-free trajectory ready for execution"

    def evaluate_cell_readiness(self, cell_state: Dict[str, Any]) -> Tuple[bool, str, str]:
        """
        Guard: Team 2 cell state check before authorizing execution.
        Requires robot idle, fixtures & clamps locked, safety OK.
        """
        if not cell_state.get("valid", False):
            return False, "CELL_STATE_INVALID", "Cell state marked invalid"

        safety = cell_state.get("safety", {})
        if safety.get("estop_active", True) or not safety.get("plc_ok", False):
            faults = ", ".join(safety.get("faults", []))
            return False, "SAFETY_INTERLOCK_FAULT", f"Safety fault active: {faults}"

        clamps = cell_state.get("clamps", {})
        if clamps.get("state") != "locked":
            return False, "CLAMPS_NOT_LOCKED", f"Clamps state is {clamps.get('state')}; must be locked"

        fixture = cell_state.get("fixture", {})
        if fixture.get("state") != "locked":
            return False, "FIXTURE_NOT_LOCKED", f"Fixture state is {fixture.get('state')}; must be locked"

        robot = cell_state.get("robot", {})
        if robot.get("robot_state") not in ["idle", "ready"]:
            return False, "ROBOT_NOT_IDLE", f"Robot state is {robot.get('robot_state')}; expected idle"

        return True, "CELL_READY", "Cell state, interlocks, clamps and fixtures verified ready"

    def evaluate_acknowledgement(self, cell_state: Dict[str, Any], expected_id: str) -> Tuple[bool, str, str]:
        """
        Guard: Confirms Team 2 command lifecycle completion.
        Separates command accepted from command completed.
        """
        last_cmd = cell_state.get("last_command", {})
        cmd_id = last_cmd.get("decision_id")
        status = last_cmd.get("status")

        if cmd_id != expected_id:
            return False, "COMMAND_ID_MISMATCH", f"Expected acknowledgement for {expected_id}, but received {cmd_id}"

        if status == "failed":
            return False, "COMMAND_EXECUTION_FAILED", last_cmd.get("message", "Command execution failed in cell")

        if status != "completed":
            return False, "COMMAND_IN_PROGRESS", f"Command {cmd_id} is still {status}"

        return True, "COMMAND_COMPLETED", f"Command {cmd_id} successfully acknowledged and completed"

    def evaluate_correction(self, correction: Dict[str, Any]) -> Tuple[bool, str, str]:
        """
        Guard: Team 4 adaptive correction proposal.
        """
        if not correction.get("valid", False):
            return False, "CORRECTION_INVALID", "Correction data marked invalid"

        action = correction.get("action_requested")
        if action == "REQUEST_REPLAN":
            return False, "REPLAN_REQUESTED", correction.get("reason", "Team 4 requested replan due to deviation")

        if action == "REQUEST_PAUSE":
            return False, "PAUSE_REQUESTED", correction.get("reason", "Team 4 requested pause")

        if not correction.get("within_limits", False):
            return False, "OFFSET_EXCEEDS_LIMITS", "Correction offset exceeds allowable limits envelope"

        return True, "CORRECTION_BOUNDED", "Correction proposal is bounded and valid for revalidation"
