#!/usr/bin/env python3
"""
Team 2 - Cell Orchestration and Simulated Execution
Tracks robot, fixture, clamps, process, safety states, and command acknowledgement lifecycle.
Follows VENTEK Consolidated Architecture Baseline v0.1.
"""

import datetime
from typing import Dict, Any, List, Optional

class CellOrchestrator:
    """
    Simulated Workcell Orchestrator.
    Manages robot, tooling, clamp actuators, PLC interlocks, and command lifecycles.
    """

    def __init__(self):
        self.seq = 0
        self.robot_state = "idle"
        self.joint_names = ["joint_a1", "joint_a2", "joint_a3", "joint_a4", "joint_a5", "joint_a6"]
        self.joint_positions_rad = [0.0, -0.5, 0.8, 0.0, 0.6, 0.0]
        self.tcp_position_m = [0.442, -0.0525, 0.835]
        self.tcp_orientation_xyzw = [0.0, 0.7071, 0.0, 0.7071]
        self.fixture_state = "locked"
        self.fixture_angle_rad = 0.0
        self.clamps_state = "locked"
        self.welding_active = False
        self.current_A: Optional[float] = None
        self.voltage_V: Optional[float] = None
        self.travel_speed_m_s: Optional[float] = None
        self.plc_ok = True
        self.estop_active = False
        self.faults: List[str] = []
        self.last_command = {
            "decision_id": "none",
            "status": "completed",
            "message": "system initialized"
        }

    def get_timestamp_utc(self) -> str:
        return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")

    def trigger_estop(self, reason: str = "EMERGENCY_STOP_BUTTON_PRESSED"):
        self.estop_active = True
        self.plc_ok = False
        self.robot_state = "fault"
        self.welding_active = False
        if reason not in self.faults:
            self.faults.append(reason)
        if self.last_command["status"] in ["accepted", "in_progress"]:
            self.last_command["status"] = "failed"
            self.last_command["message"] = f"Execution interrupted by E-stop: {reason}"

    def clear_faults(self):
        self.estop_active = False
        self.plc_ok = True
        self.faults.clear()
        self.robot_state = "idle"

    def execute_command(self, decision: Dict[str, Any], trajectory: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executes a command from Team 1 with explicit acknowledgement lifecycle.
        """
        cmd_id = decision.get("decision_id", "unknown")
        action = decision.get("action", "")

        # Check safety before execution
        if self.estop_active or not self.plc_ok:
            self.last_command = {
                "decision_id": cmd_id,
                "status": "failed",
                "message": f"Cannot execute command {cmd_id}: Safety fault active ({','.join(self.faults)})"
            }
            return self.get_state_payload()

        if action == "execute_weld":
            if not trajectory:
                self.last_command = {
                    "decision_id": cmd_id,
                    "status": "failed",
                    "message": "execute_weld received without trajectory"
                }
                return self.get_state_payload()

            # Execute simulation trajectory
            self.robot_state = "welding"
            self.welding_active = True
            self.current_A = 220.0
            self.voltage_V = 24.0
            self.travel_speed_m_s = 0.008

            # Move to final waypoint
            waypoints = trajectory.get("waypoints", [])
            if waypoints:
                last_wp = waypoints[-1]
                self.joint_positions_rad = list(last_wp.get("joint_positions_rad", self.joint_positions_rad))
                self.tcp_position_m = list(last_wp.get("tcp_position_m", self.tcp_position_m))
                self.tcp_orientation_xyzw = list(last_wp.get("tcp_orientation_xyzw", self.tcp_orientation_xyzw))

            self.robot_state = "idle"
            self.welding_active = False
            self.current_A = None
            self.voltage_V = None
            self.travel_speed_m_s = None

            self.last_command = {
                "decision_id": cmd_id,
                "status": "completed",
                "message": f"Weld trajectory {trajectory.get('trajectory_id')} successfully executed in simulation"
            }

        elif action == "pause_execution":
            self.robot_state = "paused"
            self.welding_active = False
            self.last_command = {
                "decision_id": cmd_id,
                "status": "completed",
                "message": "Motion paused safely"
            }

        else:
            self.last_command = {
                "decision_id": cmd_id,
                "status": "completed",
                "message": f"Action '{action}' processed"
            }

        return self.get_state_payload()

    def get_state_payload(self) -> Dict[str, Any]:
        self.seq += 1
        return {
            "schema_version": "0.1",
            "producer": "team2",
            "timestamp": self.get_timestamp_utc(),
            "seq": self.seq,
            "frame_id": "robot_base",
            "valid": True,
            "robot": {
                "robot_state": self.robot_state,
                "joint_names": self.joint_names,
                "joint_positions_rad": self.joint_positions_rad,
                "tcp_position_m": self.tcp_position_m,
                "tcp_orientation_xyzw": self.tcp_orientation_xyzw
            },
            "fixture": {
                "state": self.fixture_state,
                "angle_rad": self.fixture_angle_rad
            },
            "clamps": {
                "state": self.clamps_state
            },
            "process": {
                "welding_active": self.welding_active,
                "current_A": self.current_A,
                "voltage_V": self.voltage_V,
                "travel_speed_m_s": self.travel_speed_m_s
            },
            "safety": {
                "plc_ok": self.plc_ok,
                "estop_active": self.estop_active,
                "faults": list(self.faults)
            },
            "last_command": dict(self.last_command)
        }
