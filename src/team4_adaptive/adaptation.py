#!/usr/bin/env python3
"""
Team 4 - Adaptive Welding and Real-Time Quality Control
Bounded seam deviation measurement, filtering, and correction proposals.
Follows VENTEK Consolidated Architecture Baseline v0.1.
"""

import datetime
import numpy as np
from typing import Dict, Any, List, Optional

class AdaptiveController:
    """
    Evaluates tracking deviations and proposes bounded absolute offsets.
    Does not command motion directly; requests revalidation through Team 6.
    """

    def __init__(
        self,
        deadband_m: float = 0.00005,      # 0.05 mm deadband
        max_correction_m: float = 0.0010, # 1.0 mm maximum allowable dynamic offset
        alpha_filter: float = 0.8         # Low pass filter factor
    ):
        self.seq = 0
        self.deadband_m = deadband_m
        self.max_correction_m = max_correction_m
        self.alpha_filter = alpha_filter
        self.last_filtered_offset = np.zeros(3)

    def get_timestamp_utc(self) -> str:
        return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")

    def process_deviation(
        self,
        trajectory_id: str,
        trajectory_revision: int,
        joint_id: str,
        planned_position_m: List[float],
        observed_position_m: List[float]
    ) -> Dict[str, Any]:
        self.seq += 1
        planned = np.array(planned_position_m, dtype=float)
        observed = np.array(observed_position_m, dtype=float)
        deviation = observed - planned
        dev_norm = np.linalg.norm(deviation)

        # Apply deadband
        if dev_norm < self.deadband_m:
            filtered = np.zeros(3)
        else:
            filtered = self.alpha_filter * deviation + (1.0 - self.alpha_filter) * self.last_filtered_offset

        self.last_filtered_offset = filtered
        filt_norm = np.linalg.norm(filtered)

        # Check safety limits
        within_limits = bool(filt_norm <= self.max_correction_m)

        if within_limits:
            action_requested = "CORRECT_WITH_REVALIDATION"
            reason = f"Bounded deviation {filt_norm*1000:.2f}mm within {self.max_correction_m*1000:.1f}mm limit; revalidation required"
        else:
            action_requested = "REQUEST_REPLAN"
            reason = f"Measured deviation {dev_norm*1000:.2f}mm exceeds maximum allowable limit ({self.max_correction_m*1000:.1f}mm); replan required"

        return {
            "schema_version": "0.1",
            "producer": "team4",
            "timestamp": self.get_timestamp_utc(),
            "seq": self.seq,
            "frame_id": "robot_base",
            "valid": True,
            "trajectory_id": trajectory_id,
            "trajectory_revision": trajectory_revision,
            "joint_id": joint_id,
            "measurement": {
                "planned_position_m": [round(x, 6) for x in planned.tolist()],
                "observed_position_m": [round(x, 6) for x in observed.tolist()],
                "deviation_m": [round(x, 6) for x in deviation.tolist()]
            },
            "filtered_offset_m": [round(x, 6) for x in filtered.tolist()],
            "proposed_absolute_offset_m": [round(x, 6) for x in filtered.tolist()],
            "within_limits": within_limits,
            "action_requested": action_requested,
            "speed_proposal_m_s": None,
            "confidence": 0.90 if within_limits else 0.75,
            "reason": reason,
            "limits_profile": "SIMULATION_ASSUMPTIONS_ONLY"
        }
