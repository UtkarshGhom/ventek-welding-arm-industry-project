# Coordinate Frames and Transform Chain Specification

## 1. Primary Coordinate Frames

The VENTEK robotic welding workcell uses 28 well-defined coordinate frames adhering to ROS REP-103 and REP-105:

```text
world
  ├── robot_pedestal (0.0, 0.0, 0.55m)
  │     └── base_link / robot_base_link / robot_base
  │           └── link_1 -> link_2 -> link_3 -> link_4 -> link_5 -> link_6
  │                 └── flange -> tool0
  │                       └── welding_torch_link
  │                             └── welding_torch_tip / tcp_welding_torch
  │
  ├── welding_table (0.55, 0.0, 0.70m)
  │     └── fixture_base_link / fixture_frame (0.55, 0.0, 0.75m)
  │           ├── part_frame (0.55, 0.0, 0.775m)
  │           ├── clamp_1 (-0.14, -0.13, 0.025m relative to fixture)
  │           ├── clamp_2 ( 0.14, -0.13, 0.025m relative to fixture)
  │           ├── clamp_3 (-0.14,  0.13, 0.025m relative to fixture)
  │           └── clamp_4 ( 0.14,  0.13, 0.025m relative to fixture)
  │
  └── camera_link (0.85, 0.0, 1.35m)
        └── camera_optical_frame (optical axis aligned toward workpiece)
```

## 2. Canonical Transform Chain

All spatial coordinates transferred between perception, motion planning, and execution must resolve through the verified transform chain:

$$\text{camera\_optical} \longrightarrow \text{assembly\_world} \longrightarrow \text{robot\_base} \longrightarrow \text{robot\_flange} \longrightarrow \text{welding\_tcp}$$

### Rules:
1. **No Silent Frame Conversions**: Camera coordinates must NOT be treated as robot base coordinates without applying the extrinsic transformation.
2. **Calibration Status**: All vision payloads must declare `calibration_status` (`VERIFIED` or `UNVERIFIED`). Unverified transforms block trajectory execution.
3. **Tool Center Point (TCP)**: The welding wire tip TCP offset is defined as:
   - Position: `[0.1344, 0.0, 0.2574]` m relative to `flange`.
