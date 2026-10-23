# VENTEK Autonomous Robotic Welding System

[![ROS 2 Humble](https://img.shields.io/badge/ROS_2-Humble-3498DB.svg)](https://docs.ros.org/en/humble/)
[![Gazebo Harmonic](https://img.shields.io/badge/Gazebo-Harmonic_8-FF6F00.svg)](https://gazebosim.org/docs/harmonic/)
[![Python 3.10](https://img.shields.io/badge/Python-3.10-3776AB.svg)](https://www.python.org/)
[![Tests Passing](https://img.shields.io/badge/Tests-46_Passed-brightgreen.svg)]()
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

> **Autonomous Vision-Based Robotic Welding Program Generation & Real-Time Adaptive Execution**  
> Complete Vertical Slice: Known Workcell → Candidate Seam Geometry → Feasible Trajectory → Simulated Execution → Process Telemetry → Bounded Adaptation / Safe Pause → Supervisory Decisions.

---

## Table of Contents
1. [Newcomer's Onboarding & Project Map](#1-newcomers-onboarding--project-map)
2. [Simulation Architecture & Guide](#2-simulation-architecture--guide)
3. [Subsystem Division of Responsibilities](#3-subsystem-division-of-responsibilities)
4. [Where Each Team Updates Logic & Tests (`tests/`)](#4-where-each-team-updates-logic--tests-tests)
5. [Quick Start Runbook](#5-quick-start-runbook)
6. [Shared JSON Contracts (v0.1 Frozen)](#6-shared-json-contracts-v01-frozen)
7. [The 10 Minimum Integration Scenarios](#7-the-10-minimum-integration-scenarios)
8. [Complete Directory Index](#8-complete-directory-index)
9. [Architecture & Reference Documents](#9-architecture--reference-documents)

---

## 1. Newcomer's Onboarding & Project Map

Welcome to the **VENTEK Autonomous Robotic Welding** monorepo! This system automates the transition from raw CAD/point-cloud scene data to optimized, collision-free robot welding execution with live deviation tracking and safety interlocks.

### What is where?
```text
ventek_autonomous_welding/
├── docs/                 <-- All documentation, specifications, and simulation guides
│   ├── SIMULATION_GUIDE.md  <-- Gazebo Sim Harmonic, 28 frames, topics, sensor specs
│   ├── architecture/        <-- Contracts, frames, data dictionary, system flow
│   └── teams/               <-- Onboarding guides for Teams 1 through 6
├── src/                  <-- Core production algorithms and modules for Teams 1 to 6
├── tests/                <-- Subsystem testbenches where EACH TEAM updates their logic
│   ├── team1/ ... team6/    <-- Individual team logic & test files
├── integration/          <-- Frozen JSON schemas (v0.1), positive/negative examples, E2E tests
├── simulation/           <-- 3D models (visual/collision meshes), SDF worlds, scenarios
├── urdf/                 <-- KUKA KR 6 R900 robot arm and welding cell Xacro kinematic model
├── config/               <-- Robot limits, camera calibration, topics, safety YAML configs
├── scripts/              <-- Verification, depth feed viewing, and pipeline runner CLI
└── launch/               <-- ROS 2 launch files for simulation, planning, and full cell
```

---

## 2. Simulation Architecture & Guide

The primary technical reference for the robotic welding cell simulation is:
👉 **[`docs/SIMULATION_GUIDE.md`](docs/SIMULATION_GUIDE.md)** *(Comprehensive Guide: Gazebo Sim Harmonic, 28 coordinate frames, OAK-D Lite depth cameras, PBR shading, joint sliders, and topic catalog)*

### Key Simulation Highlights
- **Simulator**: Gazebo Sim Harmonic (`gz-sim 8`) bridged via `ros_gz_bridge` to ROS 2 Humble.
- **Robot Arm**: Industrial **KUKA KR 6 R900 sixx** (6-DOF, 901 mm reach, 6 kg payload) with closed-loop PID joint position controllers.
- **3D Cell**: Modular welding table, anodized workpiece fixture, toggle clamps, welding power source, KRC4 controller, and MIG welding torch.
- **Vision Sensor**: Arm-mounted Luxonis OAK-D Lite depth camera generating 30 Hz RGB (`/camera/image_raw`), 32-bit floating-point metric depth (`/camera/depth`), and dense 3D point clouds (`/camera/points`).
- **Interactive Tools**: 6-DOF joint slider GUI (`joint_state_publisher_gui`) and real-time OpenCV depth probe viewer (`view_depth_feed`).

---

## 3. Subsystem Division of Responsibilities

The software architecture is partitioned into 6 specialized teams. Each team has an explicit contract and ownership:

| Subsystem | Team Directory | Primary Role & Responsibility | Output Contract | Team Guide |
|---|---|---|---|---|
| **Supervisor** | `src/team1_autonomy/` | Deterministic state machine, sequencing rules, command ID generation, safety gates. | `decision.json` | [`docs/teams/team1_autonomy.md`](docs/teams/team1_autonomy.md) |
| **Orchestration** | `src/team2_orchestration/` | Workcell execution, robot/fixture/clamp coordination, command acknowledgement (`cmd_XXXX`). | `cell_state.json` | [`docs/teams/team2_orchestration.md`](docs/teams/team2_orchestration.md) |
| **Analytics** | `src/team3_multimodal/` | Data quality & freshness, windowed features, statistical baseline anomaly detection. | `process_feedback.json` | [`docs/teams/team3_multimodal.md`](docs/teams/team3_multimodal.md) |
| **Adaptation** | `src/team4_adaptive/` | Seam deviation tracking, deadband filtering, revision-tied absolute offsets. | `correction.json` | [`docs/teams/team4_adaptive.md`](docs/teams/team4_adaptive.md) |
| **Perception** | `src/team5_vision/` | 3D scene point clouds, calibration verification, candidate seam extraction (Candidate $\neq$ intent). | `scene.json` | [`docs/teams/team5_vision.md`](docs/teams/team5_vision.md) |
| **Planning** | `src/team6_planning/` | Approach/weld/retreat poses, reachability (IK), joint limits, collision checks, Team 4 revalidation. | `trajectory.json` | [`docs/teams/team6_planning.md`](docs/teams/team6_planning.md) |

---

## 4. Where Each Team Updates Logic & Tests (`tests/`)

Every team works directly in their designated testbench file within the [`tests/`](tests/) directory. In this workflow, teams iterate, update, and validate their algorithms against the frozen JSON contracts:

| Team | Update Logic & Tests Here | Corresponding Subsystem Package | Key Test Topics |
|---|---|---|---|
| **Team 1** | [`tests/team1/test_team1_autonomy.py`](tests/team1/test_team1_autonomy.py) | `src/team1_autonomy/` | State machine transitions, seam priority rules, decision IDs, safety interlock gates |
| **Team 2** | [`tests/team2/test_team2_orchestration.py`](tests/team2/test_team2_orchestration.py) | `src/team2_orchestration/` | Robot motion lifecycle (`accepted`→`in_progress`→`completed`), clamp actuation, E-stops |
| **Team 3** | [`tests/team3/test_team3_multimodal.py`](tests/team3/test_team3_multimodal.py) | `src/team3_multimodal/` | Telemetry freshness, data-quality checks, rule-based anomaly detection, unlabelled nulls |
| **Team 4** | [`tests/team4/test_team4_adaptive.py`](tests/team4/test_team4_adaptive.py) | `src/team4_adaptive/` | Seam deviation filtering, deadband limits (0.05 mm), revision-tied absolute offsets, replan |
| **Team 5** | [`tests/team5/test_team5_vision.py`](tests/team5/test_team5_vision.py) | `src/team5_vision/` | Sensor calibration verification, candidate seam endpoints, geometry extraction |
| **Team 6** | [`tests/team6/test_team6_planning.py`](tests/team6/test_team6_planning.py) | `src/team6_planning/` | Cartesian waypoints (Approach/Weld/Retreat), IK reachability, clamp collision, revalidation |

👉 Full guidelines: **[`tests/README.md`](tests/README.md)**

---

## 5. Quick Start Runbook

### Step 1: Build the Workspace
```bash
# Source ROS 2 Humble
source /opt/ros/humble/setup.bash

# Navigate to workspace and build
cd /home/utkarsh/ventek_ws
colcon build --symlink-install
source install/setup.bash
```

### Step 2: Verify Cell Setup & Kinematics
Run the automated pre-flight sanity suite (checks 3D meshes, 28 TF frames, TCP offset, reachability, and scenarios):
```bash
python3 scripts/verify_cell_setup.py
# Or via ROS 2 CLI
ros2 run ventek_autonomous_welding verify_cell_setup
```

### Step 3: Run the Full Test Suite (46 Tests)
Validate all team logic and integration scenarios:
```bash
# Run pytest directly
python3 -m pytest tests/ integration/tests/

# Or run tests for your individual team
python3 -m pytest tests/team1/
python3 -m pytest tests/team6/

# Or via colcon test
colcon test --packages-select ventek_autonomous_welding
colcon test-result --all
```

### Step 4: Run the Baseline End-to-End Slice Demo
Runs the live pipeline with mock simulation (Perception → Planning → Execution → Telemetry → Adaptation → Supervisor):
```bash
python3 scripts/run_integration_pipeline.py
# Or via ROS 2 CLI
ros2 run ventek_autonomous_welding run_pipeline
```

### Step 5: Launch the 3D Gazebo Simulation & RViz
Launch Gazebo Sim Harmonic, RViz 2, the KUKA robot arm model, and the joint slider GUI:
```bash
ros2 launch ventek_autonomous_welding simulation.launch.py
```

Optional depth viewer in a new terminal:
```bash
ros2 run ventek_autonomous_welding view_depth_feed
```

---

## 6. Shared JSON Contracts (v0.1 Frozen)

All data exchanged between subsystems conforms strictly to Draft-07 JSON Schemas:

- **JSON Schemas**: [`integration/schemas/`](integration/schemas/) (mirrored in [`docs/interfaces/`](docs/interfaces/))
  - `scene.schema.json`
  - `trajectory.schema.json`
  - `cell_state.schema.json`
  - `process_feedback.schema.json`
  - `correction.schema.json`
  - `decision.schema.json`
- **Canonical Examples**: [`integration/examples/`](integration/examples/)
  - Positive examples: `scene_ok.json`, `trajectory_ok.json`, `cell_state_ready.json`, `correction_small.json`, `decision_execute.json`
  - Negative/fault examples: `scene_invalid.json`, `trajectory_unreachable.json`, `cell_state_fault.json`, `correction_replan.json`, `decision_pause.json`
  - Policy examples: `process_feedback_unavailable.json`

### Contract Invariants
1. `schema_version`: Fixed to `"0.1"`.
2. `timestamp`: ISO-8601 UTC with milliseconds (e.g. `"2026-10-25T10:00:00.000Z"`).
3. `frame_id`: Explicit frame tag (`assembly_world`, `robot_base`).
4. `Validation Enum`: `PASS`, `FAIL`, `NOT_RUN`, `NOT_AVAILABLE`.
5. `Unvalidated Predictions`: Kept `null` with status `NOT_AVAILABLE` until physical inspection labels exist.

---

## 7. The 10 Minimum Integration Scenarios

The integration test suite ([`integration/tests/test_end_to_end_mock.py`](integration/tests/test_end_to_end_mock.py)) implements and validates the 10 minimum integration scenarios specified in Section 9 of the Consolidated Architecture Baseline:

1. **Scenario 1 (Nominal Happy Path)**: Valid scene → reachable seam → collision-free trajectory → simulated execution → command completed → Supervisor `COMPLETE`.
2. **Scenario 2 (No Candidate Seam)**: Empty candidate joints list halts progression; requests rescan or operator selection.
3. **Scenario 3 (Unverified Calibration)**: `calibration_status != "VERIFIED"` blocks planning progression.
4. **Scenario 4 (Unreachable Seam)**: Target beyond 0.901 m reach yields explicit IK `FAIL`, `status: "FAILED_VALIDATION"`, and no executable motion.
5. **Scenario 5 (Clamp Obstruction)**: Clamp interference envelope yields `collision: "FAIL"` and `next_action: "REJECTED"`.
6. **Scenario 6 (Stale Telemetry)**: Telemetry older than threshold flags `data_quality: "STALE"` and triggers supervisory alert.
7. **Scenario 7 (Large Seam Deviation)**: Measured deviation >1.0 mm causes Team 4 to request replan; Supervisor safely initiates `PAUSED`.
8. **Scenario 8 (Command ID Mismatch)**: Unmatched `decision_id` in acknowledgement prevents state advance.
9. **Scenario 9 (Emergency Stop / Safety Interlock)**: Tripped safety circuit immediately halts motion; AI cannot override.
10. **Scenario 10 (Schema Mismatch)**: Malformed payload fails validation, logs reason, and aborts progression.

---

## 8. Complete Directory Index

```text
ventek_autonomous_welding/
├── config/                  # Subsystem YAML configurations
│   ├── camera_config.yaml   # Camera resolution, intrinsics & extrinsics
│   ├── robot_config.yaml    # KUKA KR 6 R900 DH parameters & joint limits
│   ├── ros2_topics.yaml     # Topic naming contracts
│   ├── safety_limits.yaml   # Velocity, acceleration, and deviation thresholds
│   ├── system_config.yaml   # Master system parameters
│   └── welding_params.yaml  # Welding process recipes (voltage, wire feed)
├── data/
│   └── mock/                # Canonical mock JSON files (v0.1)
├── docs/
│   ├── SIMULATION_GUIDE.md  # Detailed Gazebo Sim Harmonic, 28 frames, topics guide
│   ├── VENTEK_Consolidated_Architecture_Baseline_and_JSON_Contracts.md
│   ├── VENTEK_Final_Product_Approach_Review_Teams_1_3_4_5_6.md
│   ├── architecture/        # Contract, TF tree, data dictionary, system flow
│   ├── interfaces/          # Mirrored canonical JSON Schemas
│   └── teams/               # Team onboarding guides (Teams 1 through 6)
├── integration/
│   ├── examples/            # Canonical positive and negative mock payloads
│   ├── pipeline.py          # Unified end-to-end vertical slice orchestrator
│   ├── schemas/             # Frozen JSON Schema definitions (Draft-07)
│   └── tests/               # Schema validation & minimum scenario tests
├── launch/                  # ROS 2 simulation, planning, and system launch files
├── scripts/
│   ├── run_integration_pipeline.py  # CLI runner for vertical slice demo
│   ├── verify_cell_setup.py         # Cell asset and kinematic integrity checks
│   └── view_depth_feed.py           # Real-time OpenCV depth stream viewer
├── simulation/              # 3D visual & collision meshes, SDF worlds, scenarios
├── src/                     # Subsystem source code
│   ├── team1_autonomy/      # Supervisor state machine
│   ├── team2_orchestration/ # Cell execution and telemetry
│   ├── team3_multimodal/    # Process analytics & data quality
│   ├── team4_adaptive/      # Seam deviation & bounded corrections
│   ├── team5_vision/        # Point cloud perception & candidate seams
│   └── team6_planning/      # Path planning & validation
├── tests/                   # Workspaces where EACH TEAM updates their logic
│   ├── team1/ ... team6/    # Subsystem test and logic files
│   ├── conftest.py          # Shared fixtures
│   └── README.md            # Testing guide
└── urdf/                    # Cell Xacro & URDF kinematic model (KUKA KR 6 R900)
```

---

## 9. Architecture & Reference Documents

- **[`docs/SIMULATION_GUIDE.md`](docs/SIMULATION_GUIDE.md)** — Gazebo Sim Harmonic, 28 coordinate frames, joint control sliders, depth viewer, PBR lighting, and topic catalog.
- **[`docs/VENTEK_Consolidated_Architecture_Baseline_and_JSON_Contracts.md`](docs/VENTEK_Consolidated_Architecture_Baseline_and_JSON_Contracts.md)** — Architectural foundation, JSON contracts, and baseline vertical slice plan.
- **[`docs/VENTEK_Final_Product_Approach_Review_Teams_1_3_4_5_6.md`](docs/VENTEK_Final_Product_Approach_Review_Teams_1_3_4_5_6.md)** — Product perspective review, subsystem criteria, and algorithm upgrade gates.
- **[`docs/architecture/system_contract.md`](docs/architecture/system_contract.md)** — Shared contract rules and interface freeze.
- **[`docs/architecture/coordinate_frames.md`](docs/architecture/coordinate_frames.md)** — 28 coordinate frames and verified transform chains.
- **[`docs/architecture/system_architecture.md`](docs/architecture/system_architecture.md)** — High-level architecture, data flow, and error recovery.
- **[`docs/architecture/data_dictionary.md`](docs/architecture/data_dictionary.md)** — Comprehensive attribute, unit, and enum dictionary.

---

## 10. License

Proprietary — Ventek Automation
