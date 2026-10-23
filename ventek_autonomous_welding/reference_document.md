# VENTEK Autonomous Welding

## Vision-Based Automatic Welding Path and Process Planning for Robotic Manufacturing Cells

> **One project. Six teams. One architecture.**
>
> **Build independently. Integrate continuously.**

---

## 1. What Is This Project?

VENTEK Autonomous Welding is a collaborative robotics and AI project focused on reducing the amount of manual programming and teaching required for robotic welding cells.

The central objective is:

> **Given a new welding setup containing a part, fixtures, and clamps, automatically understand the complete setup and generate an executable, collision-free welding sequence/path that a robot can use instead of manually teaching every point.**

The long-term system is intended to combine:

- Computer vision
- RGB-D / depth sensing
- 3D scene understanding
- Point-cloud processing
- Weld-joint detection
- Geometric reasoning
- Inverse kinematics
- Motion planning
- Collision checking
- Robot and fixture coordination
- Multimodal sensor fusion
- Predictive analytics
- Adaptive control
- Digital twins / simulation
- Cognitive decision-making
- Edge AI

This repository is the **single shared technical repository** for the project.

---

# 2. The Problem We Are Solving

## 2.1 Existing Industrial Workflow

A typical workflow currently involves:

```text
Customer Requirement
        ↓
Part Setup
        ↓
Fixture + Clamp Setup
        ↓
Manual Weld-Joint Identification
        ↓
Manual Weld Sequence Planning
        ↓
Manual Torch Orientation
        ↓
Manual Robot Teaching
        ↓
Collision / Reachability Checks
        ↓
Test Motion
        ↓
Modify Points
        ↓
Final Welding
```

This process depends heavily on skilled operators/programmers.

## 2.2 Major Problems

The project is intended to address:

- Time-consuming manual robot teaching
- Dependence on experienced programmers
- Repeated programming for new components
- Fixture and clamp interference
- Robot collision risk
- Tight-angle accessibility
- Weld orientation constraints
- Weld direction constraints
- Home-position selection
- Robot reachability
- Different welding processes
- Different materials/process parameters
- Rework when the real setup differs from the planned setup
- Limited scalability

---

# 3. Target System

The intended workflow is:

```text
REAL WELDING SETUP
        ↓
RGB-D / DEPTH SCAN
        ↓
3D SCENE RECONSTRUCTION
        ↓
PART / FIXTURE / CLAMP IDENTIFICATION
        ↓
WELD-JOINT DETECTION
        ↓
WELD GEOMETRY EXTRACTION
        ↓
WELD SEQUENCE / PATH GENERATION
        ↓
TORCH POSE GENERATION
        ↓
IK + REACHABILITY
        ↓
SINGULARITY CHECK
        ↓
COLLISION CHECK
        ↓
TRAJECTORY GENERATION
        ↓
ROBOT + FIXTURE COORDINATION
        ↓
SIMULATION / DIGITAL TWIN
        ↓
VALIDATION
        ↓
REAL ROBOT EXECUTION
        ↓
MONITORING
        ↓
DEVIATION / QUALITY DETECTION
        ↓
ADAPTIVE CORRECTION
        ↓
RE-PLANNING
```

The eventual cognitive layer should sit across this pipeline and determine what action should happen next.

---

# 4. Project Philosophy

## 4.1 The Goal Is NOT Six Independent Projects

There are six teams, but there is only **one system**.

Bad approach:

```text
Team 1 → builds an RL model
Team 2 → builds ROS nodes
Team 3 → builds a classifier
Team 4 → builds MPC
Team 5 → builds YOLO
Team 6 → builds IK

...and nothing connects.
```

Correct approach:

```text
Team 5 → scene.json
             ↓
Team 6 → trajectory.json
             ↓
Team 2 → execution / cell_state
             ↓
Team 3 → process understanding
             ↓
Team 4 → correction
             ↓
Team 6 → re-plan

Team 1 coordinates decisions across the system.
```

---

# 5. Core Rule

> ## Build Independently. Integrate Continuously.

Every team should be able to develop independently using:

- Mock data
- Simulated inputs
- Frozen interface contracts
- Sample scenarios
- Unit tests

A team should never say:

> "We cannot start until Team X finishes."

Instead:

> "We will develop against the agreed interface and mock data, then replace the mock input with the real module."

---

# 6. Official Six-Team Structure

| Team | Domain | Main Question |
|---|---|---|
| **T1** | Cognitive Autonomous Welding | What should the system do next? |
| **T2** | Multi-Agent / Cell Orchestration | How do robot, fixtures, PLC and cell agents work together? |
| **T3** | Multimodal AI & Predictive Analytics | What is happening in the process? |
| **T4** | Adaptive Welding & Real-Time Control | How should the system respond to deviations? |
| **T5** | Computer Vision & Weld Intelligence | What exists in the physical scene? |
| **T6** | Path Planning, IK & Robot Motion | Can the robot physically execute the weld? |

---

# 7. System Architecture

```text
                         ┌─────────────────────────┐
                         │        TEAM 1            │
                         │ COGNITIVE AUTONOMY       │
                         │ Decision / Digital Twin  │
                         └───────────┬─────────────┘
                                     │
                    High-level decisions / state
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         │                           │                           │
         ▼                           ▼                           ▼
     TEAM 2                       TEAM 4                     TEAM 6
 Orchestration               Adaptive Control           Motion Planning
         ▲                           ▲                           ▲
         │                           │                           │
         │                           │                           │
         │                    correction.json              scene.json
         │                           ▲                           ▲
         │                           │                           │
         │                         TEAM 3                      TEAM 5
         │                    Multimodal AI               Computer Vision
         │
         └────────────── Robot / Fixture / PLC ────────────────┘
```

---

# 8. End-to-End Data Flow

## 8.1 Initial Setup

Team 5 observes:

```text
Part
Fixture
Clamp
Welding Region
```

and generates:

```text
scene.json
```

## 8.2 Planning

Team 6 consumes `scene.json` and generates:

```text
trajectory.json
```

## 8.3 Execution

Team 2 consumes the trajectory and coordinates:

```text
Robot
Fixture
Clamp
PLC
Safety
```

and generates:

```text
cell_state.json
```

## 8.4 Process Understanding

Team 3 consumes cell/process data and generates:

```text
process indicators
anomalies
quality predictions
```

## 8.5 Adaptation

Team 4 consumes feedback and generates:

```text
correction.json
```

## 8.6 Replanning

Team 6 applies the correction and generates a revised trajectory.

## 8.7 Cognitive Decision

Team 1 consumes the state of the complete system and produces:

```text
decision.json
```

---

# 9. Team 1 — Cognitive Autonomous Welding

## Mission

> Build the high-level intelligence that decides what the welding system should do next.

## Official Research Direction

- Cognitive autonomous welding
- Multimodal sensor fusion
- Deep reinforcement learning
- Digital twin synchronization
- Edge AI

## Responsibilities

Team 1 owns:

- High-level system state
- Decision-making
- Autonomous process sequencing
- Decision confidence
- Digital twin synchronization
- RL experimentation
- Edge inference
- High-level safety-aware decisions

Team 1 does **not** own low-level motor control or basic perception.

## Inputs

Team 1 may consume:

```text
T2 → cell_state.json
T3 → process/quality information
T4 → correction state
T5 → scene state
T6 → planning state
```

## Outputs

```text
decision.json
```

Example:

```json
{
  "decision_id": "decision_001",
  "timestamp": 1728000000,
  "state": "JOINT_COMPLETED",
  "action": "MOVE_TO_NEXT_JOINT",
  "target": "joint_002",
  "reason": "Current weld completed and next joint is reachable",
  "confidence": 0.94
}
```

## Internal Structure

```text
src/team1_autonomy/
├── decision/
├── state_estimation/
├── reinforcement_learning/
├── digital_twin/
└── edge_ai/
```

## Development Approach

Do not begin with RL.

Recommended progression:

```text
Rule-Based State Machine
        ↓
State + Action Representation
        ↓
Simulation Environment
        ↓
Baseline Policy
        ↓
RL Experiment
        ↓
Policy Evaluation
        ↓
Edge Deployment
```

## First Milestone

A working rule-based decision engine that can:

1. Receive system state
2. Identify current process stage
3. Select a next action
4. Explain the reason
5. Output structured JSON
6. Reject unsafe actions
7. Log decisions

## Important Questions

- What exactly is autonomous?
- What is the state space?
- What is the action space?
- Which actions are allowed?
- Which actions are prohibited?
- What is the reward?
- What constitutes successful welding?
- What happens if confidence is low?
- When should the system stop?
- When should it request human intervention?

---

# 10. Team 2 — Multi-Agent / Cell Orchestration

## Mission

> Coordinate all physical and software agents in the welding cell.

## Agents

Potential agents include:

- Robot
- Fixture
- Clamp
- PLC
- Camera
- Sensors
- Safety controller
- Digital twin
- Supervisory software

## Responsibilities

- ROS 2 communication
- Robot coordination
- Fixture coordination
- Clamp control
- PLC communication
- OPC-UA where required
- Execution state
- Agent synchronization
- Safety monitoring
- Recovery states
- Execution logging

## Inputs

Primary input:

```text
trajectory.json
```

Other inputs:

```text
decision.json
```

## Outputs

```text
cell_state.json
```

## Internal Structure

```text
src/team2_orchestration/
├── ros2/
├── robot_coordination/
├── fixture_control/
├── plc/
└── safety/
```

## First Milestone

Demonstrate:

```text
Trajectory
    ↓
Robot Agent
    ↕
Fixture Agent
    ↕
Controller
```

in simulation.

## Important Questions

- What are the agents?
- What does each agent publish?
- What commands does each agent accept?
- What happens when an agent fails?
- How is synchronization handled?
- What is the safe state?
- How does the system stop?
- How does it resume?
- What is the PLC interface?
- Which actions require acknowledgement?

---

# 11. Team 3 — Multimodal AI & Predictive Analytics

## Mission

> Combine sensor and process information to understand what is happening during welding.

## Responsibilities

- Data acquisition
- Data synchronization
- Preprocessing
- Feature extraction
- Sensor fusion
- Anomaly detection
- Quality prediction
- Process prediction
- Multimodal representation

## Potential Inputs

```text
RGB
Depth
Point Cloud
Robot Telemetry
Joint Error
Current
Voltage
Temperature
Vibration
Path Error
Fixture State
Quality Labels
```

## Internal Structure

```text
src/team3_multimodal/
├── data_acquisition/
├── synchronization/
├── sensor_fusion/
├── predictive_models/
└── anomaly_detection/
```

## First Milestone

Create a synchronized dataset:

```text
timestamp
robot_state
current
voltage
temperature
vibration
vision_error
quality_label
```

Then establish a baseline anomaly/quality model.

## Important Questions

- What sensors actually exist?
- What are their sampling rates?
- How are timestamps synchronized?
- What is the ground truth?
- What defines a good weld?
- What defines a bad weld?
- Which features are useful?
- Which model is justified?
- Can it operate in real time?
- Where will inference run?

---

# 12. Team 4 — Adaptive Welding & Real-Time Control

## Mission

> Respond when actual execution differs from the planned process.

## Responsibilities

- Path deviation calculation
- Error modelling
- Adaptive control
- MPC
- Path correction
- Process parameter adaptation
- Quality feedback
- Replanning triggers

## Internal Structure

```text
src/team4_adaptive/
├── controllers/
├── mpc/
├── error_model/
├── path_correction/
└── quality_feedback/
```

## First Development Target

Do not start with a complex DRL/MPC architecture.

First build:

```text
Planned Path
     ↓
Actual Path
     ↓
Calculate Error
     ↓
Correction
     ↓
Corrected Path
```

## Important Questions

- What exactly is path error?
- Which sensor measures it?
- What is the control frequency?
- What is the maximum correction?
- What prevents unstable correction?
- When should welding stop?
- When should replanning happen?
- What is the safe fallback?
- How is improvement measured?

---

# 13. Team 5 — Computer Vision & Weld Intelligence

## Mission

> Understand the physical welding setup and convert it into structured geometric information.

This is a critical team for the initial physical prototype.

## Initial Sensor

The initial prototype can use:

**OAK-D Lite / RGB-D depth camera**

Primary purpose:

- Scene scanning
- RGB capture
- Depth
- Point clouds
- Geometric understanding

The initial camera should not automatically be treated as the final sensor for arc/weld-pool monitoring.

## Pipeline

```text
OAK-D
  ↓
RGB + Depth
  ↓
Calibration
  ↓
Point Cloud
  ↓
Noise Filtering
  ↓
Scene Segmentation
  ↓
Part / Fixture / Clamp Detection
  ↓
Weld-Joint Detection
  ↓
Geometry Extraction
  ↓
scene.json
```

## Responsibilities

### Scene

Identify:

- Part
- Fixture
- Clamp
- Other relevant objects

### Weld

Estimate:

- Joint location
- Start point
- End point
- Length
- Joint type where possible
- Surface normal
- Confidence

### Later

- In-process weld monitoring
- Weld quality inspection
- Defect detection
- Reflection/glare robustness

## Internal Structure

```text
src/team5_vision/
├── camera/
├── calibration/
├── pointcloud/
├── segmentation/
├── weld_detection/
└── quality_inspection/
```

## First Milestone

Real physical setup:

```text
Part + Fixture + Clamp
        ↓
OAK-D
        ↓
RGB-D
        ↓
Point Cloud
        ↓
Scene Segmentation
        ↓
Weld Joint
        ↓
3D Coordinates
        ↓
scene.json
```

## Important Questions

- What is the working distance?
- Is the depth reliable on the target surfaces?
- How are reflective metal surfaces handled?
- What calibration method is used?
- Which coordinate frame is the output in?
- How is point-cloud noise filtered?
- How is the part separated from fixtures?
- How is the weld joint detected?
- What confidence is assigned?
- What data is required?
- Can the output be consumed directly by Team 6?

---

# 14. Team 6 — Path Planning, IK & Robot Motion

## Mission

> Convert weld geometry into a physically executable robot trajectory.

## Responsibilities

- Forward kinematics
- Inverse kinematics
- Jacobian
- Reachability
- Joint limits
- Singularity handling
- Collision checking
- Torch orientation
- Trajectory generation
- Trajectory optimization
- MoveIt 2 integration
- Robot program generation

## Pipeline

```text
scene.json
    ↓
Weld Path
    ↓
Torch Poses
    ↓
IK
    ↓
Joint Limits
    ↓
Reachability
    ↓
Singularity Check
    ↓
Collision Check
    ↓
Torch Constraints
    ↓
Trajectory Optimization
    ↓
trajectory.json
```

## Internal Structure

```text
src/team6_planning/
├── fk_ik/
├── jacobian/
├── moveit/
├── collision/
├── reachability/
├── trajectory/
└── optimization/
```

## First Milestone

Use mock data:

```text
scene_001.json
       ↓
Weld Path
       ↓
Torch Poses
       ↓
IK
       ↓
Collision
       ↓
Trajectory
```

Do not wait for Team 5's physical perception system.

## Important Questions

- What robot is being used?
- What is the kinematic chain?
- Which IK solver?
- What are joint limits?
- How are singularities handled?
- What is the TCP?
- What torch orientation is required?
- What collision geometry is available?
- Which planner is used?
- What constitutes a valid trajectory?
- How is the trajectory exported?
- Can it be executed on the real robot?

---

# 15. TEAM BOUNDARIES

Use this table when deciding who owns a task.

| Task | Owner | Supporting |
|---|---|---|
| Camera driver | T5 | T2 |
| Camera calibration | T5 | T6 |
| Point cloud | T5 | T6 |
| Part detection | T5 | T3 |
| Fixture detection | T5 | T3 |
| Clamp detection | T5 | T3 |
| Weld detection | T5 | T3 |
| Weld geometry | T5 | T6 |
| Weld sequence | T1/T6 | T5 |
| Torch pose | T6 | T5 |
| IK | T6 | T1 |
| Collision | T6 | T2 |
| Trajectory | T6 | T2 |
| Robot control | T2 | T6 |
| Fixture control | T2 | T6 |
| PLC | T2 | T1 |
| Telemetry | T2/T3 | T4 |
| Sensor fusion | T3 | T5 |
| Quality prediction | T3 | T4 |
| Path deviation | T4 | T3/T6 |
| Adaptive correction | T4 | T6 |
| Replanning | T6 | T4/T1 |
| High-level decision | T1 | All |
| Digital twin | T1 | T2/T6 |
| RL | T1 | T6 |
| Safety state | T2 | T1 |
| System integration | All | Project Lead |

---

# 16. INTERFACE CONTRACTS

These are **project contracts**.

If a team changes a contract, it must be discussed before implementation changes are merged.

---

## 16.1 Scene Contract

### File

```text
docs/interfaces/scene_schema.json
```

### Direction

```text
T5 → T6 / T1
```

### Purpose

Describe the physical setup.

### Minimum information

```json
{
  "scene_id": "scene_001",
  "coordinate_frame": "world",
  "part": {},
  "fixtures": [],
  "clamps": [],
  "weld_joints": []
}
```

### Weld Joint

```json
{
  "id": "joint_001",
  "type": "fillet",
  "start": [x, y, z],
  "end": [x, y, z],
  "length": 0.25,
  "normal": [nx, ny, nz],
  "confidence": 0.92
}
```

### Contract Requirements

T5 must guarantee:

- Valid JSON
- Correct units
- Known coordinate frame
- Numeric coordinates
- Confidence where applicable
- Unique IDs

T6 must not silently reinterpret the coordinate frame.

---

# 17. TRAJECTORY CONTRACT

### File

```text
docs/interfaces/trajectory_schema.json
```

### Direction

```text
T6 → T2 / T1
```

### Purpose

Describe executable robot motion.

### Required concepts

- Trajectory ID
- Robot ID
- Joint names
- Waypoints
- Time
- Joint positions
- TCP pose
- Validation results

Example:

```json
{
  "trajectory_id": "traj_001",
  "robot": "robot_01",
  "joint_names": [
    "joint_1",
    "joint_2",
    "joint_3"
  ],
  "waypoints": [
    {
      "time": 0.0,
      "positions": [0.0, 0.5, 0.1],
      "tcp_pose": {}
    }
  ],
  "validation": {
    "reachable": true,
    "collision_free": true,
    "joint_limits_ok": true
  }
}
```

### T6 Guarantees

A trajectory marked valid must have passed the project's agreed validation checks.

### T2 Guarantees

T2 must not modify trajectory data without recording the modification.

---

# 18. CELL STATE CONTRACT

### File

```text
docs/interfaces/cell_state_schema.json
```

### Direction

```text
T2 → T1 / T3 / T4
```

### Purpose

Represent the current physical state of the cell.

Example:

```json
{
  "timestamp": 1728000000,
  "robot": {
    "state": "EXECUTING",
    "joint_positions": [],
    "tcp_pose": {}
  },
  "fixture": {
    "state": "LOCKED",
    "pose": {}
  },
  "clamps": [],
  "welding": {
    "state": "ACTIVE",
    "current": 120.0,
    "voltage": 22.0
  }
}
```

---

# 19. SENSOR DATA CONTRACT

### Direction

```text
T2 / sensors → T3 / T4
```

Minimum principle:

Every sensor observation should have a timestamp.

Potential fields:

```text
timestamp
sensor_id
value
unit
frame
quality
```

Never combine sensor measurements without understanding their timestamps.

---

# 20. CORRECTION CONTRACT

### File

```text
docs/interfaces/correction_schema.json
```

### Direction

```text
T4 → T6 / T2
```

Example:

```json
{
  "trajectory_id": "traj_001",
  "deviation": {
    "x": 0.002,
    "y": -0.001,
    "z": 0.003
  },
  "severity": "MEDIUM",
  "action": "OFFSET_PATH",
  "correction": {
    "dx": 0.001,
    "dy": 0.0,
    "dz": 0.002
  },
  "confidence": 0.88
}
```

---

# 21. DECISION CONTRACT

### File

```text
docs/interfaces/decision_schema.json
```

### Direction

```text
T1 → T2 / T4 / T6
```

Example:

```json
{
  "decision_id": "decision_001",
  "state": "PATH_DEVIATION",
  "action": "REQUEST_REPLAN",
  "target": "trajectory_001",
  "reason": "Deviation exceeded threshold",
  "confidence": 0.91
}
```

---

# 22. CONTRACT RULES

Every interface must define:

1. Owner
2. Consumer
3. Schema
4. Units
5. Coordinate frame
6. Required fields
7. Optional fields
8. Valid ranges
9. Error behavior
10. Version

## Never do this

```text
Team 5:
"We changed the output format."

Team 6:
"My code stopped working."
```

## Do this

```text
Issue:
Change scene schema from v1 → v2

Reason:
Add weld normal

Impact:
Team 6

Migration:
Old normal defaults to estimated value

Approval:
T5 + T6 + Project Lead
```

---

# 23. COORDINATE FRAME STANDARD

Use:

```text
WORLD
 ├── ROBOT_BASE
 │      └── TCP / WELDING_GUN
 │
 ├── CAMERA
 │
 └── FIXTURE
        └── PART
```

Every 3D coordinate must specify its frame.

Use SI units:

- Distance → metres
- Time → seconds
- Angle → radians

For orientations use:

```text
[x, y, z, w]
```

Quaternion convention.

---

# 24. MOCK DATA

Mock data is mandatory for parallel development.

## Directory

```text
data/mock/
```

## Recommended files

```text
scene_001.json
scene_002.json
trajectory_001.json
cell_state_001.json
sensor_stream_001.csv
correction_001.json
decision_001.json
```

## Golden Scenarios

### Scenario 1 — Simple

- One part
- One fixture
- Two clamps
- One weld

### Scenario 2 — Medium

- Multiple joints
- Multiple clamps
- Different orientations

### Scenario 3 — Difficult

- Tight-angle weld
- Collision possibility
- Multiple robot configurations

### Scenario 4 — Fixture Movement

- Robot and fixture must coordinate

### Scenario 5 — Deviation

- Actual path differs from planned path

### Scenario 6 — Failure

- Sensor/agent unavailable

All teams should eventually support the same scenarios.

---

# 25. REPOSITORY STRUCTURE

```text
ventek_autonomous_welding/
│
├── README.md
├── LICENSE
├── .gitignore
├── .gitattributes
├── .env.example
│
├── .github/
│   ├── workflows/
│   │   ├── ci.yml
│   │   └── ros_build.yml
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   ├── feature_request.md
│   │   └── research_task.md
│   ├── pull_request_template.md
│   └── CODEOWNERS
│
├── config/
│   ├── camera_config.yaml
│   ├── robot_config.yaml
│   ├── welding_params.yaml
│   ├── safety_limits.yaml
│   ├── system_config.yaml
│   └── ros2_topics.yaml
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── mock/
│   ├── samples/
│   └── logs/
│
├── docs/
│   ├── architecture/
│   ├── interfaces/
│   ├── teams/
│   ├── research/
│   └── meetings/
│
├── src/
│   ├── team1_autonomy/
│   ├── team2_orchestration/
│   ├── team3_multimodal/
│   ├── team4_adaptive/
│   ├── team5_vision/
│   └── team6_planning/
│
├── integration/
│   ├── launch/
│   ├── scenarios/
│   ├── configs/
│   └── tests/
│
├── simulation/
│   ├── robot/
│   ├── fixtures/
│   ├── worlds/
│   └── scenarios/
│
├── models/
│   ├── vision/
│   ├── multimodal/
│   ├── reinforcement_learning/
│   └── checkpoints/
│
├── urdf/
│   ├── robot/
│   ├── fixtures/
│   └── welding_cell/
│
├── launch/
├── scripts/
├── tests/
└── docker/
```

---

# 26. CODE ORGANIZATION RULES

## Team ownership

```text
src/team1_autonomy/       → T1
src/team2_orchestration/  → T2
src/team3_multimodal/     → T3
src/team4_adaptive/       → T4
src/team5_vision/         → T5
src/team6_planning/       → T6
```

## Tests

```text
tests/team1/
tests/team2/
tests/team3/
tests/team4/
tests/team5/
tests/team6/
tests/integration/
```

## Shared code

If code is genuinely shared by multiple teams, do not copy-paste it.

Discuss whether it belongs in a common utility/module.

---

# 27. ROS 2 ORGANIZATION

ROS 2 packages should be created according to functional modules rather than arbitrary scripts.

For example:

```text
team5_camera
team5_scene_perception
team5_weld_detection

team6_ik
team6_motion_planning
team6_collision

team2_robot_interface
team2_fixture_control
team2_cell_orchestrator
```

Each package should have:

- `package.xml`
- `CMakeLists.txt` or Python package configuration
- `launch/` if needed
- `config/` if needed
- `src/`
- `test/`

Do not create one giant ROS package containing the entire project.

---

# 28. GIT WORKFLOW

## Never push directly to `main`

Use:

```text
Issue
 ↓
Feature Branch
 ↓
Implementation
 ↓
Testing
 ↓
Pull Request
 ↓
Review
 ↓
CI
 ↓
Merge
```

## Branch naming

Examples:

```text
team5/pointcloud-pipeline
team5/weld-joint-detection
team6/ik-solver
team6/collision-checking
team2/fixture-controller
team3/sensor-sync
```

## Commit naming

Prefer:

```text
feat: add weld joint detector
fix: correct camera frame transform
test: add scene schema validation
docs: update trajectory contract
refactor: split point cloud pipeline
```

---

# 29. GITHUB ISSUES

Every meaningful development task should become an Issue.

## Good Issue

```text
[T5] Implement point-cloud filtering

Goal:
Remove depth noise from OAK-D point cloud.

Input:
Raw RGB-D frame.

Output:
Filtered point cloud.

Acceptance Criteria:
- Removes invalid points
- Reduces noise
- Preserves object boundaries
- Saves sample output
- Unit test included
```

## Bad Issue

```text
Work on point cloud.
```

---

# 30. PULL REQUEST REQUIREMENTS

Every PR should explain:

```text
What changed?
Why?
Which team?
Related issue?
Input interface?
Output interface?
Testing performed?
Evidence?
Dependencies?
Breaking changes?
```

A PR is not complete just because the code runs locally.

---

# 31. DEFINITION OF DONE

A task is **DONE** only when:

- Code is implemented
- Relevant tests exist
- Interface is respected
- Documentation is updated
- Result has evidence
- PR is reviewed
- CI passes
- PR is merged

For research tasks:

- Experiment is reproducible
- Baseline exists where appropriate
- Metric is defined
- Result is recorded
- Failure cases are documented

---

# 32. TEAM DEVELOPMENT STRATEGY

Every team should follow:

```text
UNDERSTAND
    ↓
DEFINE INPUT
    ↓
DEFINE OUTPUT
    ↓
CREATE MOCK INPUT
    ↓
BUILD BASELINE
    ↓
TEST
    ↓
INTEGRATE
    ↓
IMPROVE
```

Do not start with the most complicated algorithm.

---

# 33. BASELINE-FIRST RULE

For every advanced research method, first create a baseline.

Examples:

### T1

Rule-based planner → RL

### T3

Statistical anomaly detection → ML → multimodal model

### T4

PID / bounded correction → MPC → advanced adaptive control

### T5

Geometric segmentation → learned segmentation

### T6

Standard IK/planner → constrained optimization

This gives the project measurable progress.

---

# 34. SIMULATION-FIRST RULE

Before real robot execution:

```text
Algorithm
   ↓
Unit Test
   ↓
Mock Data
   ↓
Simulation
   ↓
Dry Run
   ↓
Low-Speed Real Robot
   ↓
Controlled Welding
```

Do not directly test experimental AI on the physical robot.

---

# 35. SAFETY

This project involves a physical robotic welding system.

Safety constraints must not depend exclusively on an AI model.

Maintain independent checks for:

- Joint limits
- Workspace limits
- Collision
- Velocity
- Acceleration
- Emergency stop
- Safe home position
- Fixture state
- Clamp state
- Welding state
- Recovery state

AI can recommend an action.

The safety layer must be able to reject it.

---

# 36. DATA MANAGEMENT

Do not commit large files directly to Git unless deliberately versioned.

Avoid ordinary Git commits for:

```text
*.bag
*.db3
*.pcd
*.ply
*.las
large videos
large datasets
large model checkpoints
```

Git should primarily contain:

- Source code
- Configuration
- Schemas
- Documentation
- Tests
- Small samples
- Reproducible experiment definitions

---

# 37. MILESTONES

## M0 — Foundation

Deliver:

- Repository
- Team structure
- Interfaces
- Mock data
- Coordinate conventions
- Robot selection
- Camera selection
- GitHub workflow

---

## M1 — Perception

Primary:

**T5**

Deliver:

- Camera pipeline
- Calibration
- RGB-D
- Point cloud
- Scene segmentation
- Weld detection

---

## M2 — Planning

Primary:

**T6**

Deliver:

- Weld path
- Torch poses
- IK
- Reachability
- Collision checking
- Trajectory

---

## M3 — Simulation

Primary:

**T1 + T2 + T6**

Deliver:

- Robot simulation
- Fixture simulation
- Cell simulation
- Digital twin baseline
- Mock execution

---

## M4 — Integration

Target:

```text
Camera
 ↓
Scene
 ↓
Weld
 ↓
IK
 ↓
Trajectory
 ↓
Robot Simulation
```

---

## M5 — Adaptive

Primary:

**T3 + T4 + T6**

Deliver:

- Feedback
- Path deviation
- Correction
- Quality prediction
- Replanning

---

## M6 — Autonomous

Primary:

**T1 + All**

Deliver:

- Cognitive decision-making
- Multi-agent coordination
- Adaptive planning
- Digital twin
- Edge inference
- Autonomous process flow

---

# 38. PROJECT SUCCESS CRITERIA

The project should not be judged only by individual model accuracy.

A successful integrated prototype should demonstrate:

```text
REAL SETUP
   ↓
PERCEPTION
   ↓
STRUCTURED SCENE
   ↓
WELD GEOMETRY
   ↓
ROBOT PLAN
   ↓
VALIDATED TRAJECTORY
   ↓
SIMULATION
   ↓
EXECUTION
   ↓
FEEDBACK
   ↓
CORRECTION
```

The advanced target adds:

```text
             COGNITIVE DECISION
                    ↓
PERCEIVE → PLAN → EXECUTE → OBSERVE → ADAPT
              ↑                    │
              └────────────────────┘
```

---

# 39. PROJECT MANAGEMENT

## Weekly Meeting

Recommended 60 minutes:

### 0–5 min

Project-level status.

### 5–35 min

Six team reviews.

Each team answers:

1. What was planned?
2. What was completed?
3. Show evidence.
4. What failed?
5. What is blocked?
6. What is next?

### 35–45 min

Integration review.

### 45–55 min

Task assignment.

### 55–60 min

Decisions and deadlines.

---

# 40. TASK ASSIGNMENT TEMPLATE

Every assigned task should contain:

```text
Task:
Team:
Owner:
Priority:
Deadline:

Objective:

Input:

Expected Output:

Dependencies:

Acceptance Criteria:

Testing:

Evidence Required:

GitHub Issue:
```

Example:

```text
Task:
Implement weld-joint geometry extraction

Team:
T5

Owner:
Member X

Input:
Segmented weld region

Output:
Start/end/normal/length

Acceptance:
- Coordinates in world frame
- Length within defined tolerance
- Confidence included
- scene.json generated
```

---

# 41. MEETING QUESTIONS BY TEAM

## T1

- What decision can your system make?
- What information does it need?
- What actions can it trigger?
- What is the baseline?
- What makes the decision autonomous?

## T2

- What agents exist?
- How do they communicate?
- What is the safety state?
- Can robot and fixture coordinate?
- What happens during failure?

## T3

- What data is available?
- Is it synchronized?
- What is the ground truth?
- What is the baseline model?
- What prediction are we making?

## T4

- What deviation are we correcting?
- How is it measured?
- What correction is generated?
- What prevents instability?
- When do we re-plan?

## T5

- What does the camera see?
- Is depth reliable?
- What is the coordinate frame?
- Can you detect the joint?
- Can Team 6 directly consume your output?

## T6

- Is the weld reachable?
- Is the torch orientation feasible?
- Is the trajectory collision-free?
- Are singularities handled?
- Can the trajectory be executed?

---

# 42. INTEGRATION CHECKLIST

Before declaring a module integrated:

- [ ] Input schema validated
- [ ] Output schema validated
- [ ] Coordinate frames verified
- [ ] Units verified
- [ ] Mock scenario tested
- [ ] Error handling implemented
- [ ] Logs available
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Another team has successfully consumed the output

---

# 43. GOLDEN RULES FOR ALL MEMBERS

### Rule 1

**Do not work in isolation.**

### Rule 2

**Read the README before asking for architecture clarification.**

### Rule 3

**Check `docs/interfaces/` before consuming another team's output.**

### Rule 4

**Use mock data if the real module is unavailable.**

### Rule 5

**Never silently change an interface.**

### Rule 6

**Every significant change goes through GitHub.**

### Rule 7

**Show evidence, not just status.**

### Rule 8

**Document failures.**

Failure data is valuable research data.

### Rule 9

**Baseline first, advanced method second.**

### Rule 10

**Simulation before physical testing.**

---

# 44. WHERE TO LOOK WHEN YOU HAVE A QUESTION

| Question | Location |
|---|---|
| Overall project | `README.md` |
| Architecture | `docs/architecture/` |
| Data contracts | `docs/interfaces/` |
| Team responsibility | `docs/teams/` |
| Research | `docs/research/` |
| Configuration | `config/` |
| Mock inputs | `data/mock/` |
| Code | `src/` |
| Integration | `integration/` |
| Simulation | `simulation/` |
| Robot description | `urdf/` |
| Tests | `tests/` |
| Deployment | `docker/` |
| Issues/tasks | GitHub Issues |
| Code review | GitHub Pull Requests |
| Project planning | GitHub Projects |

---

# 45. WHEN TO ASK THE PROJECT LEAD

Do **not** ask the project lead for information that is already documented here.

Ask the project lead when:

- Architecture needs to change
- Team responsibilities overlap
- A contract needs to change
- A hardware decision affects multiple teams
- A major dependency is blocked
- A safety-critical decision is required
- A research direction needs to change
- Industry requirements have changed
- Two teams disagree on ownership

Before asking:

1. Check `README.md`
2. Check `docs/architecture/`
3. Check `docs/interfaces/`
4. Check your team documentation
5. Check GitHub Issues
6. Check recent meeting decisions

Then ask a precise question.

Bad:

> What should I do?

Good:

> Team 5 currently outputs weld normals in the camera frame, while Team 6 expects world-frame normals. Should we transform inside Team 5 or define the contract so Team 6 performs the transformation?

---

# 46. RESEARCH STANDARD

A research contribution should follow:

```text
Problem
 ↓
Existing Method
 ↓
Limitation
 ↓
Proposed Improvement
 ↓
Experiment
 ↓
Baseline
 ↓
Metrics
 ↓
Results
 ↓
Failure Analysis
 ↓
Conclusion
```

For every proposed AI method ask:

- Why is AI necessary?
- What is the baseline?
- What measurable improvement is expected?
- What data is required?
- Can it run in real time?
- Can it run on target hardware?
- How does it integrate with the physical system?

Do not add AI simply because the project is called AI.

---

# 47. EXPERIMENT TEMPLATE

Every major experiment should record:

```text
Experiment ID:

Team:

Date:

Research Question:

Hypothesis:

Dataset:

Hardware:

Software:

Algorithm:

Parameters:

Baseline:

Proposed Method:

Metrics:

Expected Result:

Actual Result:

Failure Cases:

Observations:

Next Experiment:

Code / PR:

Evidence:
```

---

# 48. RISK MANAGEMENT

Important project risks include:

| Risk | Main Owner | Mitigation |
|---|---|---|
| Reflective metal breaks depth | T5 | Sensor testing + filtering |
| Weld joint detection unreliable | T5 | RGB + geometry + learned methods |
| IK failure | T6 | Multiple configurations/solvers |
| Collision false negatives | T6/T2 | Conservative margins |
| Fixture coordination failure | T2 | Simulation first |
| Lack of process data | T3 | Start data collection early |
| Adaptive instability | T4 | Bounded corrections |
| Unsafe AI policy | T1 | Independent safety layer |
| Hardware unavailable | All | Simulation/mock data |
| Integration delay | Project Lead | Frozen interfaces |
| Research over-complexity | All | Baseline-first approach |

---

# 49. OPEN QUESTIONS

The following should be continuously updated in project tracking:

- Which exact robot model will be used?
- What is the final welding gun/TCP geometry?
- What is the final camera mounting position?
- What PLC/protocol is available?
- What process sensors are available?
- What welding data can be collected?
- What constitutes acceptable weld quality?
- Which simulator will be primary?
- What exact welding processes must the prototype support?
- What materials must be considered?
- Which constraints must be hard-coded?
- Which decisions are allowed to be autonomous?

Do not make undocumented assumptions about unresolved questions.

---

# 50. CURRENT PROJECT PRIORITIES

At the foundation stage, prioritize:

### Priority 0

- Freeze architecture
- Freeze team responsibilities
- Freeze interfaces
- Create mock data
- Select robot representation
- Establish camera pipeline

### Priority 1

- Team 5 perception baseline
- Team 6 planning baseline
- Team 2 orchestration baseline

### Priority 2

- Team 3 data pipeline
- Team 4 basic correction
- Team 1 rule-based autonomy

### Priority 3

- Advanced ML
- RL
- MPC
- Digital twin synchronization
- Advanced multimodal intelligence

---

# 51. THE MOST IMPORTANT INTERACTION BETWEEN TEAMS

The first meaningful integrated chain should be:

```text
T5
Computer Vision
    │
    │ scene.json
    ▼
T6
Path Planning
    │
    │ trajectory.json
    ▼
T2
Orchestration
    │
    │ cell_state.json
    ▼
T3
Multimodal Understanding
    │
    │ process feedback
    ▼
T4
Adaptive Control
    │
    │ correction.json
    ▼
T6
Replanning
```

Then add T1:

```text
                    T1
             COGNITIVE AUTONOMY
                    │
        ┌───────────┼────────────┐
        ▼           ▼            ▼
       T2          T4           T6
```

---

# 52. FINAL MENTAL MODEL

If you forget everything else, remember these six questions:

```text
T5 — WHAT IS THERE?
     ↓
     Understand the physical scene.

T6 — CAN THE ROBOT DO IT?
     ↓
     Convert geometry into feasible motion.

T2 — HOW DO THE MACHINES WORK TOGETHER?
     ↓
     Coordinate the cell.

T3 — WHAT IS HAPPENING?
     ↓
     Understand sensor/process data.

T4 — HOW SHOULD WE RESPOND?
     ↓
     Correct deviations and adapt.

T1 — WHAT SHOULD WE DO NEXT?
     ↓
     Make high-level autonomous decisions.
```

Together:

```text
              PERCEIVE
                  ↓
             UNDERSTAND
                  ↓
                PLAN
                  ↓
             COORDINATE
                  ↓
              EXECUTE
                  ↓
              OBSERVE
                  ↓
               ADAPT
                  ↓
               DECIDE
                  ↓
                PLAN
                  ↺
```

---

# 53. FINAL PRINCIPLE

> **The objective is not to build six impressive modules.**
>
> **The objective is to build one robotic welding system whose modules work together.**

Every team should therefore optimize for:

**Correctness → Integration → Reliability → Measurable Improvement → Advanced Intelligence**

—not for algorithm complexity alone.

---

## Project Owner

**Utkarsh Ghom**

## Project

**VENTEK Autonomous Welding**

## Repository

`ventek-autonomous-welding`

## Status

**Living Technical Reference**

> Update this README when project-level architecture, contracts, responsibilities, or development methodology changes.
