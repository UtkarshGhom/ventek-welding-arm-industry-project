# VENTEK Autonomous Robotic Welding Industry Project

[![ROS 2 Humble](https://img.shields.io/badge/ROS_2-Humble-3498DB.svg)](https://docs.ros.org/en/humble/)
[![Gazebo Harmonic](https://img.shields.io/badge/Gazebo-Harmonic_8-FF6F00.svg)](https://gazebosim.org/docs/harmonic/)
[![Python 3.10](https://img.shields.io/badge/Python-3.10-3776AB.svg)](https://www.python.org/)
[![Tests Passing](https://img.shields.io/badge/Tests-46_Passed-brightgreen.svg)]()
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](ventek_autonomous_welding/LICENSE)

> **Industrial Vision-Based Robotic Welding Monorepo**  
> Dual-Workcell Architecture: **Continuous Arc Seam Welding** (KUKA KR 6 R900) & **Heavy Resistance Spot Welding** (FANUC R-2000iA/165F).  
> From Scanning Workpieces to Validating Trajectories, Simulating Execution, Monitoring Real-Time Telemetry, and Bounded Adaptive Correction.

---

## Table of Contents
1. [Executive Summary & The Two Welding Systems](#1-executive-summary--the-two-welding-systems)
2. [Newcomer's Orientation & Monorepo Map](#2-newcomers-orientation--monorepo-map)
3. [Arm 1: Continuous Arc Seam Welding (`ventek_autonomous_welding`)](#3-arm-1-continuous-arc-seam-welding-ventek_autonomous_welding)
4. [Arm 2: Heavy Resistance Spot Welding Cell (`ventek_cell_description`)](#4-arm-2-heavy-resistance-spot-welding-cell-ventek_cell_description)
5. [Simulation Guides & Visual Tooling](#5-simulation-guides--visual-tooling)
6. [Where Each Team Updates Logic & Tests (`tests/`)](#6-where-each-team-updates-logic--tests-tests)
7. [Shared JSON Contracts (v0.1 Frozen)](#7-shared-json-contracts-v01-frozen)
8. [The 10 Minimum Integration Scenarios](#8-the-10-minimum-integration-scenarios)
9. [Developer Quick Start Runbook](#9-developer-quick-start-runbook)
10. [Reference Specifications & Documentation Index](#10-reference-specifications--documentation-index)

---

## 1. Executive Summary & The Two Welding Systems

This repository contains the complete industrial robotic software, 3D simulation, kinematics, and perception stacks for VENTEK's automated welding operations. The project provides digital twins and software pipelines for **two distinct industrial robotic welding processes**:

| Feature / System | Continuous Arc Seam Welding | Heavy Resistance Spot Welding |
| :--- | :--- | :--- |
| **Package** | [`ventek_autonomous_welding/`](ventek_autonomous_welding/) | [`ventek_cell_description/`](ventek_cell_description/) |
| **Robotic Manipulator** | **KUKA KR 6 R900 sixx** (Agilus) | **FANUC R-2000iA/165F** |
| **Payload / Reach** | 6 kg / 0.901 m reach | 165 kg / 1.77 m scaled reach (2.65 m envelope) |
| **Welding Process** | Continuous Gas Metal Arc / MIG Seam Welding | Automotive Resistance Spot Welding |
| **End-Effector Tooling** | Angled GMAW torch with wire nozzle tip | Heavy Spot Welding C-Gun with dual copper electrodes |
| **Workpiece Station** | Stationary modular welding table with T-plates | Dual mobile fixture carts with sheet metal parts |
| **Safety Enclosure** | Perimeter safety wire fence | Full steel cell enclosure with actuated sliding service door |
| **Vision Camera** | Standoff/Eye-in-Hand Luxonis OAK-D Lite RGB-D | Eye-in-Hand **Intel RealSense D435** on robot `tool0` |
| **Controlled DOFs** | 6 joints (`joint_a1` – `joint_a6`) | 7 joints (`joint_1` – `joint_6`, `cell_door_joint`) |
| **Autonomous Pipeline** | Teams 1–6 (Autonomy, Orchestration, Multimodal, Adaptive, Vision, Planning) | High-fidelity digital twin, 50 Hz smoothed PID controllers, RealSense dashboard |

---

## 2. Newcomer's Orientation & Monorepo Map

If you are new to the project, here is how the workspace is structured and what each folder contains:

```text
ventek_project/
├── VENTEK_Consolidated_Architecture_Baseline_and_JSON_Contracts.md  <-- Master frozen JSON contracts & baseline rules
├── VENTEK_Final_Product_Approach_Review_Teams_1_3_4_5_6.md          <-- Product review, team roles & upgrade gates
├── README.md                                                        <-- This master guide
│
├── ventek_autonomous_welding/       <-- Continuous Arc Seam Welding Package (Teams 1–6)
│   ├── docs/
│   │   ├── SIMULATION_GUIDE.md      <-- Gazebo Sim Harmonic, 28 coordinate frames, topics
│   │   ├── architecture/            <-- Contracts, frames, data dictionary, architecture
│   │   ├── interfaces/              <-- Mirrored canonical v0.1 JSON Schemas
│   │   └── teams/                   <-- Team onboarding guides (Teams 1 through 6)
│   ├── src/                         <-- Core subsystem modules (Teams 1 to 6)
│   ├── tests/                       <-- WHERE EACH TEAM UPDATES LOGIC AND TESTS
│   │   ├── team1/ ... team6/        <-- Subsystem test & logic workbenches
│   │   ├── conftest.py              <-- Shared schema & example fixtures
│   │   └── README.md                <-- Testing runbook
│   ├── integration/
│   │   ├── schemas/                 <-- Frozen JSON Schema specifications (Draft-07)
│   │   ├── examples/                <-- Positive and negative canonical mock payloads
│   │   ├── pipeline.py              <-- End-to-end vertical slice orchestrator
│   │   └── tests/                   <-- 22 automated integration tests
│   ├── simulation/                  <-- Visual & collision meshes, SDF worlds, scenarios
│   ├── urdf/                        <-- KUKA KR 6 R900 robot arm & cell Xacro model
│   ├── config/                      <-- Robot limits, camera calibration, topics YAML
│   ├── scripts/                     <-- Verify setup, depth viewers, pipeline demo
│   └── launch/                      <-- ROS 2 simulation & full system launch files
│
├── ventek_cell_description/         <-- Heavy Resistance Spot Welding Package
│   ├── urdf/                        <-- FANUC R-2000iA, C-Gun, enclosure, fixture carts
│   ├── meshes/                      <-- High-precision STL meshes (robot, gun, carts, PLC)
│   ├── worlds/                      <-- Gazebo Sim 8 spot welding world SDF
│   ├── launch/                      <-- Full cell Gazebo, RViz, and camera dashboard launches
│   ├── config/                      <-- Joint controller gains & RViz setups
│   ├── scripts/                     <-- Live RealSense camera & depth visualizer
│   ├── README.md                    <-- Spot welding cell technical documentation
│   └── BUILD_LOG.md                 <-- Physical scaling, inertia & controller derivation
│
└── reference_models/                <-- CAD reference models, FreeCAD project & STEP files
```

---

## 3. Arm 1: Continuous Arc Seam Welding (`ventek_autonomous_welding`)

The `ventek_autonomous_welding` package hosts the complete 6-team autonomous welding stack. It replaces manual teach-and-program routines with an intelligent pipeline:

```text
Operator / Job Recipe
         |
         v
TEAM 1: Supervisor / State Machine (src/team1_autonomy/)
  | 
  |-- request_scan --> TEAM 5: Perception (src/team5_vision/)
  |                       | publishes scene.json (geometry + candidate seams)
  |
  |-- request_plan --> TEAM 6: Path Planning (src/team6_planning/)
  |                       | publishes trajectory.json (approach / weld / retreat)
  |
  |-- execute_weld --> TEAM 2: Cell Orchestration (src/team2_orchestration/)
  |                       | executes in Gazebo Sim & publishes cell_state.json
  |                       +---> TEAM 3: Multimodal Analytics (src/team3_multimodal/)
  |                       |        publishes process_feedback.json (advisories)
  |                       +---> TEAM 4: Adaptive Control (src/team4_adaptive/)
  |                                publishes correction.json (bounded offset)
  |
  v echoes command completion / fault
TEAM 1: Verifies acknowledgement -> transitions to COMPLETE
```

### Subsystem Division of Responsibilities
1. **Team 1 (Autonomy)**: Deterministic state machine (`SCANNING`, `PLANNING`, `VALIDATING`, `READY`, `EXECUTING`, `COMPLETE`, `PAUSED`, `REPLANNING`, `FAULT`), rule-based sequencing, command ID generation, and decision audit logs.
2. **Team 2 (Orchestration)**: Workcell execution, robot/fixture/clamp coordination, and command lifecycle acknowledgement (`cmd_XXXX` → `accepted` → `in_progress` → `completed`/`failed`).
3. **Team 3 (Multimodal)**: Sensor synchronization, telemetry freshness, data quality gates, and transparent statistical anomaly rules. Unvalidated quality predictions remain `null`/`NOT_AVAILABLE`.
4. **Team 4 (Adaptive)**: Seam deviation tracking, deadband filtering (0.05 mm), revision-tied absolute offsets (<= 1.0 mm), and replan/pause requests. Team 6 revalidates all corrections.
5. **Team 5 (Vision)**: 3D scene point clouds, calibration status (`VERIFIED`/`UNVERIFIED`), and candidate seam detection. Geometric edges are candidates, not proof of weld intent.
6. **Team 6 (Planning)**: Cartesian torch poses (`APPROACH`, `WELD`, `RETREAT`), IK reachability checks against KUKA KR 6 R900, joint limits, clamp collision checks, and Team 4 revalidation.

---

## 4. Arm 2: Heavy Resistance Spot Welding Cell (`ventek_cell_description`)

The `ventek_cell_description` package models a heavy automotive resistance spot welding workstation running in **Gazebo Sim 8 (Harmonic)** and **ROS 2 Humble**:

- **Robot**: **FANUC R-2000iA/165F** (6-DOF, 165 kg payload, scaled to 1.77 m reach).
- **End-Effector**: Heavy Spot Welding C-Gun (`spot_welding_gun`) with dual copper electrodes, high-current transformer, and pneumatic servo clamping cylinder.
- **Vision Camera**: Eye-in-Hand **Intel RealSense D435 RGB-D Camera** mounted on an offset carbon standoff bracket on robot `tool0`, aimed at 500 mm standoff directly at the fixture cart.
- **Enclosure & Fixtures**: Heavy steel safety enclosure with clear acrylic observation windows, an interactive actuated sliding service door (`cell_door_joint`, 0.0 to 0.90 m stroke), dual mobile fixture carts in machinery blue, and clamped automotive sheet metal parts.
- **Control**: Rittal PLC control cabinet, status stack light, and closed-loop joint position controllers with 50 Hz motion smoothing to prevent inertia bounce.

👉 Complete technical documentation: **[`ventek_cell_description/README.md`](ventek_cell_description/README.md)**  
👉 Mathematical derivation & controller tuning: **[`ventek_cell_description/BUILD_LOG.md`](ventek_cell_description/BUILD_LOG.md)**

---

## 5. Simulation Guides & Visual Tooling

The simulation guide is the central technical manual for running Gazebo Sim Harmonic and RViz:

👉 **[`ventek_autonomous_welding/docs/SIMULATION_GUIDE.md`](ventek_autonomous_welding/docs/SIMULATION_GUIDE.md)**  
*(Comprehensive Reference: Gazebo Sim Harmonic, 28 coordinate frames, OAK-D Lite depth camera, PBR shading, joint sliders, and topic catalog)*

### Launching the Spot Welding Cell (FANUC R-2000iA)
```bash
# Full Gazebo Sim 8 physics + RViz + joint sliders + pop-out RealSense camera dashboard:
ros2 launch ventek_cell_description gazebo_cell.launch.py

# Lightweight RViz model inspection (no physics, joint sliders enabled):
ros2 launch ventek_cell_description view_cell.launch.py

# Standalone OpenCV pop-out RealSense camera dashboard (with millimeter distance probe):
ros2 launch ventek_cell_description view_camera.launch.py

# RViz 3D RealSense PointCloud viewer:
ros2 launch ventek_cell_description view_vision.launch.py
```

### Launching the Continuous Arc Welding Cell (KUKA KR 6 R900)
```bash
# Full Gazebo Sim Harmonic simulation with RViz and 6-DOF joint slider GUI:
ros2 launch ventek_autonomous_welding simulation.launch.py

# Standalone OpenCV depth inspector with live crosshair probe:
ros2 run ventek_autonomous_welding view_depth_feed

# Pre-flight environment sanity check (meshes, TF frames, kinematics):
python3 ventek_autonomous_welding/scripts/verify_cell_setup.py
```

---

## 6. Where Each Team Updates Logic & Tests (`tests/`)

Every team works directly in their designated testbench file within [`ventek_autonomous_welding/tests/`](ventek_autonomous_welding/tests/). Teams iterate on, update, and validate their algorithms against the frozen JSON contracts:

| Team | Update Logic & Tests Here | Corresponding Subsystem Package | Key Test Focus |
|---|---|---|---|
| **Team 1** | [`tests/team1/test_team1_autonomy.py`](ventek_autonomous_welding/tests/team1/test_team1_autonomy.py) | `src/team1_autonomy/` | State machine transitions, seam priority rules, decision IDs, safety interlock gates |
| **Team 2** | [`tests/team2/test_team2_orchestration.py`](ventek_autonomous_welding/tests/team2/test_team2_orchestration.py) | `src/team2_orchestration/` | Robot motion lifecycle (`accepted`→`in_progress`→`completed`), clamp actuation, E-stops |
| **Team 3** | [`tests/team3/test_team3_multimodal.py`](ventek_autonomous_welding/tests/team3/test_team3_multimodal.py) | `src/team3_multimodal/` | Telemetry freshness, data-quality checks, rule-based anomaly detection, unlabelled nulls |
| **Team 4** | [`tests/team4/test_team4_adaptive.py`](ventek_autonomous_welding/tests/team4/test_team4_adaptive.py) | `src/team4_adaptive/` | Seam deviation filtering, deadband limits (0.05 mm), revision-tied absolute offsets, replan |
| **Team 5** | [`tests/team5/test_team5_vision.py`](ventek_autonomous_welding/tests/team5/test_team5_vision.py) | `src/team5_vision/` | Sensor calibration verification, candidate seam endpoints, geometry extraction |
| **Team 6** | [`tests/team6/test_team6_planning.py`](ventek_autonomous_welding/tests/team6/test_team6_planning.py) | `src/team6_planning/` | Cartesian waypoints (Approach/Weld/Retreat), IK reachability, clamp collision, revalidation |

👉 Complete testing runbook: **[`ventek_autonomous_welding/tests/README.md`](ventek_autonomous_welding/tests/README.md)**

---

## 7. Shared JSON Contracts (v0.1 Frozen)

All data exchanged between subsystems conforms strictly to Draft-07 JSON Schemas:

- **JSON Schemas**: [`ventek_autonomous_welding/integration/schemas/`](ventek_autonomous_welding/integration/schemas/) (mirrored in [`docs/interfaces/`](ventek_autonomous_welding/docs/interfaces/))
  - `scene.schema.json`
  - `trajectory.schema.json`
  - `cell_state.schema.json`
  - `process_feedback.schema.json`
  - `correction.schema.json`
  - `decision.schema.json`
- **Canonical Examples**: [`ventek_autonomous_welding/integration/examples/`](ventek_autonomous_welding/integration/examples/)
  - Positive examples: `scene_ok.json`, `trajectory_ok.json`, `cell_state_ready.json`, `correction_small.json`, `decision_execute.json`
  - Negative/fault examples: `scene_invalid.json`, `trajectory_unreachable.json`, `cell_state_fault.json`, `correction_replan.json`, `decision_pause.json`
  - Prediction policy: `process_feedback_unavailable.json`

### Contract Invariants
1. `schema_version`: Fixed to `"0.1"`.
2. `timestamp`: ISO-8601 UTC with milliseconds (e.g. `"2026-10-25T10:00:00.000Z"`).
3. `frame_id`: Explicit frame tag (`assembly_world`, `robot_base`).
4. Validation status enum: `PASS`, `FAIL`, `NOT_RUN`, `NOT_AVAILABLE`.
5. Unvalidated predictions must remain `null` with status `NOT_AVAILABLE`.

---

## 8. The 10 Minimum Integration Scenarios

The integration test suite ([`test_end_to_end_mock.py`](ventek_autonomous_welding/integration/tests/test_end_to_end_mock.py)) validates all 10 minimum integration scenarios:

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

## 9. Developer Quick Start Runbook

```bash
# 1. Source ROS 2 Humble
source /opt/ros/humble/setup.bash

# 2. Build both packages in workspace
cd /home/utkarsh/ventek_ws
colcon build --symlink-install
source install/setup.bash

# 3. Verify cell environment & 28 coordinate frames
python3 ventek_project/ventek_autonomous_welding/scripts/verify_cell_setup.py

# 4. Run all 46 automated tests (team logic, schemas, and scenarios)
python3 -m pytest ventek_project/ventek_autonomous_welding/tests/ ventek_project/ventek_autonomous_welding/integration/tests/

# 5. Run tests for your individual team
python3 -m pytest ventek_project/ventek_autonomous_welding/tests/team1/
python3 -m pytest ventek_project/ventek_autonomous_welding/tests/team6/

# 6. Run the end-to-end baseline vertical slice demo
python3 ventek_project/ventek_autonomous_welding/scripts/run_integration_pipeline.py

# 7. Launch the Spot Welding Cell (FANUC)
ros2 launch ventek_cell_description gazebo_cell.launch.py

# 8. Launch the Continuous Arc Welding Cell (KUKA)
ros2 launch ventek_autonomous_welding simulation.launch.py
```

### Running on macOS (Apple Silicon M2+) or Containerized via Docker
👉 **[`docker/README.md`](docker/README.md)**  
*(Native ARM64 container with Web-based 3D Desktop via noVNC on port 6080, CLI shell, and test runner)*

```bash
cd ventek_project/docker
docker compose up desktop      # Web Desktop at http://localhost:6080/vnc.html
docker compose run --rm dev    # Interactive shell
docker compose run --rm test   # Run full 46 automated tests
```

---

## 10. Reference Specifications & Documentation Index

- **[`docker/README.md`](docker/README.md)** — Multi-architecture Docker & macOS Apple Silicon (M2+) deployment guide.
- **[`VENTEK_Consolidated_Architecture_Baseline_and_JSON_Contracts.md`](VENTEK_Consolidated_Architecture_Baseline_and_JSON_Contracts.md)** — Architectural baseline and frozen v0.1 JSON schemas.
- **[`VENTEK_Final_Product_Approach_Review_Teams_1_3_4_5_6.md`](VENTEK_Final_Product_Approach_Review_Teams_1_3_4_5_6.md)** — Subsystem responsibilities, product criteria, and algorithm upgrade gates.
- **[`ventek_autonomous_welding/docs/SIMULATION_GUIDE.md`](ventek_autonomous_welding/docs/SIMULATION_GUIDE.md)** — Gazebo Sim Harmonic, 28 coordinate frames, joint control sliders, depth viewer, PBR lighting, and topic catalog.
- **[`ventek_cell_description/README.md`](ventek_cell_description/README.md)** — Heavy Industrial Spot Welding Cell specifications.
- **[`ventek_cell_description/BUILD_LOG.md`](ventek_cell_description/BUILD_LOG.md)** — Spot welding physical scaling, inertia tensors, and controller tuning.
- **[`ventek_autonomous_welding/docs/architecture/system_contract.md`](ventek_autonomous_welding/docs/architecture/system_contract.md)** — Shared contract rules and interface freeze.
- **[`ventek_autonomous_welding/docs/architecture/coordinate_frames.md`](ventek_autonomous_welding/docs/architecture/coordinate_frames.md)** — 28 coordinate frames and verified transform chains.
- **[`ventek_autonomous_welding/docs/architecture/system_architecture.md`](ventek_autonomous_welding/docs/architecture/system_architecture.md)** — High-level architecture, data flow, and error recovery.
- **[`ventek_autonomous_welding/docs/architecture/data_dictionary.md`](ventek_autonomous_welding/docs/architecture/data_dictionary.md)** — Comprehensive attribute, unit, and enum dictionary.

---

## 11. License

Proprietary — Ventek Automation
