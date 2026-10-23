# VENTEK Autonomous Welding — Robotic Cell Simulation Environment

This directory contains the simulation environment, 3D CAD assets, Gazebo worlds, kinematic descriptions, and scenario test files for the VENTEK Autonomous Robotic Welding Cell.

---

## 1. Environment Stack

- **ROS Distribution:** ROS 2 Humble (`/opt/ros/humble`)
- **Simulator:** Gazebo Sim 8.14.0 (Gazebo Harmonic, modern `gz sim`)
- **Robot Model:** KUKA KR 6 R900 sixx (Agilus series, 6-DOF, 0.901 m reach, 6 kg payload)
- **Tooling:** Swan-neck MIG welding torch with calibrated TCP (`welding_torch_tip` / `tcp_welding_torch`)
- **Sensor:** OAK-D Lite RGB-D camera (simulated via Gazebo Sim `rgbd_camera` sensor plugin)
- **Motion Planning:** MoveIt 2 compatible kinematic and collision structure

---

## 2. Cell Layers & 3D Assets

| Layer | Component | Description | 3D Mesh Assets |
|---|---|---|---|
| **Layer A** | Cell Envelope | Epoxy shop floor, 3-sided safety fencing perimeter (2.4m x 2.6m x 2.0m) | `safety_fence_panel.stl` |
| **Layer B** | Robot & Torch | KUKA KR 6 R900 sixx arm on 0.55m pedestal riser + Swan-neck MIG torch | `base_link`..`link_6` (DAE/STL), `welding_torch.stl/.obj` |
| **Layer C** | Table & Fixture | Siegmund/Demmeler 3D modular welding table (1.2m x 0.8m) + Fixture tooling base plate with datum stop blocks | `welding_table.stl/.obj`, `fixture_base.stl/.obj` |
| **Layer D** | Workpiece | 240 x 125 x 80 mm fabricated box subassembly with 3 ground truth fillet joints | `workpiece_nominal.stl/.obj`, `workpiece_t_joint.stl`, `workpiece_butt_joint.stl` |
| **Layer E** | Clamps | 4x Destaco 207-U vertical handle toggle clamps with red grips and pressure feet | `clamp_toggle.stl/.obj` |
| **Layer F** | Perception Sensor | Overhead angled OAK-D Lite depth camera mount (`x=0.85, y=0.0, z=1.35`) | `camera_oak_d_lite.stl/.obj` |
| **Layer G** | Aux Equipment | KUKA KRC4 controller cabinet + MIG welding power source & wire spool unit | `krc4_controller.stl`, `welding_power_source.stl` |

---

## 3. Coordinate Frames & Conventions

Conforming to both `config/system_config.yaml` and `VENTEK_Gazebo_Welding_Cell_Simulation_Plan.md`:

```text
world
  ├── robot_pedestal
  │     └── base_link (alias: robot_base_link, robot_base)
  │           └── link_1 -> link_2 -> link_3 -> link_4 -> link_5 -> link_6
  │                 └── flange
  │                       └── tool0
  │                             └── welding_torch_link
  │                                   └── welding_torch_tip (alias: tcp_welding_torch)
  │                                         [Offset from tool0: xyz=(0.1344, 0.0, 0.2574), pitch=45°]
  ├── welding_table
  ├── fixture_base_link (alias: fixture_frame) [xyz=(0.55, 0.0, 0.75)]
  │     ├── part_frame [xyz=(0.0, 0.0, 0.025) relative to fixture]
  │     ├── clamp_1 (Front-Left)
  │     ├── clamp_2 (Front-Right)
  │     ├── clamp_3 (Rear-Left)
  │     └── clamp_4 (Rear-Right)
  ├── camera_link (alias: camera_frame) [xyz=(0.85, 0.0, 1.35)]
  │     └── camera_optical_frame
  ├── krc4_cabinet
  └── welding_power_unit
```

---

## 4. How to Launch & Test

### A. Run Automated Verification Test Suite
Verifies all 25 mesh files, URDF kinematic chain, TCP offsets, reachability, clamp collision detection, and scenario contracts:
```bash
cd /home/utkarsh/ventek_ws/ventek_project/ventek_autonomous_welding
python3 scripts/verify_cell_setup.py
```

### B. Interactive Cell Viewer (RViz2 + Joint Slider GUI)
Launches RViz2 and the joint slider GUI for quick inspection without starting Gazebo physics:
```bash
ros2 launch launch/view_cell.launch.py
```

### C. Full Gazebo Sim Simulation
Launches Gazebo Sim Harmonic, loads world environment, spawns the cell and robot, bridges topics to ROS 2, and starts RViz2:
```bash
ros2 launch launch/simulation.launch.py
```

### Bridged Topics:
- `/clock` : Simulation time clock
- `/ventek/vision/camera/image` : RGB Camera Stream (`sensor_msgs/msg/Image`)
- `/ventek/vision/camera/depth_image` : Depth Map Stream (`sensor_msgs/msg/Image`)
- `/ventek/vision/camera/points` : 3D Point Cloud (`sensor_msgs/msg/PointCloud2`)
- `/ventek/vision/camera/camera_info` : Camera Intrinsics (`sensor_msgs/msg/CameraInfo`)

---

## 5. Scenario Contracts

Located in `simulation/scenarios/`:
- `scenario_001_nominal.yaml`: Nominal setup, all 3 seams clear and reachable (`trajectory_valid: true`).
- `scenario_002_clamp_obstruction.yaml`: Clamp 1 moved into Seam 1 path (`collision_detected: true`).
- `scenario_003_part_shift.yaml`: Part shifted by +15mm X, +10mm Y (`vision_shift_detected: true`).
- `scenario_004_unreachable_joint.yaml`: Joint placed at 1.25m (`reachability_success: false`).
- `scenario_005_sensor_failure.yaml`: Camera stream timeout/dropped (`perception_status: SENSOR_FAILURE`).

---

## 6. Mock Data for Pipeline Integration

Located in `data/mock/`:
- `data/mock/scene_nominal.json`: Team 5 Vision output contract consumed by Team 6 and Team 1.
- `data/mock/trajectory_nominal.json`: Team 6 Path Planning output contract consumed by Team 2 and Team 4.
- `data/mock/cell_state_nominal.json`: Team 2 Cell State output contract consumed by Team 1, 3, and 4.
