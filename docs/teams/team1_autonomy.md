# Team 1 — Cognitive Autonomy and Supervisory Decisions

## 1. Product Role
The supervisory brain of the VENTEK cell. Coordinates the overall job lifecycle, evaluates deterministic guards, sequences candidate seams, manages human confirmations, and maintains the decision audit log. It coordinates—rather than replaces—perception, motion planning, execution, adaptation, and independent safety logic.

## 2. Core Responsibilities
- **Deterministic State Machine**: Manages transitions across `SCANNING`, `PLANNING`, `VALIDATING`, `READY`, `EXECUTING`, `PAUSED`, `REPLANNING`, `FAULT`, and `COMPLETE`.
- **Command Lifecycle**: Issues commands with unique `decision_id`s (e.g., `cmd_0001`) and waits for Team 2's command completion or fault acknowledgement before advancing.
- **Safety & Calibration Gates**:
  - Rejects planning if camera calibration is not `VERIFIED`.
  - Rejects execution if weld intent is not confirmed.
  - Halts execution and transitions to `FAULT` if PLC interlock or E-stop trips.
  - Halts motion and requests replan or safe pause if Team 4 signals an out-of-bounds deviation.
- **Decision Audit Log**: Records every state transition, evaluated input sequence numbers, and rationale codes.

## 3. Technology Stack
- **Language**: Python 3.10+
- **Framework**: ROS 2 Humble (`rclpy`), Python standard `enum`, `jsonschema`
- **Location**: `src/team1_autonomy/` (`SupervisorStateMachine`)

## 4. Interface Contracts
- **Produces**: `decision.json` conforming to [`docs/interfaces/decision_schema.json`](../interfaces/decision_schema.json)
- **Consumes**:
  - Team 5 `scene.json` ([`scene_schema.json`](../interfaces/scene_schema.json))
  - Team 6 `trajectory.json` ([`trajectory_schema.json`](../interfaces/trajectory_schema.json))
  - Team 2 `cell_state.json` ([`cell_state_schema.json`](../interfaces/cell_state_schema.json))
  - Team 3 `process_feedback.json` ([`process_feedback_schema.json`](../interfaces/process_feedback_schema.json))
  - Team 4 `correction.json` ([`correction_schema.json`](../interfaces/correction_schema.json))

## 5. Upgrade Gate (Baseline Target: 25 October)
- **Baseline**: Deterministic state machine + rule-based sequencing + schema/freshness gates.
- **Upgrade to RL/Advanced Search**: Only when deterministic rules reveal measured sequencing limitations in held-out physical/simulated trials. LLMs and unconstrained RL policies are strictly forbidden from issuing direct industrial motion commands.
