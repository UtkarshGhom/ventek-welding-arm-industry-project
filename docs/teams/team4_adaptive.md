# Team 4 — Adaptive Welding and Real-Time Quality Control

## 1. Product Role
Closes the seam-tracking feedback loop by measuring deviation between the nominal trajectory and observed workpiece seams, applying filtering, and proposing bounded corrections or requesting a supervisor replan/pause.

## 2. Core Responsibilities
- **Deviation Measurement**:
  - Compares planned TCP position against observed seam position in a unified coordinate frame (`robot_base`).
- **Filtering & Deadband**:
  - Configurable deadband (0.05 mm) to avoid actuator chatter.
  - Low-pass filtering to reject sensor noise.
- **Absolute Offsets Tied to Trajectory Revisions**:
  - Uses absolute offsets tied to `trajectory_id` and `trajectory_revision`. Duplicate or delayed messages do not accumulate error.
- **Limits Envelope & Revalidation Rule**:
  - Bounded corrections (<= 1.0 mm) emit `action_requested: "CORRECT_WITH_REVALIDATION"`.
  - Team 6 MUST revalidate the corrected waypoints before the robot moves. Team 4 does not possess motion planning or collision authority.
  - Large deviations (> 1.0 mm) emit `action_requested: "REQUEST_REPLAN"` or `"REQUEST_PAUSE"`.
- **Process Parameters Freeze**:
  - Process parameters (welding current, voltage, travel speed) remain fixed in the baseline.

## 3. Technology Stack
- **Language**: Python 3.10+
- **Framework**: ROS 2 Humble, NumPy, JSON Schema
- **Location**: `src/team4_adaptive/` (`AdaptiveController`)

## 4. Interface Contracts
- **Produces**: `correction.json` conforming to [`docs/interfaces/correction_schema.json`](../interfaces/correction_schema.json)
- **Consumes**:
  - Team 6 `trajectory.json` ([`trajectory_schema.json`](../interfaces/trajectory_schema.json))
  - Team 5 `scene.json` ([`scene_schema.json`](../interfaces/scene_schema.json))
  - Team 3 `process_feedback.json` ([`process_feedback_schema.json`](../interfaces/process_feedback_schema.json))

## 5. Upgrade Gate (Baseline Target: 25 October)
- **Baseline**: Filtered measurement correction + deadband + bounded envelope + replan trigger.
- **Upgrade to PINN/CalculiX/MPC/RL**: Only if physical or held-out synthetic trials show that classical measurement feedback cannot track thermo-elastic deformation within required tolerances.
