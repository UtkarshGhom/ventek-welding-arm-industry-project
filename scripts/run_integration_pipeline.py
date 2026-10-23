#!/usr/bin/env python3
"""
VENTEK Autonomous Robotic Welding - Baseline Integration Runner
Runs the full consolidated vertical slice across Teams 1 through 6
or executes specific integration test scenarios.
"""

import sys
import os
import argparse
import json
from jsonschema import validate

# Ensure PKG_ROOT and src are on sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PKG_ROOT = os.path.dirname(SCRIPT_DIR)
if PKG_ROOT not in sys.path:
    sys.path.insert(0, PKG_ROOT)

from integration.pipeline import VentekIntegrationPipeline
from src.team1_autonomy import SupervisorStateMachine, SupervisoryState
from src.team2_orchestration import CellOrchestrator
from src.team3_multimodal import MultimodalAnalytics
from src.team4_adaptive import AdaptiveController
from src.team5_vision import VisionPerception
from src.team6_planning import TrajectoryPlanner

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def load_schema(name):
    schema_path = os.path.join(PKG_ROOT, "integration", "schemas", f"{name}.schema.json")
    with open(schema_path, "r") as f:
        return json.load(f)

def run_happy_path_demo():
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*75}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN} VENTEK Autonomous Welding - End-to-End Vertical Slice Baseline Demo {Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*75}{Colors.END}\n")

    pipeline = VentekIntegrationPipeline()
    res = pipeline.run_happy_path()

    for event in res["events"]:
        step = event["step"]
        print(f"{Colors.BOLD}{Colors.YELLOW}>> STEP: {step}{Colors.END}")
        for key, val in event.items():
            if key != "step":
                payload_str = json.dumps(val, indent=2)
                # Print abbreviated payload summary
                lines = payload_str.split("\n")
                if len(lines) > 20:
                    summary = "\n".join(lines[:10] + [f"   ... ({len(lines)-15} lines truncated) ..."] + lines[-5:])
                else:
                    summary = payload_str
                print(f"{summary}\n")

    if res["success"]:
        print(f"{Colors.GREEN}{Colors.BOLD}{'='*75}{Colors.END}")
        print(f"{Colors.GREEN}{Colors.BOLD} BASELINE SLICE COMPLETED SUCCESSFULLY: Supervisor state is {pipeline.supervisor.state.value} {Colors.END}")
        print(f"{Colors.GREEN}{Colors.BOLD}{'='*75}{Colors.END}\n")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD} FAILED: {res.get('error')} {Colors.END}\n")
        return 1

def main():
    parser = argparse.ArgumentParser(description="VENTEK Baseline Integration Pipeline Runner")
    parser.add_argument("--demo", action="store_true", help="Run the full baseline demonstration slice")
    parser.add_argument("--verify", action="store_true", help="Run pytest suite across all schemas and scenarios")
    args = parser.parse_args()

    # Default to demo if no args
    return run_happy_path_demo()

if __name__ == "__main__":
    sys.exit(main())
