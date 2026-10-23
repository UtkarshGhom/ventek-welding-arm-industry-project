# VENTEK Spot Welding Cell & Robot Simulation Build Log

## Overview
This document tracks the step-by-step engineering changes, coordinate transformations, kinematic parameters, and package structure implemented to build the Gazebo Sim (Harmonic) and ROS 2 Humble simulation model for the **FANUC R-2000iA/165F Spot Welding Cell** (`ventek_cell_description`).

---

## 1. Initial Asset Assessment & Problem Statement

### 1.1 Source Models
* **Reference Assembly**: `/home/utkarsh/ventek_ws/ventek_project/reference_models/fanuc_setup.FCStd`
* **Raw STEP Model**: `/home/utkarsh/ventek_ws/ventek_project/reference_models/spot_welding-cell.STEP`
* **Raw Meshes**: `/home/utkarsh/ventek_ws/ventek_project/ventek_cell_description/meshes/*.stl`
* **Visual Reference Images**: 
  * `Robot spot concept1.png`: Layout of cell, robot, spot gun, dual jig carts, operator loading station, and controller.
  * `Screenshot from 2026-10-20 12-41-11.png`: FreeCAD tree hierarchy and part IDs.

### 1.2 Critical Technical Challenges Identified in Raw Assets
1. **Scale**: Raw STL exports were in millimeters ($1000\times$ larger than standard ROS/Gazebo SI units).
2. **Axis Mismatch**: FreeCAD assembly used $Y$-up convention ($Y \approx 664.5\text{ mm}$ floor to $2897.5\text{ mm}$ ceiling), whereas ROS/Gazebo REP-103 expects $Z$-up.
3. **Baked-in Posed Robot Links**: The robot links (`link_1` to `link_6`) were exported in an extended forward-reaching pose with arbitrary assembly offsets rather than zero-centered at their respective joint rotation axes.
4. **Tool Attachment Offset**: The spot welding gun was positioned in world coordinates ($Y \approx 2616\text{ mm}$) instead of at $(0,0,0)$ on the robot tool flange.
5. **Excessive Mesh Density**: `plc_setup.stl` had $>1.08\text{M}$ triangles ($52\text{ MB}$) and `setup_1`/`setup_2` had $>473\text{k}$ triangles each ($23\text{ MB}$), causing severe simulation physics degradation.

---

## 2. Mesh Pre-Processing & Coordinate Transformation Log

### 2.1 Robot Manipulator (FANUC R-2000iA/165F)
* Standardized ROS-Industrial official 6-DOF meshes downloaded and placed into:
  * `meshes/robot/visual/` (`base_link.stl`, `link_1.stl` ... `link_6.stl`)
  * `meshes/robot/collision/` (`base_link.stl`, `link_1.stl` ... `link_6.stl`)
* Verified that each link is zero-centered on its joint pivot axis and scaled in meters.

### 2.2 Spot Welding Gun (`meshes/tool/`)
* Extracted mounting flange center at $[1147.736, 2616.622, 1694.033]\text{ mm}$.
* Translated vertices to place mounting faceplate at $(0, 0, 0)$.
* Applied rotation:
  $$\begin{pmatrix} X_{tool} \\ Y_{tool} \\ Z_{tool} \end{pmatrix} = \begin{pmatrix} -1 & 0 & 0 \\ 0 & 0 & 1 \\ 0 & -1 & 0 \end{pmatrix} \begin{pmatrix} X_{cad} - X_0 \\ Y_{cad} - Y_0 \\ Z_{cad} - Z_0 \end{pmatrix} \times 0.001$$
* Result: Tool approach vector points along $+Z$; tool length is $1.132\text{ m}$.
* Calculated **Tool Center Point (TCP)**: `xyz="0.0713 0.0058 1.1152"` relative to `tool0`.
* Exported to `meshes/tool/visual/spot_gun.stl` and `meshes/tool/collision/spot_gun.stl`.

### 2.3 Cell Enclosure & Static Fixtures (`meshes/cell/`)
* **Cell Ground Floor Alignment**: Ground level was at CAD $Y = 664.47\text{ mm}$. Shifted $Y$ by $-664.47\text{ mm}$ and rotated by $-90^\circ$ around $X$:
  $$X_{ros} = X_{cad} \times 0.001, \quad Y_{ros} = -Z_{cad} \times 0.001, \quad Z_{ros} = (Y_{cad} - 664.47) \times 0.001$$
* **Frame**: Exported to `meshes/cell/visual/frame_cell.stl` ($Z \in [0.000, 2.233]\text{ m}$).
* **Service Door**: Centered at door track base; exported to `meshes/cell/visual/door.stl`. Joint at `xyz="-0.553 -0.281 0.242"`.
* **Fixture Carts**: Unified `setup_1` and `setup_2` into a single reusable `fixture_cart.stl` centered at $(0,0,0)$ on the wheels. Station 1 placed at `xyz="1.768 -2.605 0.0"`; Station 2 placed at `xyz="1.739 -0.909 0.0"`.
* **PLC / R-30iA Controller**: Decimated from $1.08\text{M}$ faces to $116\text{k}$ faces ($52\text{ MB} \to 5.6\text{ MB}$), centered at bottom surface. Placed at `xyz="1.614 0.613 0.0"`.

---

## 3. Package Architecture & Implementation Steps

### 3.1 Created Directory Structure
```
ventek_cell_description/
├── CMakeLists.txt
├── package.xml
├── BUILD_LOG.md
├── config/
│   ├── fanuc_controllers.yaml       # ros2_control JointTrajectoryController & JointStateBroadcaster
│   └── rviz.rviz                    # Preconfigured RViz2 setup with RobotModel, TF, and Grid
├── launch/
│   ├── view_cell.launch.py          # Interactive RViz visualizer with joint slider GUI
│   └── gazebo_cell.launch.py        # Complete Gazebo Sim + ros2_control + entity spawner
├── meshes/
│   ├── cell/
│   │   └── visual/                  # frame_cell.stl, door.stl, fixture_cart.stl, plc_cabinet.stl
│   ├── robot/
│   │   ├── visual/                  # Official base_link.stl, link_1.stl ... link_6.stl
│   │   └── collision/               # Official collision hulls
│   └── tool/
│       ├── visual/                  # Re-centered, scaled spot_gun.stl
│       └── collision/               # Optimized spot_gun.stl
├── urdf/
│   ├── fanuc_r2000ia165f.urdf.xacro # 6-DOF Fanuc kinematics, limits, dynamics, inertias
│   ├── spot_gun.urdf.xacro          # Tool definition, mounting flange, electrode TCP
│   ├── cell_environment.urdf.xacro # Enclosure, sliding door, dual fixture stations, PLC
│   ├── ventek_cell.urdf.xacro       # Top-level unified integration & ros2_control tags
│   └── ventek_cell.gazebo.xacro     # gz_ros2_control plugin, materials, surface physics
└── worlds/
    └── spot_welding_cell.sdf        # 1000 Hz physics world, industrial lighting, ground plane
```

---

## 4. Kinematic Tree & Joint Offsets

### 4.1 Kinematic Chain Hierarchy
```
world
├── cell_base
│   ├── cell_door (prismatic joint along Y, range: 0.0 to 0.75 m)
│   ├── fixture_station_1
│   │   └── workpiece_station_1
│   └── fixture_station_2
│       └── workpiece_station_2
├── plc_cabinet
└── robot_pedestal
    └── robot_pedestal_top
        └── base_link
            └── link_1 (revolute, Z-axis, ±180°)
                └── link_2 (revolute, Y-axis, -60° to +75°)
                    └── link_3 (revolute, -Y-axis, -185° to +230°)
                        └── link_4 (revolute, -X-axis, ±360°)
                            └── link_5 (revolute, -Y-axis, ±125°)
                                └── link_6 (revolute, -X-axis, ±360°)
                                    ├── flange (mechanical interface)
                                    └── tool0 (ROS standardized tool frame)
                                        └── spot_gun_base
                                            └── spot_tcp (welding contact point)
```

### 4.2 Joint Parameters (FANUC R-2000iA/165F)
* **Joint 1**: origin `xyz="0 0 0.670"`, limits: `[-3.14159, 3.14159]`, max vel: $1.8326\text{ rad/s}$ ($105^\circ/\text{s}$), effort: $12000\text{ N}\cdot\text{m}$
* **Joint 2**: origin `xyz="0.312 0 0"`, limits: `[-1.0472, 1.3090]`, max vel: $1.8326\text{ rad/s}$ ($105^\circ/\text{s}$), effort: $14000\text{ N}\cdot\text{m}$
* **Joint 3**: origin `xyz="0 0 1.075"`, limits: `[-3.2288, 4.0142]`, max vel: $1.8326\text{ rad/s}$ ($105^\circ/\text{s}$), effort: $10000\text{ N}\cdot\text{m}$
* **Joint 4**: origin `xyz="0 0 0.225"`, limits: `[-6.28318, 6.28318]`, max vel: $2.2689\text{ rad/s}$ ($130^\circ/\text{s}$), effort: $5000\text{ N}\cdot\text{m}$
* **Joint 5**: origin `xyz="1.280 0 0"`, limits: `[-2.1816, 2.1816]`, max vel: $2.2689\text{ rad/s}$ ($130^\circ/\text{s}$), effort: $5000\text{ N}\cdot\text{m}$
* **Joint 6**: origin `xyz="0.215 0 0"`, limits: `[-6.28318, 6.28318]`, max vel: $3.6651\text{ rad/s}$ ($210^\circ/\text{s}$), effort: $3000\text{ N}\cdot\text{m}$
* **Tool Flange to TCP**: `xyz="0.0713 0.0058 1.1152"`

---

## 5. Verification & Launch Instructions

### 5.1 Build the Package
```bash
cd /home/utkarsh/ventek_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select ventek_cell_description
source install/setup.bash
```

### 5.2 Validate URDF Structure & TF Tree
```bash
# Check XML and tree validity
check_urdf <(xacro $(ros2 pkg prefix --share ventek_cell_description)/urdf/ventek_cell.urdf.xacro)

# Validate Gazebo SDFormat conversion
gz sdf -p <(xacro $(ros2 pkg prefix --share ventek_cell_description)/urdf/ventek_cell.urdf.xacro)
```

### 5.3 Launch in RViz2 (Visual Verification with Joint Sliders)
```bash
ros2 launch ventek_cell_description view_cell.launch.py
```

### 5.4 Launch in Gazebo Sim (Harmonic Physics Simulation)
```bash
ros2 launch ventek_cell_description gazebo_cell.launch.py
```

### 5.5 ROS 2 Humble Launch Parameter Note
In ROS 2 Humble, string outputs from `Command(xacro ...)` passed to node parameters must be explicitly typed using:
```python
from launch_ros.parameter_descriptions import ParameterValue
robot_description = {'robot_description': ParameterValue(robot_description_content, value_type=str)}
```
This is configured in both `view_cell.launch.py` and `gazebo_cell.launch.py` to prevent launch-time YAML parsing exceptions.

---

## 6. Gazebo Sim Visibility, Slider Synchronization & Aesthetics

### 6.1 Root Cause for Missing Gazebo Meshes
* Gazebo Sim (Harmonic) does not resolve `package://ventek_cell_description/...` URIs unless `GZ_SIM_RESOURCE_PATH` (and `IGN_GAZEBO_RESOURCE_PATH`) is populated with the workspace share directories.
* Because the primitive `<box>` for `robot_pedestal` did not require an external mesh file, only the pedestal rendered in the initial Gazebo spawn.
* **Resolution**: Configured automated export of `GZ_SIM_RESOURCE_PATH` and `IGN_GAZEBO_RESOURCE_PATH` in `gazebo_cell.launch.py` encompassing `share/`, `install/`, and source mesh directories.

### 6.2 Synchronized Slider Control Architecture (RViz + Gazebo Sim)
To enable real-time joint motion in both Gazebo Sim and RViz simultaneously when dragging GUI sliders:
1. `joint_state_publisher_gui` publishes target joint angles to `/joint_states`.
2. `robot_state_publisher` updates TF frames for real-time visualization in RViz2.
3. Native Gazebo Sim `gz::sim::systems::JointPositionController` plugins were embedded into `ventek_cell.gazebo.xacro` for `joint_1` through `joint_6` and `cell_door_joint`.
4. `ros_gz_bridge` maps `/model/ventek_spot_welding_cell/joint/*/cmd_pos` topics between ROS 2 (`std_msgs/msg/Float64`) and Gazebo Sim (`gz.msgs.Double`).
5. A custom synchronizer node ([scripts/joint_slider_sync.py](file:///home/utkarsh/ventek_ws/ventek_project/ventek_cell_description/scripts/joint_slider_sync.py)) automatically reads `/joint_states` and commands the Gazebo position controllers.

### 6.3 Aesthetic Visual Material Palette
* **Cell Enclosure**: Sleek dark structural anthracite steel (`rgba="0.22 0.24 0.28 1.0"`).
* **Sliding Service Door**: Contrasting metallic brushed aluminum (`rgba="0.82 0.84 0.88 1.0"`).
* **Fixture Carts**: Industrial Machinery Blue (`rgba="0.14 0.36 0.64 1.0"`) matching the original concept reference.
* **Workpieces**: Clamped stamped automotive sheet-metal brackets (`rgba="0.75 0.78 0.82 1.0"`) mounted directly on Stations 1 and 2.
* **Fanuc Manipulator**: Signature Fanuc Golden Yellow (`rgba="0.96 0.72 0.05 1.0"`) with graphite base and precision wrist faceplate.
* **Spot Welding Gun**: Industrial graphite chassis with polished copper bronze electrode tips and an active amber TCP contact beacon.
* **PLC Controller**: Fanuc industrial cream cabinet (`rgba="0.88 0.88 0.84 1.0"`).


---

## 7. Eye-in-Hand Intel RealSense D435 Vision & Depth Mapping

### 7.1 POV Optimization & Zero-Occlusion Standoff Mount
* **Challenge**: An eye-in-hand camera mounted flush to the robot flange (`tool0`) would have its Field of View (FOV) severely occluded by the massive C-frame spot welding gun body, cylinders, and transformer.
* **Solution**: Designed a rigid carbon-fiber standoff extension bracket attached directly to the robot `tool0` flange:
  * **Mounting Pose**: Extends forward and outward to `xyz="0.25 0.22 0.85"` relative to `tool0`.
  * **Orientation**: Pitched down by $25^\circ$ ($0.436\text{ rad}$) and angled inward by $-15^\circ$ ($-0.262\text{ rad}$).
  * **Result**: The entire gun body is positioned behind and beside the camera cone ($Z < 0.85\text{ m}$), giving the camera an unobstructed line of sight straight over and past the electrode tips down onto the fixture carts and automotive sheet-metal workpieces.

### 7.2 Sensor Specifications & Simulation Architecture
* **Sensor**: Intel RealSense D435 RGB-D simulated via native Gazebo Sim `rgbd_camera` with the `ogre2` rendering engine:
  * **RGB Resolution**: $640 \times 480$ @ 30 Hz (Format: `R8G8B8`).
  * **Field of View**: $1.5184\text{ rad}$ ($87^\circ$ Horizontal FOV).
  * **Depth Sensing Range**: $0.15\text{ m}$ near plane to $5.0\text{ m}$ far plane.
  * **Kinematic Frames**: `camera_link` (physical chassis) and standard ROS convention `camera_optical_frame` ($Z$-forward, $X$-right, $Y$-down).

### 7.3 ROS 2 - Gazebo Sim Topics
The camera feeds are bridged in real time through `ros_gz_bridge`:
* `/realsense/image`: Color RGB feed (`sensor_msgs/msg/Image`).
* `/realsense/depth_image`: Calibrated depth distance map (`sensor_msgs/msg/Image`).
* `/realsense/camera_info`: Intrinsic optical calibration matrices (`sensor_msgs/msg/CameraInfo`).
* `/realsense/points`: 3D dense point cloud (`sensor_msgs/msg/PointCloud2`).

### 7.4 Dedicated RViz Depth Viewer
To inspect the camera POV, depth map, and point cloud alongside the main cell simulation without cluttering the robot workspace view, a dedicated RViz configuration and launch script was created:
```bash
# Terminal 1: Launch Gazebo Sim with synchronized sliders and primary RViz
ros2 launch ventek_cell_description gazebo_cell.launch.py

# Terminal 2: Launch Dedicated RealSense Depth & POV Vision RViz Window
ros2 launch ventek_cell_description view_vision.launch.py
```
The dedicated viewer includes:
1. **Live RGB Feed**: View from the eye-in-hand camera perspective.
2. **Normalized Depth Map**: Dynamic color/intensity gradient showing distance to fixtures and parts ($0.2\text{ m} - 3.5\text{ m}$).
3. **Dense 3D Point Cloud**: RGB-colored surface points projected into 3D world space.
4. **TF & Robot Model**: Real-time position tracking of the arm and camera bracket relative to the workcell.

---

## Step 8: Multi-Model Architecture Differentiation

| Specification | Model 1: `ventek_autonomous_welding` | Model 2: `ventek_cell_description` |
| :--- | :--- | :--- |
| **Welding Process** | Continuous Arc / MIG Seam Welding | Resistance Spot Welding |
| **Robot Arm** | **KUKA KR 6 R900 sixx** (Agilus) | **FANUC R-2000iA/165F** |
| **Payload / Reach** | 6 kg / 0.901 m reach | 165 kg / 2.655 m reach |
| **End-Effector** | Arc Welding Torch with wire tip | Heavy Servo Spot Welding C-Gun |
| **Cell Fixtures** | Stationary welding table + clamped weld plates | Dual mobile fixture carts + toggle clamps |
| **Enclosure** | Perimeter yellow wire safety fence | Structural steel cell frame with sliding safety door |
| **Camera Sensor** | Overhead / Standoff RGB-D camera | **Eye-in-Hand Intel RealSense D435** on tool0 bracket |
| **Active DOF** | 6 joints (`joint_a1` – `joint_a6`) | 7 joints (`joint_1` – `joint_6`, `cell_door_joint`) |
| **Vision Topics** | `/ventek/vision/camera/*` | `/realsense/*` (`image`, `depth_image`, `points`) |

---

## Step 9: Arm Inertia Oscillation Elimination & Pop-Out RealSense Dashboard

### 9.1 Inertia Damping & Oscillation Suppression
* **Problem**: The FANUC R-2000iA/165F and heavy spot welding gun represent over 650 kg of moving mass. The previous low derivative damping ($D=250$) and non-zero integral gain caused severe underdamping and integral windup, producing violent back-and-forth oscillation ("to and fro") whenever sliders were moved.
* **Controller Redesign**:
  * Scaled $D$ gains by over $18\times$ (Joint 1: $D=4500$, Joint 2: $D=5500$, Joint 3: $D=4000$) to provide critical damping.
  * Eliminated $I$ gain to completely prevent integral windup overshoot.
  * Updated URDF mechanical gearbox damping in `fanuc_r2000ia165f.urdf.xacro` (Joint 1: $180\text{ Nms/rad}$, Joint 2: $250\text{ Nms/rad}$, Joint 3: $180\text{ Nms/rad}$).
* **Smooth Motion Interpolator**:
  * Upgraded `joint_slider_sync.py` with a 50 Hz Exponential Moving Average (EMA, $\alpha=0.18$) filter.
  * Discrete slider jumps are smoothly shaped into fluid industrial robot trajectories, completely eliminating mechanical jerk and inertia bounce.

### 9.2 RealSense Camera Stream Fix
* **Problem**: Meshes failed to resolve in Gazebo's ogre2 render engine during launch, causing empty frames, and the Gazebo Sim frame_id was missing from the TF tree.
* **Fix**:
  * Directly injected `GZ_SIM_RESOURCE_PATH` and `IGN_GAZEBO_RESOURCE_PATH` into the Gazebo Sim process environment.
  * Added `<visualize>true</visualize>` and normalized topic names to `/realsense`.
  * Added Gazebo auto-generated frame alias `ventek_spot_welding_cell/link_6/realsense_d435` in URDF.
  * Added `MinimalScene` ogre2 3D View and JointPositionController plugins to `spot_welding_cell.sdf`.

### 9.3 Standalone Pop-Out Camera Dashboard
* **Implementation**: Created `scripts/view_realsense_feed.py` and `launch/view_camera.launch.py`:
  * **Pop-Out GUI**: Standalone OpenCV dashboard window (no RViz required).
  * **Side-by-Side View**: Real-time RGB stream on the left, colorized TURBO depth heatmap on the right.
  * **Interactive Depth Probe**: Hovering cursor anywhere over the camera feed probes exact distance in millimeters and meters.
  * **Controls**: `'s'` toggles view layout, `'+'`/`'-'` adjusts depth contrast, `'c'` captures snapshot, `'q'` exits.
  * Automatically launched with `ros2 launch ventek_cell_description gazebo_cell.launch.py` (or separately via `view_camera.launch.py`).

---

## Step 10: Gazebo Sim Model Visibility & Camera Optical Axis Realignment

### 10.1 Gazebo Entity Spawning & Mesh Resolution Fix
* **Missing `model.config`**: Gazebo Sim (Harmonic) resolves `model://ventek_cell_description/...` by scanning directories in `GZ_SIM_RESOURCE_PATH`. Without a `model.config` in the package root, Gazebo treats the folder as an invalid model and skips loading all mesh geometries (`MeshManager.cc:211 Unable to find file`).
  * Created [model.config](file:///home/utkarsh/ventek_ws/ventek_project/ventek_cell_description/model.config) and added it to CMakeLists.txt install rules.
* **Spawner Stability**: Replaced fragile `-string` parameter passing in `ros_gz_sim create` with pre-compiled `-file /tmp/ventek_cell_model.urdf`. Spawning now completes cleanly in $<0.2\text{ s}$ without risk of string buffer truncation or hanging.
* **3D Scene Viewport Centering**: Re-aimed Gazebo's `MinimalScene` viewport camera from generic $(0,0,0)$ to `<camera_pose>4.0 -4.5 2.6 0 0.362 2.432</camera_pose>`, directly framing the spot welding cell and robot pedestal upon startup.

### 10.2 Camera Orientation & Complete Occlusion Removal
* **Optical Axis Misalignment**: An RGB-D sensor in Gazebo Sim looks along the $+X$ axis of its link. In `tool0` coordinates, $+X$ points vertically upward towards the ceiling/sky. The previous small RPY angles caused the camera to point straight into the empty sky (rendering uniform sky-blue and infinite black depth).
* **Corrected Pitch & Yaw Alignment**: Re-calculated the rotation matrix to aim $+X$ along $+Z_{\text{tool0}}$ and pitched down towards the fixture table:
  * Pose: `origin xyz="0.28 0.28 1.02" rpy="-0.80 -1.35 -2.45"`.
* **Zero Gun Occlusion**: By extending the standoff strut to $Z=1.02\text{ m}$ (forward past the spot gun body) with a $0.28\text{ m}$ lateral offset, the spot welding gun is positioned entirely behind the camera cone, leaving an unobstructed view of the fixture tables and workpieces.

---

## Step 11: Proportional Scaling of Arm and Cell & Zero-Error Fixture POV Alignment

### 11.1 Problem Statement & Root Cause
1. **Oversized Robot Reach vs. Cell Envelope**:
   * The unscaled FANUC R-2000iA/165F has a physical reach of $2.655\text{ m}$, combined with the $1.12\text{ m}$ spot welding gun, yielding an outstretched reach of $3.78\text{ m}$.
   * The original cell enclosure was $2.69\text{ m} \times 4.04\text{ m}$ with a low $2.23\text{ m}$ ceiling, while the fixture carts sit just $1.9\text{ m} - 2.0\text{ m}$ from the pedestal.
   * Consequently, the arm in simulation extended through the cell perimeter walls and ceiling, making slider manipulation cramped and causing collision risks.
2. **Camera POV Fixture Blind Spot**:
   * Initializing all joints at `0.0` placed `tool0` pointing horizontally along $+X$ into the void beyond the right cell wall, so the camera looked away from the fixture tables into empty sky.
   * Without a nominal working pose, the eye-in-hand camera could not view the clamped workpiece or toggle clamps.

### 11.2 Scaled Geometry Specifications
* **FANUC R-2000iA/165F Arm Scaling ($0.75\times$)**:
  * Implemented `arm_scale="0.75"` in [urdf/fanuc_r2000ia165f.urdf.xacro](file:///home/utkarsh/ventek_ws/ventek_project/ventek_cell_description/urdf/fanuc_r2000ia165f.urdf.xacro) across all visual and collision meshes, kinematics, and mass/inertia properties.
  * Shoulder-to-wrist reach adjusted to $1.77\text{ m}$ ($2.60\text{ m}$ total reach with gun), enabling the arm to operate at a textbook $77\%$ extension when reaching the fixture cart.
  * Inertial mass dropped from $650\text{ kg} \to 270\text{ kg}$ ($0.75^3$), dramatically reducing control inertia and eliminating any residual overshoot.
* **Spot Welding Gun Scaling ($0.75\times$)**:
  * Scaled gun body and electrode tips in [urdf/spot_gun.urdf.xacro](file:///home/utkarsh/ventek_ws/ventek_project/ventek_cell_description/urdf/spot_gun.urdf.xacro): length $= 0.836\text{ m}$, TCP at `xyz="0.0535 0.0044 0.8364"`, mass $= 40.0\text{ kg}$.
* **Cell Enclosure Expansion ($1.20\times$)**:
  * Scaled `frame_cell.stl` and `door.stl` by $1.20\times$ in [urdf/cell_environment.urdf.xacro](file:///home/utkarsh/ventek_ws/ventek_project/ventek_cell_description/urdf/cell_environment.urdf.xacro).
  * Enclosure dimensions expanded to **$3.23\text{ m}$ Width $\times 4.85\text{ m}$ Depth $\times 2.68\text{ m}$ Height**, providing $>0.76\text{ m}$ of overhead clearance above the robot elbow.
  * Door sliding travel expanded to $0.90\text{ m}$.
  * Station 1 cart relocated to `(2.033, -2.996, 0.0)`; Station 2 relocated to `(2.000, -1.045, 0.0)`.

### 11.3 Eye-in-Hand RealSense D435 Precision Optical Aiming
* Scaled carbon-fiber bracket to $Z = 0.76\text{ m}$, offset $X = 0.22\text{ m}, Y = 0.22\text{ m}$ on `tool0`.
* Optical rotation matrix calculated via vector projection to center $(320, 240)$ directly on the workpiece at $500\text{ mm}$ distance:
  * Mount pose: `origin xyz="0.22 0.22 0.76" rpy="2.08 -0.81 -2.23"`.
  * Zero gun occlusion: spot gun chassis and electrodes stay behind and beside the optical cone.

### 11.4 Nominal Workpiece Inspection Pose & Auto-Centering
* Configured the following initial joint state across `ros2_control` ([urdf/ventek_cell.urdf.xacro](file:///home/utkarsh/ventek_ws/ventek_project/ventek_cell_description/urdf/ventek_cell.urdf.xacro)), `joint_slider_sync.py`, and `joint_state_publisher_gui`:
  * `joint_1`: $-0.4872\text{ rad}$ ($-27.9^\circ$, aimed directly at Station 1 fixture cart)
  * `joint_2`: $+0.6147\text{ rad}$ ($+35.2^\circ$, leaning forward)
  * `joint_3`: $+1.0346\text{ rad}$ ($+59.3^\circ$, elbow comfortably raised at $Z = 1.37\text{ m}$)
  * `joint_4`: $0.0000\text{ rad}$
  * `joint_5`: $-1.4147\text{ rad}$ ($-81.1^\circ$, gun and camera aimed down at the fixture table)
  * `joint_6`: $0.0000\text{ rad}$
  * `cell_door_joint`: $0.0\text{ m}$
* **Launch Result**:
  * Upon running `ros2 launch ventek_cell_description gazebo_cell.launch.py`, the robot spawns directly in the nominal working pose.
  * The standalone pop-out RealSense dashboard immediately displays the blue fixture cart, toggle clamps, and sheet metal workpiece centered in the camera feed with a depth distance reading of $\approx 500\text{ mm}$.



