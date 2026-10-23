# VENTEK Autonomous Robotic Welding
## Final Product Approach Review — Teams 1, 3, 4, 5 and 6

**Purpose:** Review the available team reports from the perspective of the final product, not just the 25 October baseline.
**Scope note:** Team 2's report was unavailable and is intentionally not assessed. This document distinguishes report proposals from project-lead recommendations. Technical performance is not claimed as validated unless the source report provides evidence.

## Executive assessment

**Purpose:** This document reviews the five available team proposals from the perspective of the final VENTEK product: a system that understands a welding cell, identifies candidate welds, generates a feasible robot program, executes it in a coordinated cell, monitors deviations, and recovers safely. It is not a baseline-only checklist.

**Evidence status:** The team reports are proposals and implementation plans, not proof of completed performance. Team 3 explicitly states no experiments have been run; Team 5 states its example geometry and performance are illustrative; Team 6 says the proposed stack is not yet proof of a configured robot/solver/simulation. The recommendations below distinguish report content from project-lead feedback.

**Overall verdict:** The architecture is directionally sound. The main product risk is not a missing advanced algorithm; it is whether all modules share a trustworthy scene, robot model, coordinate frames, command lifecycle, and evidence of feasibility. Build a reliable deterministic product path first, then add learning where measured evidence shows value.

## Team 1 — Cognitive autonomy and supervisory decisions

**Product role:** The supervisory brain: chooses what the cell should do next and manages the job lifecycle. It should coordinate, not replace perception, motion planning, execution, adaptation, or independent safety systems.

### Proposed features
- Deterministic state machine covering job start, scanning, planning, validation, ready, execution, replanning, pause, fault and completion.
- Rule-based selection of the next candidate joint and fixture move, with configurable sequencing criteria.
- Input checks for schema validity, freshness, confidence and readiness before progressing.
- One active command at a time, with command identifiers and acknowledgement-aware transitions.
- Retry, pause, replan, human-intervention and fault-handling paths.
- Decision log and mock-input test harness for reproducible behaviour.

**Proposed technology stack:** Python 3; ROS 2 Humble with rclpy; Python Enum and explicit transition table/YAML; JSON Schema or Pydantic validation; optional python-transitions library. PPO/RL, Gymnasium/Stable-Baselines3 and a simulator are future candidates, not baseline dependencies.

**Proposed approach:** Consume the latest valid outputs from Teams 2–6, evaluate deterministic guards, emit one decision, wait for the corresponding execution acknowledgement, and record the transition. Keep thresholds configurable and make each transition testable.

### Project-lead review and recommendations
- Keep this deterministic supervisor as the product backbone; do not use an LLM or RL policy for safety-critical command decisions.
- Separate 'command accepted' from 'command completed'. Team 1 must not advance the job until Team 2 confirms completion or returns a fault/timeout.
- Define the product job model explicitly: job ID, part/recipe, required joints, weld process, sequence constraints, fixture requirements, and completion report.
- Make weld sequencing explainable: expose the reason/cost for a chosen next joint, including access, collision, fixture changes and any approved process constraints.
- Use hard gates for invalid calibration, uncertain weld intent, invalid trajectory, stale state, clamp/fixture not locked, or safety fault.
- Add recovery policy and idempotency: duplicate commands must not execute twice; restart/recovery must reconstruct state from logs and cell status.

**Product acceptance evidence:** A full job lifecycle with a normal completion, no detected seam, unreachable trajectory, stale input, command timeout, and safety-fault scenario. Each result should produce a traceable reason and event log.

## Team 3 — Multimodal AI and predictive analytics

**Product role:** Turns synchronized robot, process and vision streams into advisory indicators about unusual behaviour, tracking deviation and—only when labels exist—predicted quality. It should inform Teams 1 and 4, not directly command motion.

### Proposed features
- Timestamped ingestion and synchronization of cell state, robot kinematics, vision-derived geometry and available process channels.
- Explicit handling of missing, delayed, stale, invalid and differently sampled streams.
- Windowed time-domain features and a transparent rule/statistical baseline.
- Isolation Forest for unsupervised anomaly detection after the data pipeline is trustworthy.
- Conditional supervised models such as LightGBM/XGBoost with SHAP explainability if reliable labelled outcomes exist.
- Advanced candidate: dual-branch CNN-GRU plus spatial MLP and/or VAE, evaluated against the classical baseline.

**Proposed technology stack:** ROS 2 topics; Python; NumPy/pandas; scikit-learn; LightGBM or XGBoost; SHAP; a deep-learning framework for the conditional CNN-GRU/VAE phase; rosbag2 or equivalent logs for replay; JSON Schema for interface validation.

**Proposed approach:** Treat data quality and synchronization as the first product capability. Start with confirmed signals, define windows and features, establish rules/statistics, then test Isolation Forest. Train supervised models only with a defined target and trustworthy labels. Keep predictions null/NOT_AVAILABLE when evidence or channels are insufficient.

### Project-lead review and recommendations
- Prioritize data lineage, clock alignment, channel inventory and replay over neural architecture. Record sensor timestamp, receive timestamp, units, sample rate, source and quality per channel.
- Clarify what 'less than 10 ms' means: model inference, analytics latency, sensor-to-decision, or sensor-to-motion response. A 50 ms feature window cannot itself guarantee a sub-10 ms response.
- Do not equate anomaly detection with weld-defect detection. Quality claims need a source of truth such as post-weld inspection labels and run-level train/test separation.
- Use run-level or workpiece-level splits to avoid leakage from adjacent windows of the same weld appearing in both training and test data.
- Publish uncertainty, missing-channel status, model version and data-quality status with every advisory. Never silently substitute missing data with normal values.
- Define a small, measurable first product: detect injected signal anomalies and tracking-error growth, show the relevant contributing features, and report false alarms, misses and latency.

**Product acceptance evidence:** Replayable datasets; measured synchronization/freshness; baseline comparison; false-positive/false-negative and latency metrics; explicit NOT_AVAILABLE behaviour. Advanced models proceed only if they outperform the baseline on held-out runs.

## Team 4 — Adaptive welding and real-time quality control

**Product role:** Closes the feedback loop by estimating how observed seam/process behaviour differs from the plan and proposing a bounded correction, slowdown, replan or pause. It does not own the nominal path planner; Team 6 must validate any modified trajectory.

### Proposed features
- Compare planned seam/trajectory with observed seam or tracking feedback in a common coordinate frame.
- Filter noisy deviation measurements and calculate meaningful offset/error features.
- Apply configurable deadband, maximum correction, correction-rate and stale-data limits.
- Trigger replan or pause when the deviation exceeds the supported correction envelope.
- Use process feedback from Team 3 as an advisory input where its validity is established.
- Future research: reinforcement-learning proposals, MPC and physics-informed/deformation-aware modelling.

**Proposed technology stack:** Python/NumPy for measurement and filtering; ROS 2 for feedback messages; robot/camera geometry from Teams 5–6; simulation and replay for testing. The report discusses RL and MPC as later extensions; CalculiX/physics-informed approaches are optional research directions rather than established project dependencies.

**Proposed approach:** Start with measured error and conventional bounded feedback. Reject stale or invalid observations, calculate an absolute correction relative to a specific trajectory revision, then ask Team 6 to re-check IK, joint limits and collisions. If the correction cannot be validated, request replan/pause rather than forcing motion.

### Project-lead review and recommendations
- Make the correction contract explicit about frame, sign convention, units, timestamp, source measurement, trajectory ID/revision, limits profile and confidence.
- Prefer absolute offsets tied to a trajectory revision over repeatedly adding incremental offsets; this prevents duplicate or delayed messages from accumulating correction.
- Do not adjust welding current, voltage, speed or other process parameters until the physical process, sensor availability, allowed ranges and responsible authority are agreed.
- Keep safety limits independent of learned policies. Any correction that breaches a limit or lacks valid observations must fail closed.
- Separate seam-tracking error from weld-quality prediction: Team 4 controls correction logic; Team 3 estimates/analyzes signals; Team 6 validates motion.
- Evaluate advanced PINN/RL/MPC ideas against the simple feedback baseline on held-out disturbance scenarios, including cases where adaptation must be rejected.

**Product acceptance evidence:** Demonstrate a small simulated deviation that yields a bounded correction and a large/stale deviation that yields replan or pause. Show that Team 6 revalidates the result and that repeated messages do not accumulate unintended offsets.

## Team 5 — Computer vision and weld intelligence

**Product role:** Converts camera/depth/point-cloud data and CAD/assembly context into a calibrated 3D scene containing workpieces, fixtures, clamps and candidate seam geometry. It proposes where a weld might be; manufacturing instructions or operator/drawing evidence must confirm weld intent.

### Proposed features
- Camera and depth acquisition using the SDK for the actual selected sensor.
- Camera calibration and explicit camera-to-assembly / assembly-to-robot transforms.
- Point-cloud filtering, downsampling and outlier removal.
- Classical geometry pipeline using RANSAC plane segmentation, DBSCAN clustering and PCA/local geometry.
- Candidate seam endpoints, direction, length, confidence and data-quality/status fields.
- Visualisation and validation against known dimensions or CAD geometry; later, learned segmentation and defect classification if labelled data exist.

**Proposed technology stack:** Python 3.11; OpenCV 4.x; DepthAI for OAK-D Lite or pyrealsense2/librealsense for RealSense; Open3D 0.19+; NumPy/SciPy; JSON Schema and pytest. Use the SDK matching the actual camera rather than installing multiple stacks by default.

**Proposed approach:** Acquire and calibrate the sensor, transform depth to a point cloud, crop to a known region of interest, filter/downsample, segment dominant geometry, cluster candidate structures and estimate seam endpoints/length. Publish a scene payload with frame, calibration state, confidence and warnings.

### Project-lead review and recommendations
- Treat candidate-seam detection and weld-intent recognition as two different product functions. A geometric edge is not automatically a weld.
- Use the imported STEP/CAD model as a valuable reference where available: align the scan to CAD, compare observed geometry, and use drawing/BOM/operator rules to constrain candidate welds.
- Before purchasing a new camera, test the existing OAK-D Lite or available sensor on matte and reflective parts at the intended 30–80 cm range; inspect raw depth, alignment, calibration and scale.
- Define an explicit calibration owner and test it with known reference dimensions. Never infer camera-to-robot transform from the camera pose alone.
- Include fixture/clamp geometry and occlusion/visibility status, not just the workpiece. Team 6 needs collision-relevant scene geometry, and Team 1 needs confidence/ambiguity.
- Create a labelled evaluation set with known seam endpoints and non-weld edges; measure endpoint error, length error, candidate recall/precision and failure rate.

**Product acceptance evidence:** A repeatable scan or simulated/CAD-derived scene; correct scale/frame; candidate seams overlaid on geometry; comparison with known dimensions; explicit low-confidence/no-candidate states. Report sensor limitations and do not claim physical accuracy until measured.

## Team 6 — Robotic path planning, IK and motion

**Product role:** Transforms a confirmed or approved candidate seam into torch poses and a feasible, collision-checked, time-parameterized robot trajectory. This team owns nominal motion feasibility and revalidation of Team 4 corrections.

### Proposed features
- Convert seam geometry into local tangent/normal and approach, weld and retreat torch poses.
- Generate IK solutions and maintain joint-space continuity across waypoints.
- Check reachability, joint limits and singularity indicators supported by the robot model/solver.
- Build a planning scene with robot, workpiece, fixtures, clamps and relevant obstacles; check self/environment collision.
- Plan transfers, time-parameterize and optionally smooth the path; revalidate the final timed trajectory.
- Visualize and test in RViz and the selected simulator; return explicit failure/replan status when infeasible.

**Proposed technology stack:** ROS 2; URDF/Xacro and collision meshes; MoveIt 2; OMPL as a candidate planner; a robot-compatible IK plugin; RViz; Gazebo Sim or the project-approved simulator; MoveIt time parameterization; Ruckig as an optional later addition; Python/NumPy for geometry and tests.

**Proposed approach:** Validate input frames and robot/TCP model, construct Cartesian torch poses, solve IK, reject unreachable/discontinuous states, plan collision-aware transitions, time-parameterize, and validate the final trajectory again. Export a structured trajectory with explicit status and each check marked PASS/FAIL/NOT_AVAILABLE.

### Project-lead review and recommendations
- Resolve the actual FANUC model, joint configuration, joint limits, flange/tool geometry, TCP and base transform before treating a CAD assembly as a usable robot model. A STEP mesh alone does not encode joints or kinematics.
- Use a single source of truth for robot geometry and TCP. Verify units, mesh orientation, link hierarchy and collision meshes; visual appearance alone is insufficient.
- Separate the seam-following segment from approach, retreat and transfer motions. The seam path may be geometrically valid while the approach/retreat is blocked.
- Define torch orientation from the welding process and local seam geometry; do not assume a tangent alone determines the full tool pose.
- Collision, IK, joint-limit, velocity/acceleration and singularity checks must report their actual status. Unsupported checks must be NOT_AVAILABLE, never silently marked as passing.
- Benchmark MoveIt/OMPL and the chosen IK solver before adding a custom optimiser. Revalidate the final smoothed/time-parameterized trajectory, not just the original waypoints.

**Product acceptance evidence:** One known seam produces approach/weld/retreat poses and a simulated trajectory for the verified robot model. Include an unreachable pose and a blocked path test, each returning an explicit non-executable result.

## Team 2 — Deliberately not reviewed

**Status:** No Team 2 report was available in the reviewed set. Its approach, features and technology choices are therefore not assessed here.

**Product responsibility to confirm:** Cell orchestration: command lifecycle, robot/fixture/clamp coordination, cell state, fault reporting, and integration with the real controller/PLC where approved.

**Required review input:** Request a report specifying the command/acknowledgement protocol, robot-driver/controller interface, fixture and clamp states, safety boundary, state publication, recovery semantics, simulator integration and tests. Do not assume that a proposed Team 2 JSON schema is approved until its owners review it.

## Cross-team product decisions and integration risks

**1. Freeze the product contracts:** Agree versioned interfaces for scene, trajectory, cell state, process feedback, correction and supervisory decision. Standardize timestamps, frames, SI units, quaternion order, validity, confidence, status enums and stale-data policy.

**2. Define the coordinate transform chain:** Document and verify camera → assembly/workcell → robot base → flange → welding TCP. Every geometry and correction must state its frame; calibration uncertainty must be visible.

**3. Establish one source of truth for the cell:** The robot model, TCP, fixtures, clamps, workpiece and transforms must be shared between CAD, perception, planning and simulation.

**4. Define the product's job and weld semantics:** Specify how weld intent is confirmed, how weld types/process recipes affect torch pose and sequencing, and how an operator can review or override uncertain candidates.

**5. Make the execution lifecycle explicit:** Define accepted, running, completed, failed, cancelled and timed-out states; commands need IDs, acknowledgements, duplicate protection and recovery behaviour.

**6. Separate safety from AI:** Independent E-stop, PLC interlocks and robot safety functions must remain authoritative. ML, autonomy and correction modules cannot override them.

**7. Validate product value:** Measure setup/programming time saved, candidate seam accuracy, trajectory feasibility rate, collision rejection, recovery success, false alarms and cycle-time estimates. Do not claim autonomous welding productivity or weld quality until tested on real hardware with ground truth.

## Recommended product evolution

**Stage 1 — Digital workcell:** Reliable robot/workcell model, verified TCP/frames, CAD/scene inputs, simulation and a traceable job definition.

**Stage 2 — Assisted programming:** Operator-reviewed scene and weld candidates; feasible trajectory generation; simulation review and export.

**Stage 3 — Closed-loop simulation:** Cell orchestration, status telemetry, anomaly advisories, bounded corrections and automatic revalidation/replanning.

**Stage 4 — Controlled hardware pilot:** Only after risk review, controller/PLC integration, calibrated sensors, approved limits, low-speed commissioning and supervised tests.

**Stage 5 — Learning and optimisation:** Add learned perception, predictive quality models, RL/MPC or physics-informed models only where measured baselines expose a real limitation and data/validation support the upgrade.

## Final project-lead verdict

**Keep:** The separation of responsibilities; deterministic supervisory logic; classical geometry baseline; measured feedback; standard motion-planning stack; advisory analytics; and explicit failure statuses.

**Change or tighten:** Freeze schemas and coordinate frames; separate candidate geometry from confirmed weld intent; make Team 2's command lifecycle explicit; verify the robot/TCP model; and make every claimed validation measurable.

**Defer:** RL as the main supervisor, end-to-end deep multimodal prediction, physics-informed deformation control, custom trajectory optimisation and automatic process-parameter changes until data, simulation fidelity, safety constraints and baseline comparisons exist.

**Final product target:** A credible product is not six AI demonstrations. It is one integrated welding-programming system that takes a defined workcell/job, proposes and validates a weld plan, executes under controlled supervision, monitors the result, and either recovers safely or explains why it cannot proceed.
