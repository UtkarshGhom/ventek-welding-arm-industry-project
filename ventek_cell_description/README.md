# VENTEK Industrial Spot Welding Cell

> **Heavy Industrial Spot Welding Robotic Cell Simulation & Digital Twin**  
> FANUC R-2000iA/165F with Heavy Spot Welding Gun, Safety Cell Enclosure, Dual Mobile Fixture Carts, and Eye-in-Hand Intel RealSense D435 RGB-D Camera.

---

## 1. System Overview

The `ventek_cell_description` package models a heavy industrial automotive-grade resistance spot welding station in **Gazebo Sim 8 (Harmonic)** and **ROS 2 Humble**.

### Hardware & Sub-assembly Specifications:
* **Robot**: FANUC R-2000iA/165F (6-DOF, scaled proportionally at $0.75\times$ for realistic cell proportion: 1.77 m reach, industrial yellow finish).
* **End-Effector**: Heavy Spot Welding C-Gun (`spot_welding_gun`, $0.75\times$ scale) with dual copper electrodes, pneumatic servo cylinder, and high-current welding transformer.
* **Camera Vision**: Eye-in-Hand **Intel RealSense D435 RGB-D Camera** on an offset rigid carbon standoff bracket (`tool0`), precision aimed directly at the workpiece fixture table at 500 mm standoff distance, giving a clean, occlusion-free view of the fixture cart, toggle clamps, and clamped sheet metal parts.
* **Safety Enclosure**: Industrial steel structural frame scaled to $3.23\text{ m} \times 4.85\text{ m} \times 2.68\text{ m}$ height with wire mesh panels, clear acrylic operator inspection windows, $>0.76\text{ m}$ elbow ceiling clearance, and an interactive actuated sliding service door (`cell_door_joint`, 0.0 to 0.90 m stroke).
* **Fixtures**: Dual mobile fixture carts (`fixture_station_1` and `fixture_station_2`) in machinery blue with leveling casters, heavy clamping toggle clamps, and clamped automotive sheet metal workpieces.
* **Control**: Rittal-style industrial PLC control cabinet with operator HMI panel and status tower stack light.
* **Nominal Pose**: The cell launches automatically in a bent nominal inspection pose (`joint_1: -27.9°`, `joint_2: 35.2°`, `joint_3: 59.3°`, `joint_5: -81.1°`), directly framing the Station 1 workpiece in the camera feed.

---

## 2. Distinction from `ventek_autonomous_welding`

| Feature | `ventek_autonomous_welding` (Continuous Arc Seam) | `ventek_cell_description` (Spot Welding Cell) |
| :--- | :--- | :--- |
| **Primary Process** | Continuous Arc / MIG / Seam Welding | Resistance Spot Welding (Pneumatic/Servo C-Gun) |
| **Robot Manipulator** | **KUKA KR 6 R900 sixx** (Agilus) | **FANUC R-2000iA/165F** |
| **Payload / Reach** | 6 kg / 0.901 m reach | 165 kg / 2.655 m reach |
| **End Effector** | Angled Gas Metal Arc Torch + wire nozzle | Heavy Spot Welding Gun + dual copper electrodes |
| **Workpiece Setup** | Stationary modular welding table with T-plates | Dual mobile fixture carts with sheet metal parts |
| **Enclosure** | Perimeter safety wire fence | Full steel cell enclosure with sliding safety door |
| **Camera Mounting** | Standoff / Overhead camera | **Eye-in-Hand RealSense D435** on robot `tool0` |
| **Active Joints** | 6 joints (`joint_a1` – `joint_a6`) | 7 joints (`joint_1` – `joint_6`, `cell_door_joint`) |
| **Vision Topics** | `/ventek/vision/camera/*` | `/realsense/*` (`image`, `depth_image`, `points`) |

---

## 3. Quick Start & Terminal Launch Commands

### Build Workspace
```bash
cd /home/utkarsh/ventek_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

### Option A: RViz2 Lightweight Model Inspection (No Physics)
Inspect the entire cell, robot kinematics, frames, and test joints with GUI sliders:
```bash
ros2 launch ventek_cell_description view_cell.launch.py
```

### Option B: Full Gazebo Sim 8 Simulation + Pop-Out Camera Dashboard + Sliders
Runs Gazebo Sim with 1000 Hz physics, factory floor, lighting, automatic mesh resolution, joint position controllers with 50 Hz motion smoothing (preventing inertia bounce), interactive GUI sliders, and pops out the RealSense camera dashboard:
```bash
ros2 launch ventek_cell_description gazebo_cell.launch.py
```
*(Arguments: `camera_dashboard:=true` [default], `rviz:=true`, `gui:=true`)*

### Option C: Standalone Pop-Out RealSense D435 Camera Dashboard
Launches the dedicated OpenCV pop-out window with live side-by-side RGB stream, depth heatmap (Turbo colormap), and interactive mouse crosshair distance probe (reading distance in mm):
```bash
ros2 launch ventek_cell_description view_camera.launch.py
```

### Option D: RViz Vision & 3D PointCloud Viewer
Open in a separate terminal to view 3D RealSense point cloud, depth map, and optical frames in RViz:
```bash
ros2 launch ventek_cell_description view_vision.launch.py
```

---

## 4. Topic Interface

* **Robot Joint Commands**: `/model/ventek_spot_welding_cell/joint/joint_[1-6]/cmd_pos`
* **Sliding Door Command**: `/model/ventek_spot_welding_cell/joint/cell_door_joint/cmd_pos`
* **RealSense RGB Image**: `/realsense/image` (`sensor_msgs/msg/Image`)
* **RealSense Depth Map**: `/realsense/depth_image` (`sensor_msgs/msg/Image`)
* **RealSense 3D Point Cloud**: `/realsense/points` (`sensor_msgs/msg/PointCloud2`)
* **RealSense Camera Info**: `/realsense/camera_info` (`sensor_msgs/msg/CameraInfo`)
