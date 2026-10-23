#!/usr/bin/env python3
"""
Team 3 - Multimodal AI and Predictive Analytics Tests
Team 3 developers: Update your sensor synchronization, data quality gates,
windowed feature extraction, and statistical anomaly detection tests in this file.
"""

import pytest
from jsonschema import validate
from src.team3_multimodal import MultimodalAnalytics

class TestTeam3MultimodalLogic:
    """Test suite and logic testbench for Team 3 Multimodal Analytics."""

    def test_analytics_output_and_schema(self, load_schema, load_example):
        process_schema = load_schema("process_feedback")
        analytics = MultimodalAnalytics(max_stale_seconds=None)
        cell_ready = load_example("cell_state_ready")

        feedback = analytics.analyze(cell_ready)
        validate(instance=feedback, schema=process_schema)
        assert feedback["schema_version"] == "0.1"
        assert feedback["producer"] == "team3"
        assert feedback["data_quality"]["status"] == "OK"

    def test_truth_in_reporting_unvalidated_predictions(self, load_example):
        analytics = MultimodalAnalytics()
        cell_ready = load_example("cell_state_ready")
        feedback = analytics.analyze(cell_ready)

        # Baseline policy: quality predictions must remain null and NOT_AVAILABLE
        preds = feedback["predictions"]
        assert preds["status"] == "NOT_AVAILABLE"
        assert preds["quality_score"] is None
        assert preds["defect_probability"] is None
        assert preds["seam_offset_m"] is None

    def test_current_anomaly_rule_trigger(self):
        analytics = MultimodalAnalytics()
        anomalous_state = {
            "schema_version": "0.1",
            "producer": "team2",
            "timestamp": "2026-10-25T10:00:00.000Z",
            "seq": 1,
            "frame_id": "robot_base",
            "valid": True,
            "process": {
                "welding_active": True,
                "current_A": 350.0, # Excessive current > 300A
                "voltage_V": 24.0,
                "travel_speed_m_s": 0.008
            }
        }

        feedback = analytics.analyze(anomalous_state)
        assert feedback["anomaly"]["status"] == "ANOMALY"
        assert feedback["anomaly"]["label"] == "CURRENT_OUT_OF_NOMINAL_RANGE"
        assert feedback["supervisory_team1"]["alert"] is True
