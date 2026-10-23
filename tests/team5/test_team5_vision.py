#!/usr/bin/env python3
"""
Team 5 - Computer Vision and Weld Intelligence Tests
Team 5 developers: Update your point cloud processing, camera calibration checks,
CAD registration, and candidate seam extraction tests in this file.
"""

import pytest
from jsonschema import validate
from src.team5_vision import VisionPerception

class TestTeam5VisionLogic:
    """Test suite and logic testbench for Team 5 Vision Pipeline."""

    def test_nominal_scene_generation_and_schema(self, load_schema):
        scene_schema = load_schema("scene")
        perception = VisionPerception(calibration_status="VERIFIED")

        scene = perception.scan_scene()
        validate(instance=scene, schema=scene_schema)
        assert scene["schema_version"] == "0.1"
        assert scene["producer"] == "team5"
        assert scene["calibration_status"] == "VERIFIED"
        assert len(scene["parts"]) > 0
        assert len(scene["candidate_joints"]) > 0

    def test_candidate_joint_properties(self):
        perception = VisionPerception()
        scene = perception.scan_scene()
        candidate = scene["candidate_joints"][0]

        assert candidate["joint_id"] == "candidate_001"
        assert candidate["length_m"] > 0.0
        assert len(candidate["start_point_m"]) == 3
        assert len(candidate["end_point_m"]) == 3
        # Invariant: geometric feature is NOT weld intent
        assert candidate["weld_intent_confirmed"] is False
        assert candidate["status"] == "CANDIDATE_REQUIRES_CONFIRMATION"

    def test_uncalibrated_sensor_state(self):
        perception = VisionPerception(calibration_status="UNVERIFIED")
        scene = perception.scan_scene()
        assert scene["calibration_status"] == "UNVERIFIED"

    def test_empty_candidate_joints_detection(self):
        perception = VisionPerception()
        scene = perception.scan_scene(inject_no_seam=True)
        assert len(scene["candidate_joints"]) == 0
        assert len(scene["warnings"]) > 0
