# Team 3 — Multimodal AI and Predictive Analytics

## 1. Product Role
Synchronizes robot kinematics, welding process telemetry, and perception feedback into timestamped multi-channel streams. Computes transparent statistical features, detects signal anomalies, and provides advisory alerts to Teams 1 and 4.

## 2. Core Responsibilities
- **Data Quality & Freshness**:
  - Validates time-order, sampling freshness, and channel completeness.
  - Flags missing or stale telemetry channels explicitly.
- **Transparent Anomaly Detection**:
  - Implements statistical baseline rules over windowed signals (current, voltage, speed).
  - Flags signal anomalies without confusing unusual data with confirmed weld defects.
- **Truth-in-Reporting (Predictions Policy)**:
  - Quality scores, defect probabilities, and uncertainty MUST remain `null` and marked `NOT_AVAILABLE` until physical, ground-truth inspection labels (post-weld NDT/macro-etch) and run-level cross-validation splits exist.
- **Advisory Output**:
  - Publishes recommendations to `/cell/process_feedback`. Advisory only; never directly commands robot motion.

## 3. Technology Stack
- **Language**: Python 3.10+
- **Framework**: ROS 2 Humble, NumPy, SciPy, scikit-learn, JSON Schema
- **Location**: `src/team3_multimodal/` (`MultimodalAnalytics`)

## 4. Interface Contracts
- **Produces**: `process_feedback.json` conforming to [`docs/interfaces/process_feedback_schema.json`](../interfaces/process_feedback_schema.json)
- **Consumes**:
  - Team 2 `cell_state.json` ([`cell_state_schema.json`](../interfaces/cell_state_schema.json))

## 5. Upgrade Gate (Baseline Target: 25 October)
- **Baseline**: Ingest + data-quality checks + windowed features + rule/statistical baseline + Isolation Forest.
- **Upgrade to Supervised Models (LightGBM/CNN-GRU/VAE)**: Requires held-out run-level datasets with physical ground truth labels demonstrating lower false-alarm rates than the transparent statistical baseline.
