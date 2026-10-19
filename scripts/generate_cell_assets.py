#!/usr/bin/env python3
"""
VENTEK Autonomous Welding - 3D Cell Asset Generator
Generates high-precision CAD meshes (DAE, OBJ, STL) with distinct materials:
1. Welding Torch (copper nozzle, stainless neck, black insulator, copper wire)
2. Modular 3D Welding Table (dark slate steel plate, anthracite legs, galvanized feet)
3. Fixture Base (anodized fixture blue plate, ground steel datum stops, riser pads)
4. Workpieces:
   - Nominal fabricated box frame (milled steel gray, with distinct weld seams)
   - T-Fillet joint workpiece
   - Butt joint workpiece
5. Destaco Toggle Clamps (safety red vinyl grip, zinc-plated arm & spindle, black rubber foot)
6. OAK-D Lite Depth Camera (anodized matte black body, optical glass lenses)
7. Cell Equipment (KRC4 controller cabinet, MIG power source)
"""

import os
import numpy as np
import trimesh

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PKG_ROOT = os.path.dirname(SCRIPT_DIR)
MESH_CELL_DIR = os.path.join(PKG_ROOT, "simulation", "cell", "meshes")
MESH_TOOL_DIR = os.path.join(PKG_ROOT, "simulation", "tool", "meshes")

os.makedirs(MESH_CELL_DIR, exist_ok=True)
os.makedirs(MESH_TOOL_DIR, exist_ok=True)


def export_colored_mesh(mesh, base_path):
    """Export mesh as STL (collision), DAE (COLLADA Z_UP for visual), and OBJ with vertex colors."""
    # 1. STL for collision checking
    mesh.export(base_path + ".stl")

    # 2. DAE (COLLADA Z_UP) with embedded multi-material Phong colors
    try:
        dae_data = mesh.export(file_type='dae')
        if isinstance(dae_data, str):
            dae_data = dae_data.encode('utf-8')
        # Ensure Z is UP in Collada
        dae_data = dae_data.replace(b'<up_axis>Y_UP</up_axis>', b'<up_axis>Z_UP</up_axis>')
        with open(base_path + ".dae", "wb") as f:
            f.write(dae_data)
    except Exception as e:
        print(f"Warning: DAE export error for {base_path}: {e}")

    # 3. Wavefront OBJ with vertex normals and colors
    mesh.export(base_path + ".obj", include_normals=True)


def create_welding_torch():
    """Create a high-fidelity swan-neck MIG welding torch with distinct materials."""
    parts = []

    # 1. Robot mounting flange & insulator block (Heat-resistant black nylon)
    flange = trimesh.creation.cylinder(radius=0.040, height=0.018, sections=36)
    flange.apply_translation([0, 0, 0.009])
    flange.visual.face_colors = [32, 32, 36, 255]
    parts.append(flange)

    block = trimesh.creation.box(extents=[0.050, 0.045, 0.035])
    block.apply_translation([0, 0, 0.018 + 0.0175])
    block.visual.face_colors = [32, 32, 36, 255]
    parts.append(block)

    # 2. Straight stem & angled swan-neck (Stainless steel chrome)
    stem_len = 0.070
    stem = trimesh.creation.cylinder(radius=0.012, height=stem_len, sections=24)
    stem.apply_translation([0, 0, 0.053 + stem_len / 2.0])
    stem.visual.face_colors = [195, 200, 208, 255]
    parts.append(stem)

    bend_angle = np.radians(45.0)
    neck_len = 0.120
    neck = trimesh.creation.cylinder(radius=0.010, height=neck_len, sections=24)
    rot_y = trimesh.transformations.rotation_matrix(bend_angle, [0, 1, 0])
    neck.apply_transform(rot_y)
    start_pos = np.array([0, 0, 0.053 + stem_len])
    center_offset = np.array([
        (neck_len / 2.0) * np.sin(bend_angle),
        0.0,
        (neck_len / 2.0) * np.cos(bend_angle)
    ])
    neck.apply_translation(start_pos + center_offset)
    neck.visual.face_colors = [195, 200, 208, 255]
    parts.append(neck)

    neck_end = start_pos + np.array([
        neck_len * np.sin(bend_angle),
        0.0,
        neck_len * np.cos(bend_angle)
    ])

    # 3. Gas nozzle (Polished Brass / Copper)
    nozzle_len = 0.055
    nozzle = trimesh.creation.cone(radius=0.013, height=nozzle_len, sections=24)
    nozzle.apply_transform(rot_y)
    nozzle_center = neck_end + np.array([
        (nozzle_len / 2.0) * np.sin(bend_angle),
        0.0,
        (nozzle_len / 2.0) * np.cos(bend_angle)
    ])
    nozzle.apply_translation(nozzle_center)
    nozzle.visual.face_colors = [218, 140, 50, 255]
    parts.append(nozzle)

    nozzle_tip = neck_end + np.array([
        nozzle_len * np.sin(bend_angle),
        0.0,
        nozzle_len * np.cos(bend_angle)
    ])

    # 4. Welding wire stick-out (Bright copper wire)
    wire_len = 0.015
    wire = trimesh.creation.cylinder(radius=0.0014, height=wire_len, sections=12)
    wire.apply_transform(rot_y)
    wire_center = nozzle_tip + np.array([
        (wire_len / 2.0) * np.sin(bend_angle),
        0.0,
        (wire_len / 2.0) * np.cos(bend_angle)
    ])
    wire.apply_translation(wire_center)
    wire.visual.face_colors = [240, 115, 35, 255]
    parts.append(wire)

    torch_mesh = trimesh.util.concatenate(parts)
    export_colored_mesh(torch_mesh, os.path.join(MESH_TOOL_DIR, "welding_torch"))
    print("Generated Welding Torch (Brass Nozzle, Steel Neck, Black Body)")


def create_welding_table():
    """Create a Siegmund/Demmeler modular 3D welding table with dark industrial cast iron & anthracite finish."""
    parts = []
    table_w = 1.20   # X dimension (m)
    table_d = 0.80   # Y dimension (m)
    top_thick = 0.05 # Z plate thickness (m)
    leg_h = 0.70     # Leg height (m)

    # Table Top Plate (Dark slate steel plate)
    top_plate = trimesh.creation.box(extents=[table_w, table_d, top_thick])
    top_plate.apply_translation([0, 0, leg_h + top_thick / 2.0])
    top_plate.visual.face_colors = [62, 66, 74, 255]
    parts.append(top_plate)

    # Side skirts
    skirt_drop = 0.08
    skirt_thick = 0.02
    for sx, sy, w, d in [
        (0, table_d / 2.0 - skirt_thick / 2.0, table_w, skirt_thick),
        (0, -table_d / 2.0 + skirt_thick / 2.0, table_w, skirt_thick),
        (-table_w / 2.0 + skirt_thick / 2.0, 0, skirt_thick, table_d),
        (table_w / 2.0 - skirt_thick / 2.0, 0, skirt_thick, table_d),
    ]:
        skirt = trimesh.creation.box(extents=[w, d, skirt_drop])
        skirt.apply_translation([sx, sy, leg_h - skirt_drop / 2.0])
        skirt.visual.face_colors = [52, 56, 62, 255]
        parts.append(skirt)

    # 4 Heavy Steel Legs (Dark Anthracite)
    leg_size = 0.08
    leg_pad_r = 0.06
    leg_pad_h = 0.02
    x_offsets = [-table_w / 2.0 + leg_size / 2.0 + 0.04, table_w / 2.0 - leg_size / 2.0 - 0.04]
    y_offsets = [-table_d / 2.0 + leg_size / 2.0 + 0.04, table_d / 2.0 - leg_size / 2.0 - 0.04]

    for lx in x_offsets:
        for ly in y_offsets:
            leg = trimesh.creation.box(extents=[leg_size, leg_size, leg_h - leg_pad_h])
            leg.apply_translation([lx, ly, (leg_h - leg_pad_h) / 2.0 + leg_pad_h])
            leg.visual.face_colors = [38, 40, 44, 255]
            parts.append(leg)

            pad = trimesh.creation.cylinder(radius=leg_pad_r, height=leg_pad_h, sections=24)
            pad.apply_translation([lx, ly, leg_pad_h / 2.0])
            pad.visual.face_colors = [125, 130, 138, 255]
            parts.append(pad)

    # Lower structural cross braces
    brace_z = 0.20
    for by in y_offsets:
        b = trimesh.creation.box(extents=[table_w - 0.16, 0.04, 0.04])
        b.apply_translation([0, by, brace_z])
        b.visual.face_colors = [46, 50, 55, 255]
        parts.append(b)

    for bx in x_offsets:
        b = trimesh.creation.box(extents=[0.04, table_d - 0.16, 0.04])
        b.apply_translation([bx, 0, brace_z])
        b.visual.face_colors = [46, 50, 55, 255]
        parts.append(b)

    table_mesh = trimesh.util.concatenate(parts)
    export_colored_mesh(table_mesh, os.path.join(MESH_CELL_DIR, "welding_table"))
    print("Generated Modular Welding Table (Dark Slate Steel Top & Anthracite Frame)")


def create_fixture_base():
    """Create a precision steel tooling base plate in vibrant Anodized Fixture Blue with ground datum blocks."""
    parts = []
    base_w = 0.46  # X
    base_d = 0.36  # Y
    base_t = 0.025 # Z

    # Base tooling plate (Anodized Tooling Blue)
    plate = trimesh.creation.box(extents=[base_w, base_d, base_t])
    plate.apply_translation([0, 0, base_t / 2.0])
    plate.visual.face_colors = [35, 95, 165, 255]
    parts.append(plate)

    # 2 Datum Locating Angle Blocks (Ground tool steel)
    stop1 = trimesh.creation.box(extents=[0.26, 0.035, 0.045])
    stop1.apply_translation([0, -0.125 / 2.0 - 0.035 / 2.0, base_t + 0.045 / 2.0])
    stop1.visual.face_colors = [195, 202, 210, 255]
    parts.append(stop1)

    stop2 = trimesh.creation.box(extents=[0.035, 0.14, 0.045])
    stop2.apply_translation([-0.24 / 2.0 - 0.035 / 2.0, 0, base_t + 0.045 / 2.0])
    stop2.visual.face_colors = [195, 202, 210, 255]
    parts.append(stop2)

    # 4 Clamp Mounting Riser Bosses
    clamp_pad_size = 0.055
    clamp_pad_h = 0.020
    for cx, cy in [[-0.14, -0.13], [0.14, -0.13], [-0.14, 0.13], [0.14, 0.13]]:
        pad = trimesh.creation.box(extents=[clamp_pad_size, clamp_pad_size, clamp_pad_h])
        pad.apply_translation([cx, cy, base_t + clamp_pad_h / 2.0])
        pad.visual.face_colors = [48, 115, 185, 255]
        parts.append(pad)

    fixture_mesh = trimesh.util.concatenate(parts)
    export_colored_mesh(fixture_mesh, os.path.join(MESH_CELL_DIR, "fixture_base"))
    print("Generated Fixture Base Plate (Anodized Blue & Ground Tooling Stops)")


def create_workpieces():
    """Create workpieces in distinct Milled Steel Metallic Gray."""
    # 1. Nominal Fabricated Box Workpiece
    parts_nominal = []
    L, W, H = 0.240, 0.125, 0.080
    t_base, t_wall = 0.010, 0.010

    # Bottom plate
    bottom = trimesh.creation.box(extents=[L, W, t_base])
    bottom.apply_translation([0, 0, t_base / 2.0])
    bottom.visual.face_colors = [142, 148, 158, 255]
    parts_nominal.append(bottom)

    # Side walls
    wall1 = trimesh.creation.box(extents=[L, t_wall, H - t_base])
    wall1.apply_translation([0, -W / 2.0 + t_wall / 2.0, t_base + (H - t_base) / 2.0])
    wall1.visual.face_colors = [148, 154, 164, 255]
    parts_nominal.append(wall1)

    wall2 = trimesh.creation.box(extents=[L, t_wall, H - t_base])
    wall2.apply_translation([0, W / 2.0 - t_wall / 2.0, t_base + (H - t_base) / 2.0])
    wall2.visual.face_colors = [148, 154, 164, 255]
    parts_nominal.append(wall2)

    # End walls
    inner_w = W - 2 * t_wall
    end1 = trimesh.creation.box(extents=[t_wall, inner_w, H - t_base])
    end1.apply_translation([-L / 2.0 + t_wall / 2.0, 0, t_base + (H - t_base) / 2.0])
    end1.visual.face_colors = [145, 150, 160, 255]
    parts_nominal.append(end1)

    end2 = trimesh.creation.box(extents=[t_wall, inner_w, H - t_base])
    end2.apply_translation([L / 2.0 - t_wall / 2.0, 0, t_base + (H - t_base) / 2.0])
    end2.visual.face_colors = [145, 150, 160, 255]
    parts_nominal.append(end2)

    # End mounting flanges
    flange_w = 0.020
    fl1 = trimesh.creation.box(extents=[flange_w, W + 0.030, H])
    fl1.apply_translation([-L / 2.0 - flange_w / 2.0, 0, H / 2.0])
    fl1.visual.face_colors = [138, 144, 152, 255]
    parts_nominal.append(fl1)

    fl2 = trimesh.creation.box(extents=[flange_w, W + 0.030, H])
    fl2.apply_translation([L / 2.0 + flange_w / 2.0, 0, H / 2.0])
    fl2.visual.face_colors = [138, 144, 152, 255]
    parts_nominal.append(fl2)

    wp_nominal = trimesh.util.concatenate(parts_nominal)
    export_colored_mesh(wp_nominal, os.path.join(MESH_CELL_DIR, "workpiece_nominal"))

    # 2. T-Joint Workpiece
    parts_t = []
    fl_t = trimesh.creation.box(extents=[0.240, 0.120, 0.010])
    fl_t.apply_translation([0, 0, 0.005])
    fl_t.visual.face_colors = [142, 148, 158, 255]
    parts_t.append(fl_t)
    wb_t = trimesh.creation.box(extents=[0.240, 0.010, 0.070])
    wb_t.apply_translation([0, 0, 0.010 + 0.035])
    wb_t.visual.face_colors = [148, 154, 164, 255]
    parts_t.append(wb_t)
    wp_t = trimesh.util.concatenate(parts_t)
    export_colored_mesh(wp_t, os.path.join(MESH_CELL_DIR, "workpiece_t_joint"))

    # 3. Butt-Joint Workpiece
    parts_butt = []
    p1 = trimesh.creation.box(extents=[0.240, 0.060, 0.010])
    p1.apply_translation([0, -0.0305, 0.005])
    p1.visual.face_colors = [142, 148, 158, 255]
    parts_butt.append(p1)
    p2 = trimesh.creation.box(extents=[0.240, 0.060, 0.010])
    p2.apply_translation([0, 0.0305, 0.005])
    p2.visual.face_colors = [148, 154, 164, 255]
    parts_butt.append(p2)
    wp_butt = trimesh.util.concatenate(parts_butt)
    export_colored_mesh(wp_butt, os.path.join(MESH_CELL_DIR, "workpiece_butt_joint"))
    print("Generated Workpieces (Milled Steel Metal)")


def create_toggle_clamp():
    """Create Destaco 207-U vertical handle toggle clamp with safety red handle & zinc-plated linkage."""
    parts = []

    # 1. Base mounting bracket (Zinc-plated steel)
    base = trimesh.creation.box(extents=[0.050, 0.045, 0.025])
    base.apply_translation([0, 0, 0.0125])
    base.visual.face_colors = [190, 195, 202, 255]
    parts.append(base)

    # 2. Pivot cheeks
    cheek1 = trimesh.creation.box(extents=[0.040, 0.006, 0.035])
    cheek1.apply_translation([0, -0.016, 0.025 + 0.0175])
    cheek1.visual.face_colors = [190, 195, 202, 255]
    parts.append(cheek1)

    cheek2 = trimesh.creation.box(extents=[0.040, 0.006, 0.035])
    cheek2.apply_translation([0, 0.016, 0.025 + 0.0175])
    cheek2.visual.face_colors = [190, 195, 202, 255]
    parts.append(cheek2)

    # 3. Handle stem (Steel) & Red vinyl grip
    handle_len = 0.090
    handle_stem = trimesh.creation.cylinder(radius=0.006, height=handle_len, sections=16)
    rot_handle = trimesh.transformations.rotation_matrix(np.radians(-10.0), [0, 1, 0])
    handle_stem.apply_transform(rot_handle)
    handle_stem.apply_translation([-0.010, 0, 0.050 + handle_len / 2.0])
    handle_stem.visual.face_colors = [190, 195, 202, 255]
    parts.append(handle_stem)

    # High-visibility Destaco Red Grip
    grip_len = 0.050
    grip = trimesh.creation.cylinder(radius=0.012, height=grip_len, sections=24)
    grip.apply_transform(rot_handle)
    grip.apply_translation([-0.010, 0, 0.050 + handle_len - grip_len / 2.0])
    grip.visual.face_colors = [220, 25, 25, 255]
    parts.append(grip)

    # 4. Horizontal clamping arm
    arm_len = 0.095
    arm = trimesh.creation.box(extents=[arm_len, 0.018, 0.014])
    arm.apply_translation([arm_len / 2.0 - 0.010, 0, 0.055])
    arm.visual.face_colors = [190, 195, 202, 255]
    parts.append(arm)

    # 5. Pressure spindle (Steel) & Cushion foot (Black rubber)
    spindle_x = arm_len - 0.018
    spindle_len = 0.045
    spindle = trimesh.creation.cylinder(radius=0.004, height=spindle_len, sections=16)
    spindle.apply_translation([spindle_x, 0, 0.055 - spindle_len / 2.0])
    spindle.visual.face_colors = [180, 185, 192, 255]
    parts.append(spindle)

    foot_r, foot_h = 0.012, 0.015
    foot = trimesh.creation.cylinder(radius=foot_r, height=foot_h, sections=24)
    foot.apply_translation([spindle_x, 0, 0.055 - spindle_len + foot_h / 2.0])
    foot.visual.face_colors = [25, 25, 28, 255]
    parts.append(foot)

    clamp_mesh = trimesh.util.concatenate(parts)
    export_colored_mesh(clamp_mesh, os.path.join(MESH_CELL_DIR, "clamp_toggle"))
    print("Generated Destaco Toggle Clamp (Safety Red Grip, Zinc-Plated Arm, Rubber Foot)")


def create_oak_d_lite():
    """Create OAK-D Lite depth camera model with anodized matte black body and optical glass lenses."""
    parts = []
    cam_w, cam_h, cam_d = 0.091, 0.028, 0.017

    body = trimesh.creation.box(extents=[cam_w, cam_d, cam_h])
    body.visual.face_colors = [25, 25, 28, 255]
    parts.append(body)

    lens_depth = 0.003
    rot_x = trimesh.transformations.rotation_matrix(np.radians(90), [1, 0, 0])
    for lx in [-0.0375, 0.0, 0.0375]:
        r = 0.006 if lx == 0.0 else 0.0045
        lens = trimesh.creation.cylinder(radius=r, height=lens_depth, sections=20)
        lens.apply_transform(rot_x)
        lens.apply_translation([lx, cam_d / 2.0 + lens_depth / 2.0, 0])
        # Center RGB is emerald, stereo side lenses are optical navy
        lens.visual.face_colors = [20, 55, 45, 255] if lx == 0.0 else [15, 40, 80, 255]
        parts.append(lens)

    bracket = trimesh.creation.box(extents=[0.025, 0.020, 0.030])
    bracket.apply_translation([0, -0.005, -cam_h / 2.0 - 0.015])
    bracket.visual.face_colors = [75, 78, 84, 255]
    parts.append(bracket)

    camera_mesh = trimesh.util.concatenate(parts)
    export_colored_mesh(camera_mesh, os.path.join(MESH_CELL_DIR, "camera_oak_d_lite"))
    print("Generated OAK-D Lite Depth Camera (Anodized Black Body & Optical Lenses)")


def create_cell_equipment():
    """Create industrial robot controller cabinet, MIG power source, and safety fence."""
    # 1. KRC4 Cabinet
    krc4_parts = []
    cabinet = trimesh.creation.box(extents=[0.60, 0.50, 1.00])
    cabinet.apply_translation([0, 0, 0.50])
    cabinet.visual.face_colors = [210, 212, 215, 255]
    krc4_parts.append(cabinet)

    holder = trimesh.creation.box(extents=[0.22, 0.06, 0.28])
    holder.apply_translation([0, 0.25 + 0.03, 0.70])
    holder.visual.face_colors = [35, 35, 38, 255]
    krc4_parts.append(holder)

    krc4_mesh = trimesh.util.concatenate(krc4_parts)
    export_colored_mesh(krc4_mesh, os.path.join(MESH_CELL_DIR, "krc4_controller"))

    # 2. MIG Power Source
    power_parts = []
    p_box = trimesh.creation.box(extents=[0.50, 0.40, 0.65])
    p_box.apply_translation([0, 0, 0.325])
    p_box.visual.face_colors = [190, 30, 30, 255]
    power_parts.append(p_box)

    spool = trimesh.creation.cylinder(radius=0.15, height=0.10, sections=24)
    rot_x = trimesh.transformations.rotation_matrix(np.radians(90), [1, 0, 0])
    spool.apply_transform(rot_x)
    spool.apply_translation([0, 0, 0.65 + 0.16])
    spool.visual.face_colors = [50, 50, 55, 255]
    power_parts.append(spool)

    power_mesh = trimesh.util.concatenate(power_parts)
    export_colored_mesh(power_mesh, os.path.join(MESH_CELL_DIR, "welding_power_source"))

    # 3. Fence panel
    fence_parts = []
    for px in [-0.50, 0.50]:
        post = trimesh.creation.cylinder(radius=0.025, height=2.00, sections=16)
        post.apply_translation([px, 0, 1.00])
        post.visual.face_colors = [40, 42, 45, 255]
        fence_parts.append(post)

    for pz in [0.15, 1.95]:
        rail = trimesh.creation.box(extents=[1.00, 0.04, 0.04])
        rail.apply_translation([0, 0, pz])
        rail.visual.face_colors = [40, 42, 45, 255]
        fence_parts.append(rail)

    mesh_p = trimesh.creation.box(extents=[0.96, 0.01, 1.76])
    mesh_p.apply_translation([0, 0, 1.05])
    mesh_p.visual.face_colors = [235, 195, 25, 200]
    fence_parts.append(mesh_p)

    fence_mesh = trimesh.util.concatenate(fence_parts)
    export_colored_mesh(fence_mesh, os.path.join(MESH_CELL_DIR, "safety_fence_panel"))
    print("Generated Cell Equipment (KRC4 Cabinet, MIG Power Source, Safety Fence Panel)")


if __name__ == "__main__":
    print("=== Generating VENTEK 3D Cell CAD Assets with Full Color Materials ===")
    create_welding_torch()
    create_welding_table()
    create_fixture_base()
    create_workpieces()
    create_toggle_clamp()
    create_oak_d_lite()
    create_cell_equipment()
    print("=== All 3D CAD Assets Successfully Created! ===")
