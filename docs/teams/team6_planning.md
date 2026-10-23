# Team 6 — Robotic Path Planning, IK, and Motion

## 1. Product Role
Transforms confirmed candidate seams into collision-free, kinematically feasible, time-parameterized robot trajectories. Revalidates revised motion proposals from Team 4 before cell execution.

## 2. Core Responsibilities
- **Torch Pose Generation**:
  - Derives approach, weld (lead/tilt angle), and retreat torch poses from seam endpoints and surface normals.
  - Distinguishes seam-following segments from approach, retreat, and transfer motions.
- **Feasibility Checks & Truth-in-Reporting**:
  - Evaluates Inverse Kinematics (reachability), joint limits, and collision clearance.
  - Reports validation results using explicit enums: `PASS`, `FAIL`, `NOT_RUN`, `NOT_AVAILABLE`.
  - Unsupported checks (such as singularity or dynamic torque) must be marked `NOT_AVAILABLE`, never falsified as passing.
- **Revalidation Authority**:
  - Re-evaluates modified waypoints proposed by Team 4 to ensure offsets do not cause joint limits violations or collisions with clamps.
- **Rejection & Failure Handling**:
  - Unreachable seams or blocked paths emit `status: "FAILED_VALIDATION"`, `next_action: "REJECTED"`, and a descriptive `failure_reason`.

## 3. Technology Stack
- **Language**: Python 3.10+ / C++
- **Framework**: ROS 2 Humble, URDF/Xacro, MoveIt 2, OMPL, RViz 2
- **Robot Model**: KUKA KR 6 R900 sixx (901 mm reach, 6 kg payload)
- **Location**: `src/team6_planning/` (`TrajectoryPlanner`)

## 4. Interface Contracts
- **Produces**: `trajectory.json` conforming to [`docs/interfaces/trajectory_schema.json`](../interfaces/trajectory_schema.json)
- **Consumes**:
  - Team 5 `scene.json` ([`scene_schema.json`](../interfaces/scene_schema.json))
  - Team 4 `correction.json` ([`correction_schema.json`](../interfaces/correction_schema.json))

## 5. Upgrade Gate (Baseline Target: 25 October)
- **Baseline**: Verified KUKA robot model + MoveIt 2 / OMPL + Approach/Weld/Retreat waypoint IK & collision validation.
- **Upgrade to Custom Optimizers / Ruckig**: Benchmark standard MoveIt time-parameterization first; add custom optimizers only if benchmarking exposes specific cycle-time or jerk limitations.
