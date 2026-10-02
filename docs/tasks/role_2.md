# Operational Mandate: Role 2 - Markie
**Title:** Paper Lead, Evaluation/XAI Engineer & Backend Designer

## Phase 1: Documentation Scaffolding
* **Dependencies:** None.
* **Target Files:** `reports/discovery_log.md`, `reports/executive_summary.md`, `reports/presentation_script.md`.
* **Instructions:** Setup the formatting for all final academic deliverables. Begin drafting the Executive Summary structure based on the six mandatory rubric questions. Establish the presentation script outline.

## Phase 2: Node.js Backend Bridge Development
* **Dependencies:** Requires predefined expected feature inputs from Kit Dustin.
* **Target Files:** `server/server.js`, `server/predict_bridge.py`.
* **Instructions:** 
  1. Navigate to `server/` (`cd server`) and run `node server.js` to start the Express server on port 5000.
  2. Implement the POST route at `/api/analyze` inside `server/server.js`.
  3. Write `server/predict_bridge.py` in Python to load trained `.pkl` and `.pt` model files from `../models/`.
  4. Configure Node.js to spawn `predict_bridge.py` via `child_process.spawn()` using the root `.venv/Scripts/python.exe` interpreter, passing packet JSON over `stdin` and returning the prediction JSON over `stdout` to Amber's TSX frontend.

## Phase 3: Evaluation Metrics & Explainable AI (XAI)
* **Dependencies:** **BLOCKER** - Wait for Kenneth to finish Phase 2 and populate `models/` with trained artifacts.
* **Target Files:** `src/evaluate.py`, `notebooks/03_Evaluation_and_XAI.ipynb`.
* **Instructions:** 
  1. Load trained models and compute Macro F1-Score, Precision, and Recall for all 5 classes.
  2. Generate and export multi-class confusion matrices to `outputs/`.
  3. Implement decision threshold calibration to prioritize detection of rare `u2r` and `r2l` attacks.
  4. Run `shap.TreeExplainer` on the XGBoost model to generate feature importance plots, providing forensic evidence of which features trigger alerts.

## Phase 4: Final Documentation & Presentation
* **Dependencies:** Completion of Phase 3.
* **Target Files:** `reports/*`.
* **Instructions:** Populate the Executive Summary and Discovery Log with final empirical results and visual outputs. Ensure all external resources and AI assistants are properly cited. Present the Evaluation & XAI segment during the final video recording.