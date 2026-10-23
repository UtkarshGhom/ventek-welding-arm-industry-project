#!/usr/bin/env python3
"""
Team 4 - Adaptive Control and Seam Tracking Tests
Team 4 developers: Update your deviation filtering, deadband models,
bounded correction proposals, and replan thresholds in this file.
"""

import pytest
from jsonschema import validate
from src.team4_adaptive import AdaptiveController

class TestTeam4AdaptiveLogic:
    """Test suite and logic testbench for Team 4 Adaptive Control."""

    def test_bounded_correction_and_schema(self, load_schema):
        correction_schema = load_schema("correction")
        adapter = AdaptiveController(deadband_m=0.00005, max_correction_m=0.0010)

        # 0.4 mm deviation (within 1.0 mm limit)
        correction = adapter.process_deviation(
            trajectory_id="traj_001",
            trajectory_revision=1,
            joint_id="candidate_001",
            planned_position_m=[0.450, 0.020, 0.220],
            observed_position_m=[0.450, 0.0204, 0.220]
        )

        validate(instance=correction, schema=correction_schema)
        assert correction["schema_version"] == "0.1"
        assert correction["producer"] == "team4"
        assert correction["within_limits"] is True
        assert correction["action_requested"] == "CORRECT_WITH_REVALIDATION"
        assert correction["trajectory_revision"] == 1

    def test_deadband_filtering(self):
        adapter = AdaptiveController(deadband_m=0.00005) # 50 microns

        # 20 micron jitter (below deadband)
        correction = adapter.process_deviation(
            trajectory_id="traj_001",
            trajectory_revision=1,
            joint_id="candidate_001",
            planned_position_m=[0.450, 0.020, 0.220],
            observed_position_m=[0.450, 0.02002, 0.220]
        )
        assert correction["filtered_offset_m"] == [0.0, 0.0, 0.0]

    def test_excessive_deviation_triggers_replan(self):
        adapter = AdaptiveController(max_correction_m=0.0010) # 1.0 mm limit

        # 2.5 mm deviation (exceeds limit)
        correction = adapter.process_deviation(
            trajectory_id="traj_001",
            trajectory_revision=1,
            joint_id="candidate_001",
            planned_position_m=[0.450, 0.020, 0.220],
            observed_position_m=[0.450, 0.0225, 0.220]
        )
        assert correction["within_limits"] is False
        assert correction["action_requested"] == "REQUEST_REPLAN"
        assert "exceeds maximum allowable limit" in correction["reason"]
