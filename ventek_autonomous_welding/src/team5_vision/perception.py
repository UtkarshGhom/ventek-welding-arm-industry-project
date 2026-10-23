#!/usr/bin/env python3
"""
Team 5 - Computer Vision and Weld Intelligence
Perception pipeline, scene geometry generation, and candidate seam detection.
Follows VENTEK Consolidated Architecture Baseline v0.1.
"""

import datetime
import numpy as np
from typing import Dict, Any, List, Optional

class VisionPerception:
    """
    Simulated Perception Pipeline.
    Extracts workpiece, fixture, clamp geometry, and candidate seams.
    Enforces that geometric edges are candidate seams, not proof of weld intent.
    """

    def __init__(self, calibration_status: str = "VERIFIED"):
        self.seq = 0
        self.calibration_status = calibration_status

    def get_timestamp_utc(self) -> str:
        return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")

    def scan_scene(
        self,
        part_type: str = "workpiece_nominal",
        part_offset: Optional[List[float]] = None,
        inject_no_seam: bool = False
    ) -> Dict[str, Any]:
        self.seq += 1
        offset = np.array(part_offset or [0.0, 0.0, 0.0], dtype=float)

        part_base_pos = np.array([0.55, 0.0, 0.775]) + offset
        seam_start = part_base_pos + np.array([-0.108, -0.0525, 0.010])
        seam_end = part_base_pos + np.array([0.108, -0.0525, 0.010])
        seam_dir = seam_end - seam_start
        length = float(np.linalg.norm(seam_dir))
        direction_unit = (seam_dir / length).tolist() if length > 0 else [1.0, 0.0, 0.0]

        candidate_joints = []
        if not inject_no_seam:
            candidate_joints.append({
                "joint_id": "candidate_001",
                "part_ids": ["part_001"],
                "joint_type": "fillet",
                "start_point_m": [round(x, 4) for x in seam_start.tolist()],
                "end_point_m": [round(x, 4) for x in seam_end.tolist()],
                "direction_unit": [round(x, 4) for x in direction_unit],
                "length_m": round(length, 4),
                "local_normal": [0.0, 0.7071, 0.7071],
                "confidence": 0.88,
                "valid": True,
                "weld_intent_confirmed": False,
                "status": "CANDIDATE_REQUIRES_CONFIRMATION"
            })

        return {
            "schema_version": "0.1",
            "producer": "team5",
            "timestamp": self.get_timestamp_utc(),
            "seq": self.seq,
            "frame_id": "assembly_world",
            "units": {
                "position": "m",
                "angle": "rad"
            },
            "valid": True,
            "calibration_status": self.calibration_status,
            "parts": [
                {
                    "part_id": "part_001",
                    "type": "workpiece",
                    "mesh_uri": f"simulation/cell/meshes/{part_type}.stl",
                    "pose": {
                        "position_m": [round(x, 4) for x in part_base_pos.tolist()],
                        "orientation_xyzw": [0.0, 0.0, 0.0, 1.0]
                    },
                    "confidence": 0.95
                }
            ],
            "fixtures": [
                {
                    "fixture_id": "fixture_base_01",
                    "type": "modular_table",
                    "pose": {
                        "position_m": [0.55, 0.0, 0.75],
                        "orientation_xyzw": [0.0, 0.0, 0.0, 1.0]
                    }
                }
            ],
            "clamps": [
                {
                    "clamp_id": "clamp_01",
                    "state": "locked",
                    "pose": {
                        "position_m": [0.41, -0.13, 0.775],
                        "orientation_xyzw": [0.0, 0.0, 0.0, 1.0]
                    }
                }
            ],
            "candidate_joints": candidate_joints,
            "warnings": [] if candidate_joints else ["No candidate seam extracted from point cloud ROI"]
        }
