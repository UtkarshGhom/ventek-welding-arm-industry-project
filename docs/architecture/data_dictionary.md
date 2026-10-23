# VENTEK Canonical Data Dictionary (v0.1)

## 1. Global Attributes (Required in all payloads)

| Field | Type | Description | Allowed Values |
|---|---|---|---|
| `schema_version` | string | Canonical schema revision | `"0.1"` |
| `producer` | string | Subsystem originating the payload | `"team1"`, `"team2"`, `"team3"`, `"team4"`, `"team5"`, `"team6"` |
| `timestamp` | string (ISO-8601 UTC) | Generation time in UTC | e.g. `"2026-10-25T10:00:00.000Z"` |
| `seq` | integer | Monotonically increasing sequence number | $\ge 0$ |
| `frame_id` | string | Reference coordinate frame of coordinates | `"robot_base"`, `"assembly_world"`, `"camera_optical_frame"` |
| `valid` | boolean | Indicates whether payload data checks passed | `true`, `false` |

## 2. Validation Status Enum

Applied across trajectory validations, kinematic checks, and quality gates:
- `PASS`: Explicitly tested and passed criteria.
- `FAIL`: Explicitly tested and failed criteria.
- `NOT_RUN`: Skipped due to an upstream failure.
- `NOT_AVAILABLE`: Metric or solver check is unsupported or unconfigured. Never falsify as passing.

## 3. Team 1 — `decision.json`

| Field | Type | Description |
|---|---|---|
| `decision_id` | string | Unique command identifier (e.g. `cmd_0001`) |
| `state` | string | Current supervisory state (`SCANNING`, `PLANNING`, `VALIDATING`, `READY`, `EXECUTING`, `PAUSED`, `REPLANNING`, `FAULT`, `COMPLETE`) |
| `next_state` | string | Target supervisory state |
| `action` | string | Action name (`request_scan`, `request_plan`, `execute_weld`, `pause_execution`, `replan`, `complete_job`) |
| `target.joint_id` | string / null | Target candidate joint identifier |
| `target.trajectory_ref` | string / null | Referenced trajectory identifier |
| `reason_code` | string | Traceable decision code (e.g. `TRAJECTORY_VALIDATED_CELL_READY`) |
| `reason_text` | string | Human-readable explanation of decision |
| `requires_human` | boolean | Indicates if manual operator confirmation is required |
| `timeout_s` | float | Execution timeout window in seconds |

## 4. Team 2 — `cell_state.json`

| Field | Type | Description |
|---|---|---|
| `robot.robot_state` | string | State: `idle`, `moving`, `welding`, `paused`, `fault`, `homing` |
| `robot.joint_positions_rad` | array[float] | Current joint angles in radians (6 DOFs) |
| `robot.tcp_position_m` | array[float] | TCP position $[x, y, z]$ in meters |
| `robot.tcp_orientation_xyzw` | array[float] | TCP orientation quaternion $[x, y, z, w]$ |
| `fixture.state` | string | State: `locked`, `unlocked`, `moving`, `error` |
| `clamps.state` | string | State: `locked`, `unlocked`, `error` |
| `process.welding_active` | boolean | Arc active flag |
| `process.current_A` | float / null | Measured welding current in Amperes |
| `process.voltage_V` | float / null | Measured welding arc voltage in Volts |
| `process.travel_speed_m_s` | float / null | Measured travel speed in meters per second |
| `safety.plc_ok` | boolean | Hardware safety circuit integrity status |
| `safety.estop_active` | boolean | E-stop trip status |
| `last_command.decision_id` | string | Echoed command decision ID |
| `last_command.status` | string | Acknowledgement status: `accepted`, `in_progress`, `completed`, `failed`, `timed_out` |

## 5. Team 3 — `process_feedback.json`

| Field | Type | Description |
|---|---|---|
| `data_quality.status` | string | Stream health: `OK`, `DEGRADED`, `STALE`, `INVALID` |
| `anomaly.status` | string | Evaluated signal status: `OK`, `ANOMALY`, `NOT_AVAILABLE` |
| `anomaly.score` | float / null | Anomaly score $[0.0, 1.0]$ |
| `predictions.quality_score` | float / null | Predicted weld quality (null until ground truth validated) |
| `predictions.defect_probability`| float / null | Predicted defect likelihood (null until ground truth validated) |
| `predictions.status` | string | Must be `NOT_AVAILABLE` in baseline simulation |
| `supervisory_team1.alert` | boolean | High-priority supervisory alert flag |

## 6. Team 4 — `correction.json`

| Field | Type | Description |
|---|---|---|
| `trajectory_id` | string | Target trajectory identifier |
| `trajectory_revision` | integer | Target revision counter |
| `measurement.deviation_m` | array[float] | Vector deviation $[dx, dy, dz]$ in meters |
| `filtered_offset_m` | array[float] | Filtered offset vector in meters |
| `proposed_absolute_offset_m` | array[float] | Absolute offset vector tied to revision |
| `within_limits` | boolean | True if offset is within allowable dynamic limit |
| `action_requested` | string | `CORRECT_WITH_REVALIDATION`, `REQUEST_REPLAN`, `REQUEST_PAUSE`, `NO_CORRECTION` |

## 7. Team 5 — `scene.json`

| Field | Type | Description |
|---|---|---|
| `calibration_status` | string | Camera calibration state: `VERIFIED`, `UNVERIFIED`, `CALIBRATING`, `FAILED` |
| `candidate_joints[].joint_id` | string | Candidate joint ID |
| `candidate_joints[].start_point_m` | array[float] | Seam start coordinate $[x, y, z]$ in meters |
| `candidate_joints[].end_point_m` | array[float] | Seam end coordinate $[x, y, z]$ in meters |
| `candidate_joints[].length_m` | float | Seam physical length in meters |
| `candidate_joints[].weld_intent_confirmed` | boolean | Must be `false` unless explicitly confirmed |
| `candidate_joints[].status` | string | Must be `CANDIDATE_REQUIRES_CONFIRMATION` for raw visual detections |

## 8. Team 6 — `trajectory.json`

| Field | Type | Description |
|---|---|---|
| `status` | string | Feasibility status: `VALIDATED_CANDIDATE`, `FAILED_VALIDATION` |
| `waypoints[].phase` | string | Motion phase: `APPROACH`, `WELD`, `RETREAT`, `TRANSFER` |
| `validation.ik` | string | Reachability check result (`PASS`, `FAIL`, `NOT_AVAILABLE`) |
| `validation.collision` | string | Collision check result (`PASS`, `FAIL`, `NOT_AVAILABLE`) |
| `next_action` | string | Recommended next step: `READY_FOR_SIMULATION`, `REJECTED`, `REPLAN_REQUIRED` |
| `failure_reason` | string / null | Descriptive rejection explanation |
