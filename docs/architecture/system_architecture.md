# VENTEK System Architecture & Data Flow

## 1. High-Level Architecture

```text
Operator / Job Recipe
         |
         v
TEAM 1: Supervisor / State Machine
  | 
  |-- request_scan --> TEAM 5: Perception (RGB-D / Point Cloud)
  |                       |
  |                       v publishes scene.json (candidate seams + geometry)
  |
  |-- request_plan --> TEAM 6: Motion Planning (MoveIt 2 / OMPL / IK)
  |                       |
  |                       v publishes trajectory.json (approach / weld / retreat)
  |
  |-- execute_weld --> TEAM 2: Cell Orchestration (Gazebo Sim / Robot Driver)
  |                       |
  |                       +---> publishes cell_state.json
  |                       |       |
  |                       |       +---> TEAM 3: Multimodal Analytics
  |                       |       |       └── publishes process_feedback.json (advisory)
  |                       |       |
  |                       |       +---> TEAM 4: Adaptive Control
  |                       |               └── publishes correction.json (deviation offset)
  |                       |
  |                       v echoes command completion / fault
  +<----------------------+
```

## 2. End-to-End Sequence (Happy Path)

1. **Job Start**: Team 1 supervisor enters `SCANNING` and commands Team 5 to scan the setup.
2. **Perception**: Team 5 acquires point cloud, checks calibration, detects candidate seam endpoints, and publishes `scene.json`.
3. **Sequencing Guard**: Team 1 evaluates candidate seam geometry and confidence, transitions to `PLANNING`, and requests motion planning from Team 6.
4. **Trajectory Generation**: Team 6 computes Cartesian torch poses, solves IK, validates reachability and obstacle clearance, and outputs `trajectory.json` with status `VALIDATED_CANDIDATE`.
5. **Execution Authorization**: Team 1 confirms trajectory validity and checks `cell_state.json` (robot idle, clamps locked, safety OK), issues `execute_weld` decision with unique `decision_id`, and transitions to `EXECUTING`.
6. **Simulated Execution**: Team 2 executes the trajectory waypoints, turns on simulated process current, updates kinematics, and echoes command completion in `cell_state.json`.
7. **Advisory Analytics**: Team 3 checks telemetry freshness, computes windowed features, evaluates baseline anomaly rules, and publishes `process_feedback.json`.
8. **Adaptive Tracking**: Team 4 monitors observed TCP error, filters high-frequency noise, verifies offsets remain within allowable safety bounds, and requests revalidation through Team 6.
9. **Supervisory Completion**: Team 1 confirms Team 2's command completion acknowledgement, records the audit trail, and transitions to `COMPLETE`.

## 3. Fault & Recovery Paths

- **No Candidate Seam**: Team 1 pauses progression; requests rescan or operator manual selection.
- **Unreachable Seam / Kinematic Limit Exceeded**: Team 6 returns `status: "FAILED_VALIDATION"`, `next_action: "REJECTED"`. Team 1 halts planning; no motion is authorized.
- **Obstacle / Clamp Collision**: Team 6 returns `collision: "FAIL"`. Team 1 halts execution or requests fixture repositioning.
- **Large Seam Deviation**: Team 4 emits `action_requested: "REQUEST_REPLAN"`. Team 1 safely pauses motion (`decision: pause_execution`).
- **Emergency Stop / PLC Fault**: Independent safety circuits immediately halt cell motion. Team 2 reports `robot_state: "fault"` and `estop_active: true`. Team 1 transitions to `FAULT`.
