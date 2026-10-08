# Operational Mandate: Role 2 - Markie

**Title:** Paper Lead & Backend Designer

---

## Phase 1: Documentation Scaffolding

**Documents to reference:**
- `docs/reports/paper_structure.md` — the paper's required sections and formatting
- `docs/reports/paper_narrative_context.md` — source material for Introduction, Problem Statement, Methodology
- `docs/README.md` — documentation hierarchy and escalation

- **Dependencies:** None.
- **Target Files:** `docs/reports/discovery_log.md`,
  `docs/reports/executive_summary.md`,
  `docs/reports/presentation_script.md`.
- **Instructions:** Set up the formatting for all final academic
  deliverables. Begin drafting the Executive Summary structure based
  on the six mandatory rubric questions. Establish the presentation
  script outline.

**Sprint report name:**
`docs/reports/role-2-phase-1-markie-documentation-scaffolding.md`

---

## Phase 2: Node.js Backend Bridge Development

**Documents to reference:**
- `docs/contracts/api_data_contract.md` — authoritative payload schema, HTTP status codes, validation rules
- `docs/reports/paper_narrative_context.md` section 13 — source pointer index
- `data/processed/feature_names.json` — the exact 43-feature ordering the bridge must reconstruct
- `data/processed/class_order.json` — the class name ordering for prediction decoding
- `data/processed/encoder_service.pkl` — frequency encoder for `service`
- `data/processed/encoder_onehot_protocol_flag.pkl` — one-hot encoder for `protocol_type` and `flag`
- `data/processed/scaler_tabnet.pkl` — StandardScaler for TabNet inference

- **Dependencies:** Requires predefined expected feature inputs from
  Kit. The interface is governed by
  `docs/contracts/api_data_contract.md`.
- **Target Files:** `server/server.js`, `server/predict_bridge.py`.
- **Instructions:**
  1. Navigate to `server/` (`cd server`) and run `node server.js` to
     start the Express server on port 5000.
  2. Implement the POST route at `/api/analyze` inside
     `server/server.js`.
  3. Write `server/predict_bridge.py` in Python to load trained model
     files from `../models/`.
  4. Configure Node.js to spawn `predict_bridge.py` via
     `child_process.spawn()` using the root `.venv/Scripts/python.exe`
     interpreter, passing packet JSON over `stdin` and returning the
     prediction JSON over `stdout` to Amber's TSX frontend.

**Sprint report name:**
`docs/reports/role-2-phase-2-markie-backend-bridge.md`

---

## Phase 3: Paper Integration

**Documents to reference:**
- `docs/reports/paper_structure.md` — professor format sections I through X
- `docs/reports/paper_narrative_context.md` — all sections; especially section 13 "Source Pointer Index" and section 14 "Where the Sprint Reports Map to Paper Sections"
- `outputs/03_evaluation/*` — figures and metrics to integrate
- `docs/reports/role-1-phase-2-kit-data-preparation.md` — data sections
- `docs/reports/role-1-phase-3-kit-model-architecture.md` — model sections
- `models/rf_baseline.meta.json`, `models/xgb_optuna.meta.json`, `models/tabnet_best.meta.json` — hyperparameters for Section IV

- **Dependencies:** Role 5 (Dwayne) delivers evaluation and XAI
  figures to `outputs/03_evaluation/`.
- **Target Files:** `docs/reports/paper.md`.
- **Instructions:**
  1. Integrate Dwayne's confusion matrices, per-class metrics tables,
     PR curves, and SHAP plots into the paper's Results and
     Explainability sections.
  2. Edit Dwayne's draft sections for coherence, terminology
     consistency, and style.
  3. Write the sections Markie owns: Introduction, Problem Statement,
     Related Work, Methodology, Discussion, Conclusion, Future Work.
  4. Ensure every figure and table in the paper cites its source file
     in `outputs/03_evaluation/`.
- **Handoff:** Paper draft ready for Kit's review.

**Sprint report name:**
`docs/reports/role-2-phase-3-markie-paper-integration.md`

---

## Phase 4: Final Documentation and Presentation

**Documents to reference:**
- `docs/reports/paper.md` — the integrated paper
- `docs/reports/discovery_log.md` — populated from Phase 1 report sources
- `docs/reports/role-1-phase-1-kit-environment-setup.md` — Phase 1 issues for the Discovery Log
- `docs/reports/role-1-phase-2-kit-data-preparation.md` — Phase 2 issues for the Discovery Log
- `docs/reports/role-1-phase-3-kit-model-architecture.md` — Phase 3 issues for the Discovery Log
- `docs/reports/presentation_script.md` — for the video segment

- **Dependencies:** Completion of Phase 3.
- **Target Files:** `docs/reports/*`.
- **Instructions:**
  1. Populate the Executive Summary and Discovery Log with final
     empirical results and visual outputs.
  2. Ensure all external resources and AI assistants are properly
     cited.
  3. Present the paper overview and backend segment during the final
     video recording.

**Sprint report name:**
`docs/reports/role-2-phase-4-markie-final-documentation.md`

---

## Scope Clarification

Evaluation and XAI metrics generation is owned by Role 5 (Dwayne).
Markie consumes the outputs and writes the narrative. Markie does not
produce confusion matrices or SHAP plots. Those are Dwayne's
deliverables.

Backend development (Express server and Python inference bridge) is
owned by Markie and remains in scope.