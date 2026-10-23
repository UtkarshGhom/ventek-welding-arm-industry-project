# VENTEK Autonomous Robotic Welding
## Consolidated Architecture, JSON Contracts, and Baseline Plan

**Version:** 1.0 integration proposal  
**Prepared:** 21 October 2026  
**Baseline target:** 25 October 2026  
**Status:** Consolidated from available Team 1, 3, 4, 5 and 6 reports. Team 2's report was not in the reviewed set, so its contract below must be confirmed with Team 2.

> This is a proposed integration plan, not a claim that all modules have already been implemented or validated.

## 1. Final approach

Build one complete, reproducible vertical slice before advanced algorithms:

**Known workcell → candidate seam geometry → feasible trajectory → simulated execution → cell/process status → bounded correction or safe pause → supervisory decision and logs.**

The 25 October goal is a simulation baseline, not a fully autonomous industrial welding system.

### Decisions
- **Team 1:** deterministic supervisory state machine and rule-based weld sequencing.
- **Team 2:** cell orchestration, command execution/acknowledgement, robot/fixture/clamp state.
- **Team 3:** synchronized process data, data-quality checks, baseline anomaly analytics, advisory feedback.
- **Team 4:** measured seam deviation, filtering, bounded correction proposals and replan/pause requests.
- **Team 5:** vision/point-cloud processing, part/fixture/clamp geometry and candidate seam detection.
- **Team 6:** nominal weld path, torch poses, IK, joint limits, collision checks, trajectory timing and validation.

Team 4 must not create a competing full path planner; Team 6 owns nominal planning and revalidation. Team 3 does not command motion or claim weld quality without valid labels. Geometry from Team 5 is a *candidate seam*, not proof of weld intent. Team 1 must wait for Team 2's command completion/fault acknowledgement, not merely command receipt.

## 2. Architecture and data flow

```text
Operator/job config
       |
       v
TEAM 1: supervisor / sequencing
  | request scan / plan / execute / pause / replan
  v
TEAM 5: camera/RGB-D/point cloud -> scene.json
  | candidate seams + part/fixture/clamp geometry
  v
TEAM 6: torch poses -> IK -> collision checks -> trajectory.json
  |
  v
TEAM 2: cell orchestration -> simulated execution -> cell_state.json
  |                                             |
  |                                             +----> TEAM 3
  |                                             |      analytics -> process_feedback.json
  |                                             |
  |                                             +----> TEAM 4
  |                                                    deviation -> correction.json
  +---------------------------------------------------------+
                                                            |
                                                            v
                                                   TEAM 1 supervisor
                                            continue / replan / pause / fault / finish

Independent PLC/E-stop/safety logic remains outside AI authority.
Every corrected trajectory must be revalidated by Team 6 before execution.
```

### End-to-end happy path
1. Team 1 requests a scan.
2. Team 5 publishes a valid `scene.json` with calibration status and at least one candidate seam.
3. Team 1 chooses a candidate/order using deterministic rules and requests planning.
4. Team 6 returns a `trajectory.json` with explicit validation status.
5. Team 1 authorises execution only when required checks pass and the cell is ready.
6. Team 2 simulates execution and publishes `cell_state.json` with a command acknowledgement.
7. Team 3 publishes advisory `process_feedback.json`; unavailable predictions remain `null`.
8. Team 4 publishes a bounded `correction.json` proposal or requests replan/pause.
9. Team 6 revalidates any changed path; Team 1 updates state and records logs.

## 3. Shared contract rules — freeze these before integration

Current reports conflict on timestamp format and frame names: Team 1 uses ISO-8601 UTC and `cell_base`; Team 5 uses Unix seconds and `assembly_world`; Team 6 uses ISO-8601 UTC and `robot_base`. Do not mix these silently.

**Canonical v0.1 proposal**
- `schema_version`: `"0.1"`.
- `timestamp`: ISO-8601 UTC, e.g. `"2026-10-25T10:00:00.000Z"`.
- `producer`: `team1` … `team6`.
- `seq`: increasing sequence number per stream.
- `frame_id`: actual frame of all positions in the payload.
- Units: metres, radians, seconds; electrical units explicit.
- Quaternion order: `[x, y, z, w]`.
- All positions must use a verified transform. Camera coordinates are not robot coordinates until calibrated.
- `valid` means input/data checks passed; it does not mean the action is safe.
- Validation enum: `PASS`, `FAIL`, `NOT_RUN`, `NOT_AVAILABLE`.
- Missing/stale data must be explicit; do not substitute normal-looking values.
- Each command has a unique `decision_id`; Team 2 echoes it in its acknowledgement.
- ROS 2 topics are the proposed runtime transport. JSON is the initial payload/mock contract. Later, stable fields can be converted to typed ROS messages.

Proposed transform chain: `camera_optical → assembly_world → robot_base → robot_flange → welding_tcp`. Each transform must be measured or taken from a verified model. Mark calibration unverified until then.

Recommended shared files:
```text
integration/
  schemas/{scene,trajectory,cell_state,process_feedback,correction,decision}.schema.json
  examples/{scene_ok,scene_invalid,trajectory_ok,trajectory_unreachable,
            cell_state_ready,cell_state_fault,process_feedback_unavailable,
            correction_small,correction_replan,decision_execute,decision_pause}.json
  tests/{test_schema_validation.py,test_end_to_end_mock.py}
```

## 4. Canonical JSON examples

These are illustrative mock payloads. They consolidate the reports and resolve incompatible conventions; they are not real measurements or proof of implemented algorithms.

### 4.1 Team 5 output — `scene.json`
Consumers: Teams 6 and 1. Purpose: scene geometry and candidate weld seams.

```json
{
  "schema_version": "0.1",
  "producer": "team5",
  "timestamp": "2026-10-25T10:00:00.000Z",
  "seq": 1,
  "frame_id": "assembly_world",
  "units": {"position": "m", "angle": "rad"},
  "valid": true,
  "calibration_status": "VERIFIED",
  "parts": [
    {
      "part_id": "part_001",
      "type": "workpiece",
      "mesh_uri": "meshes/workpiece.stl",
      "pose": {
        "position_m": [0.45, 0.0, 0.20],
        "orientation_xyzw": [0.0, 0.0, 0.0, 1.0]
      },
      "confidence": 0.91
    }
  ],
  "fixtures": [],
  "clamps": [],
  "candidate_joints": [
    {
      "joint_id": "candidate_001",
      "part_ids": ["part_001"],
      "joint_type": "unknown",
      "start_point_m": [0.40, 0.0, 0.20],
      "end_point_m": [0.55, 0.0, 0.20],
      "direction_unit": [1.0, 0.0, 0.0],
      "length_m": 0.15,
      "local_normal": null,
      "confidence": 0.72,
      "valid": true,
      "weld_intent_confirmed": false,
      "status": "CANDIDATE_REQUIRES_CONFIRMATION"
    }
  ],
  "warnings": []
}
```

**Baseline:** known CAD/sample point cloud or simulated RGB-D input; verify scale and calibration; filter points; use RANSAC plane fitting, DBSCAN clustering and PCA/local geometry to propose endpoints and length; emit confidence and warnings. Do not infer weld intent from geometry alone.

**Stack:** Python, OpenCV, the SDK for the actual camera (DepthAI for OAK-D or `pyrealsense2` for RealSense), Open3D, NumPy/SciPy, JSON Schema and pytest. Pin compatible versions after a sensor smoke test.

**Later:** learned seam segmentation, multi-view fusion, defect classification and uncertainty calibration, only after labelled data and a measured baseline exist.

### 4.2 Team 6 output — `trajectory.json`
Consumers: Teams 2 and 1. Purpose: candidate motion plus truthful validation results.

```json
{
  "schema_version": "0.1",
  "producer": "team6",
  "timestamp": "2026-10-25T10:01:00.000Z",
  "trajectory_id": "traj_001",
  "robot_id": "robot_mock_01",
  "coordinate_frame": "robot_base",
  "units": {"position": "m", "joint_position": "rad", "time": "s"},
  "status": "VALIDATED_CANDIDATE",
  "joint_names": ["joint_1", "joint_2", "joint_3", "joint_4", "joint_5", "joint_6"],
  "waypoints": [
    {
      "time_from_start_s": 0.0,
      "joint_positions_rad": [0.0, -0.5, 0.8, 0.0, 0.6, 0.0],
      "tcp_position_m": [0.35, 0.02, 0.24],
      "tcp_orientation_xyzw": [0.0, 0.0, 0.0, 1.0],
      "phase": "APPROACH"
    },
    {
      "time_from_start_s": 1.0,
      "joint_positions_rad": [0.1, -0.45, 0.75, 0.0, 0.65, 0.0],
      "tcp_position_m": [0.45, 0.02, 0.22],
      "tcp_orientation_xyzw": [0.0, 0.0, 0.0, 1.0],
      "phase": "WELD"
    },
    {
      "time_from_start_s": 2.0,
      "joint_positions_rad": [0.15, -0.4, 0.7, 0.0, 0.7, 0.0],
      "tcp_position_m": [0.55, 0.02, 0.22],
      "tcp_orientation_xyzw": [0.0, 0.0, 0.0, 1.0],
      "phase": "RETREAT"
    }
  ],
  "validation": {
    "ik": "PASS",
    "joint_limits": "PASS",
    "singularity": "NOT_AVAILABLE",
    "collision": "PASS",
    "velocity_acceleration": "PASS",
    "torque": "NOT_AVAILABLE"
  },
  "next_action": "READY_FOR_SIMULATION",
  "failure_reason": null
}
```

Joint values above are mock examples, not solved for the FANUC robot.

**Baseline:** verified robot model and TCP, or clearly labelled substitute; seam points to approach/weld/retreat poses; compatible IK; joint-bound and continuity checks; collision scene with part/fixtures/clamps; MoveIt 2 + OMPL if compatible; trajectory time parameterisation; final collision/path-deviation recheck; RViz/Gazebo validation.

**Stack:** URDF/Xacro, ROS 2, MoveIt 2, OMPL, RViz, Gazebo, Python metrics/tests. Ruckig is optional after baseline and requires revalidation.

**Later:** custom optimisation/planners only if tests reveal a specific limitation in the standard stack.

### 4.3 Team 2 output — `cell_state.json`
Consumers: Teams 1, 3 and 4. Team 2 owns execution state and acknowledgement.

```json
{
  "schema_version": "0.1",
  "producer": "team2",
  "timestamp": "2026-10-25T10:01:05.000Z",
  "seq": 12,
  "frame_id": "robot_base",
  "valid": true,
  "robot": {
    "robot_state": "idle",
    "joint_names": ["joint_1", "joint_2", "joint_3", "joint_4", "joint_5", "joint_6"],
    "joint_positions_rad": [0.0, -0.5, 0.8, 0.0, 0.6, 0.0],
    "tcp_position_m": [0.35, 0.02, 0.24],
    "tcp_orientation_xyzw": [0.0, 0.0, 0.0, 1.0]
  },
  "fixture": {"state": "locked", "angle_rad": 0.0},
  "clamps": {"state": "locked"},
  "process": {
    "welding_active": false,
    "current_A": null,
    "voltage_V": null,
    "travel_speed_m_s": null
  },
  "safety": {"plc_ok": true, "estop_active": false, "faults": []},
  "last_command": {
    "decision_id": "cmd_0001",
    "status": "completed",
    "message": "simulation command completed"
  }
}
```

If sensors are absent, values stay `null`; synthetic signals must be explicitly labelled as simulated. Baseline: load cell/robot, expose command interface, acknowledge accepted/in-progress/completed/failed with command ID, publish state and faults, test success and timeout/fault. Confirm exact fields with Team 2 because its report was not included in the reviewed files.

### 4.4 Team 3 output — `process_feedback.json`
Topic proposal: `/cell/process_feedback`. Consumers: Teams 4, 1 and 2. Advisory only.

```json
{
  "schema_version": "0.1",
  "producer": "team3",
  "timestamp": "2026-10-25T10:01:05.050Z",
  "seq": 25,
  "frame_id": "robot_base",
  "valid": true,
  "data_quality": {
    "status": "OK",
    "missing_channels": [],
    "stale_channels": [],
    "window_start": "2026-10-25T10:01:05.000Z",
    "window_end": "2026-10-25T10:01:05.050Z"
  },
  "features": {
    "current_mean_A": null,
    "voltage_mean_V": null,
    "travel_speed_mean_m_s": null,
    "tracking_error_mean_m": null
  },
  "anomaly": {
    "status": "NOT_AVAILABLE",
    "score": null,
    "label": null,
    "method": "rule_baseline"
  },
  "predictions": {
    "quality_score": null,
    "defect_probability": null,
    "seam_offset_m": null,
    "uncertainty": null,
    "status": "NOT_AVAILABLE"
  },
  "advisory_team4": {
    "recommendation": "NO_ADVISORY",
    "reason": "NO_VALIDATED_MODEL_OR_SIGNAL"
  },
  "supervisory_team1": {
    "alert": false,
    "reason_code": "NO_VALIDATED_ALERT"
  },
  "model": {"name": "rule_baseline", "version": "0.1"}
}
```

**Baseline:** ingest timestamped cell state and optional vision geometry; check time order, freshness, missing channels, units and ranges; log/replay; compute simple windowed features and transparent rules/statistics; then compare with Isolation Forest if data supports it. An anomaly means unusual data, not confirmed defective weld.

**Stack:** ROS 2, Python, NumPy, pandas, scikit-learn, JSON Schema, pytest and rosbag2/logging. LightGBM/XGBoost + SHAP require reliable labels. CNN-GRU + spatial MLP/VAE require the advanced-model gate, run-level splits and runtime/false-alarm comparisons. A 50 ms window does not by itself prove sub-10 ms end-to-end response.

### 4.5 Team 4 output — `correction.json`
Consumers: Teams 6, 1 and 2. Proposal only; Team 6 validates revised motion.

```json
{
  "schema_version": "0.1",
  "producer": "team4",
  "timestamp": "2026-10-25T10:01:05.060Z",
  "seq": 8,
  "frame_id": "robot_base",
  "valid": true,
  "trajectory_id": "traj_001",
  "trajectory_revision": 1,
  "joint_id": "candidate_001",
  "measurement": {
    "planned_position_m": [0.45, 0.02, 0.22],
    "observed_position_m": [0.45, 0.0205, 0.2198],
    "deviation_m": [0.0, 0.0005, -0.0002]
  },
  "filtered_offset_m": [0.0, 0.0004, -0.0001],
  "proposed_absolute_offset_m": [0.0, 0.0004, -0.0001],
  "within_limits": true,
  "action_requested": "CORRECT_WITH_REVALIDATION",
  "speed_proposal_m_s": null,
  "confidence": null,
  "reason": "bounded measurement-based proposal; validate through Team 6",
  "limits_profile": "SIMULATION_ASSUMPTIONS_ONLY"
}
```

**Baseline:** compare observed and planned seam position at the same nominal station and frame; low-pass filter; apply configurable deadband/maximum offset/rate; reject stale or invalid measurements; request replan/pause if too large. Offset is absolute relative to a trajectory revision so duplicate messages do not accumulate correction. Keep process speed fixed until signals, limits and validation exist.

Team 4 report values such as 0.02 mm deadband, 1 mm max offset, 0.25 mm/s offset-rate and 0.3 s timeout are assumptions, **not approved industrial limits**. PINN + CalculiX can be evaluated later against the measurement-only baseline on held-out synthetic runs; reported synthetic improvement does not prove physical performance. Defer MPC, online learning and full pose correction.

### 4.6 Team 1 output — `decision.json`
Consumers: Teams 2, 5 and 6; Teams 3/4 can use it for mode/logging.

```json
{
  "schema_version": "0.1",
  "producer": "team1",
  "timestamp": "2026-10-25T10:01:05.100Z",
  "seq": 7,
  "frame_id": "robot_base",
  "valid": true,
  "decision_id": "cmd_0002",
  "state": "READY",
  "next_state": "EXECUTING",
  "action": "execute_weld",
  "target": {
    "joint_id": "candidate_001",
    "trajectory_ref": "traj_001",
    "fixture_angle_rad": null
  },
  "reason_code": "TRAJECTORY_VALIDATED_CELL_READY",
  "reason_text": "Required planning checks passed and cell is ready",
  "inputs_used": {
    "scene_seq": 1,
    "trajectory_seq": 1,
    "cell_state_seq": 12,
    "process_feedback_seq": 25,
    "correction_seq": 8
  },
  "requires_human": false,
  "timeout_s": 60.0
}
```

**States:** `SCANNING`, `PLANNING`, `VALIDATING`, `READY`, `EXECUTING`, `PAUSED`, `REPLANNING`, `FAULT`, `COMPLETE`.

**Baseline:** deterministic state machine, rule-based sequencing, schema/freshness/calibration/confidence gates, one active command at a time, wait for command completion, pause on stale required inputs, fault on E-stop/PLC/robot/collision fault, resume only after cause clears and required human confirmation, and log every decision. Keep thresholds in YAML and mark assumptions until tested.

**Later:** compare rules with exhaustive/beam search. RL/PPO only if a validated simulator and data exist and the baseline/search has a measured limitation; Team 6's checks must veto unsafe paths.

## 5. Baseline acceptance checklist by team

### Team 1 — Supervisor
- Runnable state machine on mock inputs.
- Happy path: scan → plan → validate → execute → complete.
- Fault paths: stale input, invalid schema, unreachable path, timeout and safety fault.
- Unique command IDs, acknowledgement required, deterministic replay and schema-valid outputs.

### Team 2 — Orchestration
- One simulated robot/cell plus minimum fixture/clamp state.
- Command acknowledgement lifecycle with ID and accepted/in-progress/completed/failed.
- `cell_state.json` published with timestamps, state and faults.
- One successful and one failed/timed-out command demonstrated.

### Team 3 — Analytics
- Repeatable ingest/log/replay; data freshness and missing-channel checks.
- Simple features + rule/statistical baseline.
- One injected anomaly detected and normal sample checked.
- Unknown quality/defect predictions remain null; report false alarms, misses and latency.

### Team 4 — Adaptation
- Shared-frame deviation measurement, filtering and bounded absolute offset.
- Stale/invalid/out-of-limit input triggers pause/replan.
- Duplicate correction cannot accumulate; Team 6 revalidates it.
- No PINN/MPC in the baseline control path.

### Team 5 — Perception
- One known CAD/sample/simulated depth scene.
- Verified scale and explicit calibration status.
- One `scene.json` with part/fixture/clamp context and a candidate seam.
- Geometry visualisation and endpoint/length sanity checks; candidate distinct from confirmed weld.

### Team 6 — Planning
- Verified robot model or explicitly labelled substitute.
- One straight reachable seam with approach/weld/retreat.
- IK, joint-limit and collision checks where supported; timed simulated trajectory.
- Unreachable pose or blocked path returns explicit failure and no executable trajectory.

### Project lead / integration
- Freeze schemas/frames, examples and validators.
- One documented launch/run instruction.
- Happy-path end-to-end run and at least one injected failure.
- Logs, configuration, package versions, test report and demo evidence saved.
- Never label a simulated result as physical welding or industrial-quality validation.

## 6. Build sequence before 25 October

**A. Freeze interfaces first.** Approve timestamp, frames, units, quaternion order, field names and status enums. Team 2 confirms command lifecycle. Add JSON Schemas and positive/negative examples.

**B. Mock-first module tests.** Team 5 writes `scene.json`; Team 6 consumes it and returns `trajectory.json`; Team 2 simulates command/acknowledgement and writes `cell_state.json`; Team 3 consumes synthetic state; Team 4 consumes synthetic deviations; Team 1 orchestrates the state machine.

**C. One vertical slice in simulation.** Load simplified cell geometry and one robot model; show workpiece, fixture, clamps and torch/TCP; plan one seam; visualise and simulate; publish state; log the run; repeat with an unreachable pose or stale message.

**D. Acceptance review.** Run schema tests and happy/fault scenarios from a clean checkout. Unsupported checks must say `NOT_AVAILABLE`, not pass. Freeze a baseline tag before advanced algorithms.

## 7. Suggested repository layout

```text
ventek_autonomous_welding/
  README.md
  config/{robot_config.yaml,camera_config.yaml,safety_limits.yaml,system_config.yaml}
  docs/{architecture/,interfaces/,teams/,decisions/}
  integration/{schemas/,examples/,launch/,tests/}
  src/{team1_autonomy/,team2_orchestration/,team3_multimodal/,
       team4_adaptive/,team5_vision/,team6_planning/}
  simulation/{robot/,fixtures/,worlds/,scenarios/}
  meshes/
  data/{mock/,raw/,processed/,logs/}
  tests/
```

Keep large point clouds, videos, rosbag2 files and model checkpoints out of normal Git unless LFS/dedicated storage is deliberately set up.

## 8. Advanced algorithm upgrade gates

| Team | Baseline | Upgrade only when |
|---|---|---|
| T1 | State machine + deterministic rules | Rules/search have measured sequencing limits and validated simulation/data support comparison |
| T2 | Reliable command/state/acknowledgement | Verified coordination constraints require more complex scheduling |
| T3 | Data-quality gates + rules/statistics + Isolation Forest | Reliable labels/held-out runs exist and advanced model beats baseline at acceptable false-alarm/runtime cost |
| T4 | Filtered measurement correction + bounds | PINN/CalculiX beats measurement-only baseline on held-out cases; control limits reviewed |
| T5 | Calibrated geometry + classical candidate detection | Labelled examples show learned perception improves accuracy and confidence calibration |
| T6 | IK + joint limits + collision-aware planning + timing | Test evidence identifies a gap the standard MoveIt/OMPL stack cannot meet |

Do not adopt an algorithm because it is fashionable or has one impressive synthetic result. It must beat the baseline on a defined metric under comparable held-out tests and retain explicit failure/safety handling.

## 9. Minimum integration scenarios

1. Valid scene → reachable seam → collision-free trajectory → command completed → Team 1 COMPLETE.
2. No candidate seam → rescan/human review; no execution.
3. Unverified calibration or low confidence → block planning or require review.
4. Unreachable seam → explicit IK failure; no executable trajectory.
5. Clamp collision → collision failure or validated alternative.
6. Stale Team 3/4 input → reject/ignore according to policy; never treat as normal.
7. Large deviation → Team 4 requests replan/pause; Team 6 revalidates.
8. Command acknowledgement timeout → pause/escalate/fault.
9. E-stop/PLC/robot fault → independent safety response; AI cannot override.
10. Schema mismatch → reject, log and stop progression.

## 10. Open decisions for the integration meeting

1. Confirm actual robot model, joint limits, kinematics, flange and TCP. CAD meshes alone are not a moving robot model.
2. Confirm Ubuntu/ROS 2/Gazebo versions and avoid mixing incompatible simulator stacks.
3. Confirm Team 2's exact cell-state fields, command lifecycle, fixture actuation and safety boundary.
4. Confirm camera model, working distance, depth scale, intrinsics/extrinsics and calibration owner.
5. Decide who confirms weld intent using drawings/operator labels.
6. Approve measured transforms between camera, assembly, robot base, flange and TCP.
7. Inventory real process signals, rates, units and timestamp source.
8. Agree how Team 4 proposals are passed to Team 6 for revalidation.
9. Define quality ground truth before emitting quality/defect predictions.
10. Clarify timing requirements: model inference, analytics latency, sensor-to-decision or sensor-to-motion.

## Final recommendation

**Build the smallest complete and testable loop, not six advanced standalone prototypes.** The baseline demo should show one known scene, `scene.json`, one validated `trajectory.json`, simulated execution and `cell_state.json`, advisory Team 3 feedback, one bounded Team 4 correction/replan case, and Team 1's decision/log. Use clearly labelled mock data where a sensor/module is not ready. Once this works reproducibly, teams can upgrade behind the frozen interfaces.
