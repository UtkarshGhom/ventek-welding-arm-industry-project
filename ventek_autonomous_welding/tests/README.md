# VENTEK Subsystem Tests & Logic Workspaces

Every subsystem team updates, iterates on, and validates their logic in their respective folder within this directory:

| Team | Directory | Test & Logic Workspace | Subsystem Package |
|---|---|---|---|
| **Team 1** | [`tests/team1/`](team1/) | [`test_team1_autonomy.py`](team1/test_team1_autonomy.py) | `src/team1_autonomy/` |
| **Team 2** | [`tests/team2/`](team2/) | [`test_team2_orchestration.py`](team2/test_team2_orchestration.py) | `src/team2_orchestration/` |
| **Team 3** | [`tests/team3/`](team3/) | [`test_team3_multimodal.py`](team3/test_team3_multimodal.py) | `src/team3_multimodal/` |
| **Team 4** | [`tests/team4/`](team4/) | [`test_team4_adaptive.py`](team4/test_team4_adaptive.py) | `src/team4_adaptive/` |
| **Team 5** | [`tests/team5/`](team5/) | [`test_team5_vision.py`](team5/test_team5_vision.py) | `src/team5_vision/` |
| **Team 6** | [`tests/team6/`](team6/) | [`test_team6_planning.py`](team6/test_team6_planning.py) | `src/team6_planning/` |

## How to Run Tests

```bash
# Run tests for your specific team
python3 -m pytest tests/team1/
python3 -m pytest tests/team2/
python3 -m pytest tests/team3/
python3 -m pytest tests/team4/
python3 -m pytest tests/team5/
python3 -m pytest tests/team6/

# Run all unit and integration tests across all teams
python3 -m pytest tests/ integration/tests/

# Or using colcon in your ROS 2 workspace
colcon test --packages-select ventek_autonomous_welding
colcon test-result --all
```

## Team Rules
1. All generated payloads must validate against the frozen schemas in [`integration/schemas/`](../integration/schemas/).
2. Maintain truth-in-reporting: use status enums `PASS`, `FAIL`, `NOT_RUN`, `NOT_AVAILABLE`. Never falsify unsupported checks as passing.
3. Every test file contains ready-to-run template logic and scenario checks.
