# Team 5 — Computer Vision and Weld Intelligence

## 1. Product Role
Converts camera depth and point cloud streams along with CAD/fixture models into a calibrated 3D scene representation. Proposes candidate weld seams with geometric properties and confidence scores.

## 2. Core Responsibilities
- **Calibration Status & Coordinate Frames**:
  - Requires explicit calibration state: `VERIFIED`, `UNVERIFIED`, `CALIBRATING`, or `FAILED`.
  - Transforms camera optical frames into `assembly_world` and `robot_base` through calibrated transform chains.
- **Scene Geometry Extraction**:
  - Segments workpieces, fixtures, and pneumatic clamps.
  - Generates collision-relevant bounding obstacles for Team 6.
- **Candidate Seam Detection**:
  - Proposes joint endpoints, direction vectors, length (m), and surface normals.
- **Candidate vs Weld Intent Rule**:
  - Candidate seams are geometric features, NOT proof of weld intent.
  - Sets `weld_intent_confirmed: false` and `status: "CANDIDATE_REQUIRES_CONFIRMATION"`.
  - Manufacturing rules, operator input, or job recipes must confirm weld intent before execution.

## 3. Technology Stack
- **Language**: Python 3.10+
- **Framework**: OpenCV 4.x, Open3D, NumPy, SciPy, DepthAI (OAK-D Lite) / pyrealsense2
- **Location**: `src/team5_vision/` (`VisionPerception`)

## 4. Interface Contracts
- **Produces**: `scene.json` conforming to [`docs/interfaces/scene_schema.json`](../interfaces/scene_schema.json)
- **Consumes**:
  - Depth camera point clouds, CAD models (STL/STEP)

## 5. Upgrade Gate (Baseline Target: 25 October)
- **Baseline**: Calibrated geometry + RANSAC plane fitting + DBSCAN clustering + PCA seam endpoints.
- **Upgrade to Deep Learned Seam Segmentation**: Only after a verified labelled evaluation dataset demonstrates improved recall and precision over classical geometry on reflective steel surfaces.
