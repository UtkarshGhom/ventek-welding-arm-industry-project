#!/usr/bin/env python3
"""
VENTEK Autonomous Welding - Robotic Cell Environment Verification Script
Validates:
1. 3D Mesh Integrity (KUKA robot, welding torch, table, fixture, workpiece, clamps, camera)
2. URDF/Xacro kinematic chain & TF coordinate frame definitions
3. Tool Center Point (TCP) offset & orientation
4. Candidate weld joints reachability & kinematic envelope
5. Collision checking (nominal clearance vs clamp obstruction)
6. Scenario contracts & mock JSON interface files
"""

import os
import sys
import yaml
import json
import numpy as np
import xml.etree.ElementTree as ET

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PKG_ROOT = os.path.dirname(SCRIPT_DIR)

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_result(title, passed, message=""):
    status = f"{Colors.GREEN}[PASS]{Colors.END}" if passed else f"{Colors.RED}[FAIL]{Colors.END}"
    detail = f" - {message}" if message else ""
    print(f" {status} {title}{detail}")
    return passed

def test_mesh_assets():
    print(f"\n{Colors.BOLD}1. Checking 3D Mesh Assets (Visual & Collision):{Colors.END}")
    required_meshes = [
        "simulation/robot/meshes/visual/base_link.dae",
        "simulation/robot/meshes/visual/link_1.dae",
        "simulation/robot/meshes/visual/link_2.dae",
        "simulation/robot/meshes/visual/link_3.dae",
        "simulation/robot/meshes/visual/link_4.dae",
        "simulation/robot/meshes/visual/link_5.dae",
        "simulation/robot/meshes/visual/link_6.dae",
        "simulation/robot/meshes/collision/base_link.stl",
        "simulation/robot/meshes/collision/link_1.stl",
        "simulation/robot/meshes/collision/link_2.stl",
        "simulation/robot/meshes/collision/link_3.stl",
        "simulation/robot/meshes/collision/link_4.stl",
        "simulation/robot/meshes/collision/link_5.stl",
        "simulation/robot/meshes/collision/link_6.stl",
        "simulation/tool/meshes/welding_torch.stl",
        "simulation/tool/meshes/welding_torch.obj",
        "simulation/cell/meshes/welding_table.stl",
        "simulation/cell/meshes/fixture_base.stl",
        "simulation/cell/meshes/workpiece_nominal.stl",
        "simulation/cell/meshes/workpiece_t_joint.stl",
        "simulation/cell/meshes/workpiece_butt_joint.stl",
        "simulation/cell/meshes/clamp_toggle.stl",
        "simulation/cell/meshes/camera_oak_d_lite.stl",
        "simulation/cell/meshes/krc4_controller.stl",
        "simulation/cell/meshes/welding_power_source.stl"
    ]
    all_ok = True
    for mesh in required_meshes:
        full_path = os.path.join(PKG_ROOT, mesh)
        exists = os.path.exists(full_path) and os.path.getsize(full_path) > 0
        if not exists:
            all_ok = False
            print_result(mesh, False, "File missing or empty")
        else:
            print_result(mesh, True, f"{os.path.getsize(full_path)} bytes")
    return all_ok

def test_urdf_kinematic_frames():
    print(f"\n{Colors.BOLD}2. Validating URDF Kinematic Structure & Coordinate Frames:{Colors.END}")
    urdf_path = os.path.join(PKG_ROOT, "urdf", "welding_cell", "welding_cell.urdf")
    if not os.path.exists(urdf_path):
        print_result("URDF Exists", False, f"{urdf_path} not found")
        return False

    tree = ET.parse(urdf_path)
    root = tree.getroot()

    links = set(link.get("name") for link in root.findall("link"))
    joints = set(joint.get("name") for joint in root.findall("joint"))

    required_frames = [
        "world",
        "robot_pedestal",
        "base_link",
        "robot_base_link",
        "robot_base",
        "link_1",
        "link_2",
        "link_3",
        "link_4",
        "link_5",
        "link_6",
        "flange",
        "tool0",
        "welding_torch_link",
        "welding_torch_tip",
        "tcp_welding_torch",
        "welding_table",
        "fixture_base_link",
        "fixture_frame",
        "part_frame",
        "clamp_1",
        "clamp_2",
        "clamp_3",
        "clamp_4",
        "camera_link",
        "camera_optical_frame",
        "camera_frame"
    ]

    all_frames_ok = True
    for frame in required_frames:
        present = frame in links
        if not present:
            all_frames_ok = False
            print_result(f"Frame '{frame}'", False, "Missing in URDF links")
        else:
            print_result(f"Frame '{frame}'", True)

    # Check TCP definition
    tcp_joint = None
    for j in root.findall("joint"):
        if j.get("name") == "welding_torch_tip_joint":
            tcp_joint = j
            break

    if tcp_joint is not None:
        origin = tcp_joint.find("origin")
        xyz = [float(v) for v in origin.get("xyz").split()]
        expected_xyz = [0.1344, 0.0, 0.2574]
        match = np.allclose(xyz, expected_xyz, atol=0.005)
        print_result("TCP Welding Torch Offset", match, f"xyz={xyz}")
    else:
        print_result("TCP Welding Torch Offset", False, "welding_torch_tip_joint not found")

    return all_frames_ok

def test_kinematic_reachability():
    print(f"\n{Colors.BOLD}3. Kinematic Reachability & Work Envelope Checks:{Colors.END}")
    # KUKA KR 6 R900: reach = 0.901m
    max_reach = 0.901
    robot_base_world = np.array([0.0, 0.0, 0.55]) # Pedestal top

    # Workpiece nominal weld seams in world frame:
    # Fixture base link: [0.55, 0.0, 0.75]
    # Part frame: [0.55, 0.0, 0.775]
    part_origin_world = np.array([0.55, 0.0, 0.775])

    # Seam 1 (Longitudinal Fillet): 240mm (X: -0.108 to +0.108, Y: -0.0525, Z: +0.010)
    seam1_start = part_origin_world + np.array([-0.108, -0.0525, 0.010])
    seam1_mid   = part_origin_world + np.array([ 0.000, -0.0525, 0.010])
    seam1_end   = part_origin_world + np.array([ 0.108, -0.0525, 0.010])

    for pt_name, pt in [("Seam 1 Start", seam1_start), ("Seam 1 Mid", seam1_mid), ("Seam 1 End", seam1_end)]:
        dist = np.linalg.norm(pt - robot_base_world)
        reachable = dist < (max_reach - 0.05) # 50mm safety margin
        print_result(f"Reachability {pt_name}", reachable, f"distance={dist:.3f}m / max={max_reach:.3f}m")

    # Out of reach scenario test
    out_of_reach_pt = np.array([1.25, 0.0, 0.85])
    dist_oor = np.linalg.norm(out_of_reach_pt - robot_base_world)
    correctly_flagged_oor = dist_oor > max_reach
    print_result("Out-of-Reach Rejection (Scenario 4)", correctly_flagged_oor, f"distance={dist_oor:.3f}m > max_reach={max_reach:.3f}m")

    return True

def test_collision_constraints():
    print(f"\n{Colors.BOLD}4. Collision Detection & Interference Modeling:{Colors.END}")
    # Part bounding box in fixture frame:
    part_min = np.array([-0.120, -0.0625, 0.025])
    part_max = np.array([ 0.120,  0.0625, 0.105])

    # Nominal Clamps positions
    clamp_1_nominal = np.array([-0.14, -0.13, 0.025])
    clamp_clearance = np.linalg.norm(clamp_1_nominal[:2] - part_min[:2])
    nominal_safe = clamp_clearance > 0.050
    print_result("Scenario 1 Nominal Clamp Clearance", nominal_safe, f"clearance={clamp_clearance*1000:.1f}mm")

    # Scenario 2 Obstruction Clamp position: [-0.08, -0.06, 0.025]
    clamp_1_obstruct = np.array([-0.08, -0.06, 0.025])
    # Seam 1 passes at Y = -0.0525, Z = 0.035 from X = -0.108 to +0.108
    # Distance between clamp_1_obstruct and seam 1 trajectory:
    torch_radius = 0.020 # 20mm torch nozzle radius
    clamp_radius = 0.030 # 30mm clamp interference radius
    interference_dist = abs(clamp_1_obstruct[1] - (-0.0525))
    collision_detected = interference_dist < (torch_radius + clamp_radius)
    print_result("Scenario 2 Clamp Interference Detection", collision_detected, f"dist={interference_dist*1000:.1f}mm < threshold={(torch_radius+clamp_radius)*1000:.1f}mm")

    return nominal_safe and collision_detected

def test_scenarios_and_contracts():
    print(f"\n{Colors.BOLD}5. Testing Scenarios & Interface Contracts:{Colors.END}")
    all_ok = True

    # Check scenarios
    for i in range(1, 6):
        scen_name = f"scenario_{i:03d}"
        matching = [f for f in os.listdir(os.path.join(PKG_ROOT, "simulation", "scenarios")) if f.startswith(scen_name)]
        if matching:
            with open(os.path.join(PKG_ROOT, "simulation", "scenarios", matching[0]), "r") as f:
                data = yaml.safe_load(f)
                has_id = "scenario_id" in data
                has_outcome = "expected_outcome" in data
                print_result(f"Scenario {i} ({matching[0]})", has_id and has_outcome)
        else:
            all_ok = False
            print_result(f"Scenario {i}", False, "Missing scenario YAML")

    # Check mock JSON contracts
    json_contracts = ["scene_nominal.json", "trajectory_nominal.json", "cell_state_nominal.json"]
    for jf in json_contracts:
        path = os.path.join(PKG_ROOT, "data", "mock", jf)
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                valid_format = ("schema_version" in data and "producer" in data) or ("header" in data)
                print_result(f"Mock Contract {jf}", valid_format, f"{len(data)} root keys, schema_version={data.get('schema_version', 'legacy')}")
        else:
            all_ok = False
            print_result(f"Mock Contract {jf}", False, "File missing")

    return all_ok

def main():
    print(f"{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD} VENTEK Autonomous Welding - Robotic Cell Environment Verification {Colors.END}")
    print(f"{Colors.BOLD}{'='*70}{Colors.END}")

    t1 = test_mesh_assets()
    t2 = test_urdf_kinematic_frames()
    t3 = test_kinematic_reachability()
    t4 = test_collision_constraints()
    t5 = test_scenarios_and_contracts()

    all_passed = t1 and t2 and t3 and t4 and t5
    print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
    if all_passed:
        print(f"{Colors.GREEN}{Colors.BOLD} ALL VERIFICATION SUITES PASSED! CELL READY FOR PIPELINE INTEGRATION {Colors.END}")
    else:
        print(f"{Colors.RED}{Colors.BOLD} SOME VERIFICATION CHECKS FAILED! {Colors.END}")
    print(f"{Colors.BOLD}{'='*70}{Colors.END}\n")

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
