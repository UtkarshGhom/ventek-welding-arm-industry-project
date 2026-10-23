# VENTEK Shared Contract Rules & Canonical v0.1 Specification

## 1. Core Contract Rules (Frozen for Integration)

All subsystem communication, whether serialized over ROS 2 topics or exchanged as JSON payloads, must strictly conform to these rules:

1. **Schema Version**: Fixed to `"0.1"` (`"schema_version": "0.1"`).
2. **Timestamp Standard**: ISO-8601 UTC with millisecond precision (e.g. `"2026-10-25T10:00:00.000Z"`).
3. **Producer Attribution**: Explicit team string: `"team1"` through `"team6"`.
4. **Sequence Numbers**: Monotonically increasing integer `seq` per stream.
5. **Frame Identifiers**: All 3D coordinates must explicitly declare their frame (`"frame_id"`), typically `"assembly_world"` for vision and `"robot_base"` for motion/robot state.
6. **Standard Units**: SI units strictly:
   - Position: meters (`m`)
   - Angles & Joint Positions: radians (`rad`)
   - Time: seconds (`s`)
   - Electrical: Amperes (`A`), Volts (`V`)
7. **Quaternion Convention**: `[x, y, z, w]` order everywhere.
8. **Validation Enums**: Status checks must report one of: `PASS`, `FAIL`, `NOT_RUN`, `NOT_AVAILABLE`. Never substitute a passing value for an untested or unavailable metric.
9. **Missing Data Policy**: Missing channels or unvalidated predictions must be explicitly `null` with status `NOT_AVAILABLE`. Do not substitute "normal-looking" dummy data.
10. **Command Acknowledgement**: Every command decision has a unique `decision_id` (e.g. `cmd_0001`). Team 2 echoes this ID in `cell_state.json` and updates `status` (`accepted` -> `in_progress` -> `completed`/`failed`).

## 2. Summary of Frozen Schemas

| Payload | Producer | Consumer | Schema Location | Description |
|---|---|---|---|---|
| `scene.json` | Team 5 | Teams 6, 1 | [`docs/interfaces/scene_schema.json`](../interfaces/scene_schema.json) | Calibrated scene, workpieces, clamps, candidate seams |
| `trajectory.json` | Team 6 | Teams 2, 1 | [`docs/interfaces/trajectory_schema.json`](../interfaces/trajectory_schema.json) | Approach/weld/retreat waypoints, IK, joint & collision checks |
| `cell_state.json` | Team 2 | Teams 1, 3, 4 | [`docs/interfaces/cell_state_schema.json`](../interfaces/cell_state_schema.json) | Robot pose, clamps, process telemetry, command acknowledgement |
| `process_feedback.json` | Team 3 | Teams 1, 4, 2 | [`docs/interfaces/process_feedback_schema.json`](../interfaces/process_feedback_schema.json) | Data quality, signal anomalies, advisory alerts |
| `correction.json` | Team 4 | Teams 6, 1, 2 | [`docs/interfaces/correction_schema.json`](../interfaces/correction_schema.json) | Seam deviation, filtered offset, replan/pause request |
| `decision.json` | Team 1 | Teams 2, 5, 6 | [`docs/interfaces/decision_schema.json`](../interfaces/decision_schema.json) | Supervisory state transition, command ID, execution authorization |

## 3. Directory Layout for Schemas and Examples

```text
integration/
  schemas/
    scene.schema.json
    trajectory.schema.json
    cell_state.schema.json
    process_feedback.schema.json
    correction.schema.json
    decision.schema.json
  examples/
    scene_ok.json
    scene_invalid.json
    trajectory_ok.json
    trajectory_unreachable.json
    cell_state_ready.json
    cell_state_fault.json
    process_feedback_unavailable.json
    correction_small.json
    correction_replan.json
    decision_execute.json
    decision_pause.json
  tests/
    test_schema_validation.py
    test_end_to_end_mock.py
```
