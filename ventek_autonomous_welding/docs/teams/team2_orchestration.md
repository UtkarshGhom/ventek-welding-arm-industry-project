# Team 2 — Cell Orchestration and Simulation Execution

## 1. Product Role
Owns the physical and simulated workcell coordination. Manages the execution lifecycle for robot motion, fixture clamps, positioner tables, and welding power supplies. Echoes and acknowledges commands issued by Team 1, reporting truth-in-state.

## 2. Core Responsibilities
- **Command Acknowledgement Lifecycle**:
  - Handles command states: `accepted` -> `in_progress` -> `completed` or `failed`.
  - Echoes the originating `decision_id` in `cell_state.json`.
  - Distinguishes "command receipt" from "command completion".
- **Cell Component Telemetry**:
  - Robot state: `idle`, `moving`, `welding`, `paused`, `fault`, `homing`.
  - Joint positions (rad) and TCP pose (position m, orientation xyzw).
  - Fixture state (`locked`, `unlocked`, `moving`) and angle (rad).
  - Pneumatic clamp states (`locked`, `unlocked`).
  - Process signals: arc current (A), arc voltage (V), travel speed (m/s).
- **Safety Boundary**:
  - Independent PLC, safety gate interlocks, and physical/simulated E-stops operate outside AI authority.
  - Commands received while safety circuit is tripped are immediately rejected with status `failed`.

## 3. Technology Stack
- **Language**: Python 3.10+ / C++
- **Framework**: ROS 2 Humble, Gazebo Sim Harmonic, RViz 2
- **Location**: `src/team2_orchestration/` (`CellOrchestrator`)

## 4. Interface Contracts
- **Produces**: `cell_state.json` conforming to [`docs/interfaces/cell_state_schema.json`](../interfaces/cell_state_schema.json)
- **Consumes**:
  - Team 1 `decision.json` ([`decision_schema.json`](../interfaces/decision_schema.json))
  - Team 6 `trajectory.json` ([`trajectory_schema.json`](../interfaces/trajectory_schema.json))

## 5. Upgrade Gate (Baseline Target: 25 October)
- **Baseline**: Reliable command/state acknowledgement in Gazebo Sim + KUKA KR 6 R900 simulation model.
- **Upgrade**: Hardware controller driver integration only after simulation validation passes full regression test suite.
