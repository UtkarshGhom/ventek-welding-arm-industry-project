# VENTEK Autonomous Welding System

> **Vision-Based Autonomous Robotic Welding Program Generation & Execution**  
> From Scanning the Setup to Executing an Optimized, Collision-Free Welding Process

## Overview

This monorepo contains the complete software stack for Ventek's autonomous welding system. The system replaces manual teach-and-program workflows with an AI-driven pipeline that scans welding setups, detects joints, plans collision-free paths, executes welding, and continuously improves through reinforcement learning.

## Architecture

The system comprises 6 functional subsystems:

| Module | Description |
|--------|-------------|
| `team1_cognitive_autonomy` | High-level decision making, RL, digital twin |
| `team2_cell_coordination` | Robot/fixture/PLC orchestration, ROS 2 middleware |
| `team3_multimodal_ai` | Sensor fusion, anomaly detection, quality prediction |
| `team4_adaptive_control` | Real-time path correction, MPC, process tuning |
| `team5_vision` | 3D perception, joint detection, geometry extraction |
| `team6_path_planning` | IK, trajectory optimisation, collision checking |

## Quick Start

```bash
# 1. Clone and setup workspace
git clone <repo-url>
cd ventek_autonomous_welding
./scripts/setup_workspace.sh

# 2. Build with colcon
colcon build --symlink-install

# 3. Source workspace
source install/setup.bash

# 4. Launch simulation
ros2 launch launch/simulation.launch.py

# 5. Launch full system (hardware)
ros2 launch launch/full_system.launch.py
```

## Configuration

All system configuration is centralised in `config/`:
- `system_config.yaml` — Global parameters
- `robot_config.yaml` — Robot specs & joint limits
- `welding_params.yaml` — Default welding parameters
- `camera_config.yaml` — Camera calibration
- `ros2_topics.yaml` — Topic/service naming contracts
- `plc_registers.yaml` — PLC register map
- `safety_limits.yaml` — Safety thresholds

## Technology Stack

- **Middleware**: ROS 2 Humble
- **Vision**: OpenCV, Open3D, YOLOv8, PCL
- **ML/DL**: PyTorch, TensorFlow
- **Planning**: MoveIt 2, Ruckig
- **Simulation**: Gazebo Ignition, RViz 2
- **Industrial**: OPC-UA, Modbus
- **Edge**: NVIDIA Jetson, TensorRT
- **Containers**: Docker, Docker Compose

## Documentation

See `docs/` for detailed documentation including:
- System architecture diagrams
- API documentation
- Inter-team interface specifications
- Team reference materials

## License

Proprietary — Ventek Automation
