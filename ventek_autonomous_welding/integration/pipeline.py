#!/usr/bin/env python3
"""
VENTEK End-to-End Vertical Slice Pipeline
Integrates Teams 1 through 6 into a reproducible baseline simulation pipeline.
Follows VENTEK Consolidated Architecture Baseline v0.1.
"""

from typing import Dict, Any, Optional, Tuple, List
from src.team1_autonomy import SupervisorStateMachine, SupervisoryState
from src.team2_orchestration import CellOrchestrator
from src.team3_multimodal import MultimodalAnalytics
from src.team4_adaptive import AdaptiveController
from src.team5_vision import VisionPerception
from src.team6_planning import TrajectoryPlanner

class VentekIntegrationPipeline:
    """
    Executes the consolidated end-to-end slice:
    Team 1 (Supervisor) -> Team 5 (Perception) -> Team 6 (Planning)
    -> Team 2 (Orchestration) -> Team 3 (Analytics) -> Team 4 (Adaptation)
    -> Supervisory closure and logs.
    """

    def __init__(self, perception_calibration: str = "VERIFIED"):
        self.supervisor = SupervisorStateMachine()
        self.cell = CellOrchestrator()
        self.analytics = MultimodalAnalytics()
        self.adaptation = AdaptiveController()
        self.perception = VisionPerception(calibration_status=perception_calibration)
        self.planner = TrajectoryPlanner()

    def run_happy_path(self) -> Dict[str, Any]:
        """
        Executes Scenario 1: Nominal Happy Path
        1. Supervisor starts job -> SCANNING.
        2. Perception produces scene with candidate seam.
        3. Supervisor validates scene -> PLANNING.
        4. Planner produces validated trajectory.
        5. Supervisor validates trajectory and cell readiness -> READY -> EXECUTING.
        6. Cell executes simulated trajectory -> completed acknowledgement.
        7. Analytics provides advisory feedback.
        8. Adaptation evaluates nominal feedback.
        9. Supervisor confirms completion -> COMPLETE.
        """
        results = {"events": [], "success": False}

        # 1. Supervisor requests scan
        scan_decision = self.supervisor.build_decision(
            action="request_scan",
            next_state=SupervisoryState.SCANNING,
            reason_code="START_JOB_CYCLE",
            reason_text="Initiating perception scan for workpiece setup",
            inputs_used={}
        )
        results["events"].append({"step": "1_scan_requested", "decision": scan_decision})

        # 2. Team 5 scans scene
        scene = self.perception.scan_scene()
        results["events"].append({"step": "2_scene_published", "scene": scene})

        # 3. Supervisor evaluates scene
        scene_ok, code, msg = self.supervisor.evaluate_scene(scene)
        if not scene_ok:
            results["error"] = f"Scene check failed: {code} - {msg}"
            return results

        candidate = scene["candidate_joints"][0]
        plan_decision = self.supervisor.build_decision(
            action="request_plan",
            next_state=SupervisoryState.PLANNING,
            reason_code=code,
            reason_text=msg,
            inputs_used={"scene_seq": scene["seq"]},
            target_joint=candidate["joint_id"]
        )
        results["events"].append({"step": "3_plan_requested", "decision": plan_decision})

        # 4. Team 6 plans trajectory
        trajectory = self.planner.plan_seam(candidate)
        results["events"].append({"step": "4_trajectory_published", "trajectory": trajectory})

        # 5. Supervisor evaluates trajectory
        traj_ok, t_code, t_msg = self.supervisor.evaluate_trajectory(trajectory)
        if not traj_ok:
            results["error"] = f"Trajectory check failed: {t_code} - {t_msg}"
            return results

        # 6. Check cell readiness
        cell_state = self.cell.get_state_payload()
        ready_ok, r_code, r_msg = self.supervisor.evaluate_cell_readiness(cell_state)
        if not ready_ok:
            results["error"] = f"Cell not ready: {r_code} - {r_msg}"
            return results

        # Authorize execution
        exec_decision = self.supervisor.build_decision(
            action="execute_weld",
            next_state=SupervisoryState.EXECUTING,
            reason_code="TRAJECTORY_VALIDATED_CELL_READY",
            reason_text="Required planning checks passed and cell is ready",
            inputs_used={
                "scene_seq": scene["seq"],
                "trajectory_seq": 1,
                "cell_state_seq": cell_state["seq"]
            },
            target_joint=candidate["joint_id"],
            target_traj=trajectory["trajectory_id"]
        )
        results["events"].append({"step": "5_execution_authorized", "decision": exec_decision})

        # 7. Team 2 executes weld in simulation
        executed_state = self.cell.execute_command(exec_decision, trajectory)
        results["events"].append({"step": "6_cell_executed", "cell_state": executed_state})

        # 8. Team 3 Multimodal analytics
        feedback = self.analytics.analyze(executed_state)
        results["events"].append({"step": "7_analytics_feedback", "feedback": feedback})

        # 9. Team 4 Adaptation check (simulated nominal deviation of 0.1mm)
        nominal_wp = trajectory["waypoints"][1]["tcp_position_m"]
        observed_wp = [nominal_wp[0], nominal_wp[1] + 0.0001, nominal_wp[2]]
        correction = self.adaptation.process_deviation(
            trajectory_id=trajectory["trajectory_id"],
            trajectory_revision=1,
            joint_id=candidate["joint_id"],
            planned_position_m=nominal_wp,
            observed_position_m=observed_wp
        )
        results["events"].append({"step": "8_adaptation_evaluated", "correction": correction})

        # 10. Supervisor verifies acknowledgement
        ack_ok, a_code, a_msg = self.supervisor.evaluate_acknowledgement(
            executed_state,
            expected_id=exec_decision["decision_id"]
        )
        if not ack_ok:
            results["error"] = f"Acknowledgement check failed: {a_code} - {a_msg}"
            return results

        # Complete job
        complete_decision = self.supervisor.build_decision(
            action="complete_job",
            next_state=SupervisoryState.COMPLETE,
            reason_code="WELD_COMPLETED_SUCCESSFULLY",
            reason_text=f"Weld command {exec_decision['decision_id']} confirmed executed by Team 2",
            inputs_used={
                "cell_state_seq": executed_state["seq"],
                "correction_seq": correction["seq"]
            }
        )
        results["events"].append({"step": "9_job_completed", "decision": complete_decision})
        results["success"] = True
        return results
