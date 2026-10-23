#!/usr/bin/env python3
"""
Integration Schema Validation Test Suite
Validates all canonical JSON examples against their JSON Schema specifications (v0.1 canonical).
"""

import os
import json
import pytest
from jsonschema import validate, ValidationError, Draft7Validator

PKG_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCHEMAS_DIR = os.path.join(PKG_ROOT, "integration", "schemas")
EXAMPLES_DIR = os.path.join(PKG_ROOT, "integration", "examples")

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

@pytest.fixture(scope="module")
def schemas():
    schema_files = {
        "scene": "scene.schema.json",
        "trajectory": "trajectory.schema.json",
        "cell_state": "cell_state.schema.json",
        "process_feedback": "process_feedback.schema.json",
        "correction": "correction.schema.json",
        "decision": "decision.schema.json",
    }
    loaded = {}
    for key, filename in schema_files.items():
        schema_path = os.path.join(SCHEMAS_DIR, filename)
        assert os.path.exists(schema_path), f"Schema {filename} missing"
        schema_dict = load_json(schema_path)
        # Validate that the schema itself is a valid Draft 7 schema
        Draft7Validator.check_schema(schema_dict)
        loaded[key] = schema_dict
    return loaded

class TestSchemaValidation:
    """Test suite ensuring all canonical examples adhere strictly to schemas."""

    def test_scene_ok_validates(self, schemas):
        data = load_json(os.path.join(EXAMPLES_DIR, "scene_ok.json"))
        validate(instance=data, schema=schemas["scene"])
        assert data["schema_version"] == "0.1"
        assert data["producer"] == "team5"
        assert data["calibration_status"] == "VERIFIED"
        assert len(data["candidate_joints"]) > 0

    def test_scene_invalid_rejected(self, schemas):
        data = load_json(os.path.join(EXAMPLES_DIR, "scene_invalid.json"))
        with pytest.raises(ValidationError):
            validate(instance=data, schema=schemas["scene"])

    def test_trajectory_ok_validates(self, schemas):
        data = load_json(os.path.join(EXAMPLES_DIR, "trajectory_ok.json"))
        validate(instance=data, schema=schemas["trajectory"])
        assert data["status"] == "VALIDATED_CANDIDATE"
        assert data["validation"]["ik"] == "PASS"
        assert data["validation"]["collision"] == "PASS"
        assert data["next_action"] == "READY_FOR_SIMULATION"

    def test_trajectory_unreachable_validates(self, schemas):
        data = load_json(os.path.join(EXAMPLES_DIR, "trajectory_unreachable.json"))
        validate(instance=data, schema=schemas["trajectory"])
        assert data["status"] == "FAILED_VALIDATION"
        assert data["validation"]["ik"] == "FAIL"
        assert data["next_action"] == "REJECTED"
        assert data["failure_reason"] is not None

    def test_cell_state_ready_validates(self, schemas):
        data = load_json(os.path.join(EXAMPLES_DIR, "cell_state_ready.json"))
        validate(instance=data, schema=schemas["cell_state"])
        assert data["robot"]["robot_state"] == "idle"
        assert data["fixture"]["state"] == "locked"
        assert data["clamps"]["state"] == "locked"
        assert data["safety"]["plc_ok"] is True
        assert data["safety"]["estop_active"] is False

    def test_cell_state_fault_validates(self, schemas):
        data = load_json(os.path.join(EXAMPLES_DIR, "cell_state_fault.json"))
        validate(instance=data, schema=schemas["cell_state"])
        assert data["robot"]["robot_state"] == "fault"
        assert data["safety"]["estop_active"] is True
        assert len(data["safety"]["faults"]) > 0

    def test_process_feedback_unavailable_validates(self, schemas):
        data = load_json(os.path.join(EXAMPLES_DIR, "process_feedback_unavailable.json"))
        validate(instance=data, schema=schemas["process_feedback"])
        assert data["anomaly"]["status"] == "NOT_AVAILABLE"
        assert data["predictions"]["status"] == "NOT_AVAILABLE"
        assert data["predictions"]["quality_score"] is None

    def test_correction_small_validates(self, schemas):
        data = load_json(os.path.join(EXAMPLES_DIR, "correction_small.json"))
        validate(instance=data, schema=schemas["correction"])
        assert data["within_limits"] is True
        assert data["action_requested"] == "CORRECT_WITH_REVALIDATION"
        assert data["trajectory_revision"] == 1

    def test_correction_replan_validates(self, schemas):
        data = load_json(os.path.join(EXAMPLES_DIR, "correction_replan.json"))
        validate(instance=data, schema=schemas["correction"])
        assert data["within_limits"] is False
        assert data["action_requested"] == "REQUEST_REPLAN"

    def test_decision_execute_validates(self, schemas):
        data = load_json(os.path.join(EXAMPLES_DIR, "decision_execute.json"))
        validate(instance=data, schema=schemas["decision"])
        assert data["state"] == "READY"
        assert data["next_state"] == "EXECUTING"
        assert data["action"] == "execute_weld"
        assert data["decision_id"] == "cmd_0002"

    def test_decision_pause_validates(self, schemas):
        data = load_json(os.path.join(EXAMPLES_DIR, "decision_pause.json"))
        validate(instance=data, schema=schemas["decision"])
        assert data["state"] == "EXECUTING"
        assert data["next_state"] == "PAUSED"
        assert data["action"] == "pause_execution"
        assert data["requires_human"] is True

    def test_missing_required_fields_rejected(self, schemas):
        """Mutated payloads lacking required fields must fail validation."""
        for schema_name, schema in schemas.items():
            minimal_invalid = {"schema_version": "0.1"}
            with pytest.raises(ValidationError):
                validate(instance=minimal_invalid, schema=schema)
