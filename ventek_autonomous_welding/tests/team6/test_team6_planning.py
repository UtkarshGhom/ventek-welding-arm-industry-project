#!/usr/bin/env python3
"""
Team 6 - Path Planning, Kinematics and Motion Feasibility Tests
Team 6 developers: Update your MoveIt 2 configs, IK reachability,
torch orientation solvers, and clamp collision validation tests in this file.
"""

import pytest
from jsonschema import validate
from src.team6_planning import TrajectoryPlanner

class TestTeam6PlanningLogic:
    """Test suite and logic testbench for Team 6 Path Planning."""

    def test_nominal_planning_and_schema(self, load_schema, load_example):
        trajectory_schema = load_schema("trajectory")
        scene = load_example("scene_ok")
        candidate = scene["candidate_joints"][0]

        planner = TrajectoryPlanner()
        trajectory = planner.plan_seam(candidate)

        validate(instance=trajectory, schema=trajectory_schema)
        assert trajectory["schema_version"] == "0.1"
        assert trajectory["producer"] == "team6"
        assert trajectory["status"] == "VALIDATED_CANDIDATE"
        assert trajectory["validation"]["ik"] == "PASS"
        assert trajectory["validation"]["collision"] == "PASS"
        assert trajectory["validation"]["singularity"] == "NOT_AVAILABLE"
        assert trajectory["next_action"] == "READY_FOR_SIMULATION"
        assert len(trajectory["waypoints"]) >= 3

    def test_phases_sequence_approach_weld_retreat(self, load_example):
        scene = load_example("scene_ok")
        candidate = scene["candidate_joints"][0]
        planner = TrajectoryPlanner()
        trajectory = planner.plan_seam(candidate)

        phases = [wp["phase"] for wp in trajectory["waypoints"]]
        assert phases[0] == "APPROACH"
        assert "WELD" in phases[1:-1]
        assert phases[-1] == "RETREAT"

    def test_out_of_reach_seam_rejection(self):
        planner = TrajectoryPlanner(max_reach_m=0.901)
        out_of_reach_candidate = {
            "joint_id": "out_of_reach_joint",
            "start_point_m": [1.25, 0.0, 0.85],
            "end_point_m": [1.45, 0.0, 0.85]
        }
        trajectory = planner.plan_seam(out_of_reach_candidate)
        assert trajectory["status"] == "FAILED_VALIDATION"
        assert trajectory["validation"]["ik"] == "FAIL"
        assert trajectory["next_action"] == "REJECTED"
        assert "exceeds kinematic limit" in trajectory["failure_reason"]

    def test_clamp_collision_detection(self, load_example):
        scene = load_example("scene_ok")
        candidate = scene["candidate_joints"][0]
        planner = TrajectoryPlanner()

        # Obstructing clamp position right on the seam
        obstructing_clamp = [[0.550, -0.0525, 0.785]]
        trajectory = planner.plan_seam(candidate, clamp_positions=obstructing_clamp)
        assert trajectory["status"] == "FAILED_VALIDATION"
        assert trajectory["validation"]["collision"] == "FAIL"
        assert trajectory["next_action"] == "REJECTED"
        assert "Clamp interference detected" in trajectory["failure_reason"]

    def test_revalidate_team4_correction(self, load_example):
        scene = load_example("scene_ok")
        candidate = scene["candidate_joints"][0]
        planner = TrajectoryPlanner()

        # Small 0.3mm offset from Team 4
        corrected_trajectory = planner.plan_seam(candidate, offset_m=[0.0, 0.0003, 0.0])
        assert corrected_trajectory["status"] == "VALIDATED_CANDIDATE"
        assert corrected_trajectory["validation"]["ik"] == "PASS"
        assert corrected_trajectory["validation"]["collision"] == "PASS"
