# Operational Mandate: Role 3 - Amber

**Title:** Model Developer (Random Forest) & UI/UX Designer
---
## Phase 1: Frontend TSX Architecture

**Documents to reference:**
- `docs/SETUP.md` — onboarding guide; complete this before any other task
- `docs/contracts/api_data_contract.md` — TypeScript interfaces for `NetworkPacketRequest` and `PredictionResponse`
- `docs/design/ui_spec.md` — color palette, layout, panel specifications (if the file exists)
- `docs/reports/paper_narrative_context.md` section 13 — source pointer index

- **Dependencies:** GitHub repository access. Can be started
  concurrently with data preparation.
- **Target Directory:** `client/` (Next.js/React TSX App Router).
- **Target Files:** `client/src/app/page.tsx`,
  `client/src/components/*`.
- **Instructions:**
  1. Complete `docs/SETUP.md` sections 1 through 10. Confirm that
     Notebook 01 has been run, `data/processed/` exists, and the four
     frozen hashes print `OK`.
  2. Navigate to `client/` (`cd client`) and run `npm run dev` to
     launch the dev server on `http://localhost:3000`.
  3. Design the Security Operations Center (SOC) interactive dashboard
     using Tailwind CSS.
  4. Build input forms for the network telemetry features defined in
     `docs/contracts/api_data_contract.md` section 2. Fields
     `protocol_type`, `service`, and `flag` are strings, not integers.
  5. Build the alert module to render threat predictions and
     confidence meters.
- **Handoff:** Phase 1 completion noted in the sprint report.

**Sprint report name:**
`docs/reports/role-3-phase-1-amber-frontend-scaffold.md`

---

## Phase 2: Random Forest Development

**Documents to reference:**
- `docs/contracts/role-3-rf-architecture-spec.md` — the complete implementation contract for the RF section of `src/models.py`
- `docs/reports/role-1-phase-2-kit-data-preparation.md` — data pipeline that produces the input arrays
- `data/processed/feature_names.json` — the 43-feature ordering
- `data/processed/class_order.json` — the class name ordering
- `data/processed/split_indices.json` — the frozen train/test split
- `src/models.py` — the RF stubs to implement

- **Dependencies:** Kit has pushed the cleaned dataset to
  `data/processed/`.
- **Target Files:** `src/models.py`, Random Forest section only.
- **Instructions:** Implement the baseline Random Forest classifier
  following `docs/contracts/role-3-rf-architecture-spec.md` sections
  3 through 8. This serves as the bagging ensemble comparison against
  the boosting and deep learning models. Configure the model to
  produce feature importances to answer the rubric requirement
  regarding redundant features. Run Notebook 02 Cells 5 and 6.
- **Handoff:** Notify Kit that the Random Forest model is trained and
  that `models/rf_baseline.joblib` and `models/rf_baseline.meta.json`
  exist on disk.

**Sprint report name:**
`docs/reports/role-3-phase-2-amber-rf-baseline.md`

---

## Phase 3: Frontend-Backend Integration

**Documents to reference:**
- `docs/contracts/api_data_contract.md` — the payload contract for the integration
- `docs/contracts/role-2-phase-2-markie-backend-bridge.md` (sprint report) — Markie's implementation notes
- `outputs/03_evaluation/test_predictions.csv` — demo packet source for the UI

- **Dependencies:** Markie has started the Node.js Express server
  (`cd server; node server.js`).
- **Target Files:** `client/src/app/page.tsx`.
- **Instructions:** Connect the TSX dashboard form submission to send
  an HTTP POST request to `http://localhost:5000/api/analyze`.
  Dynamically render prediction labels, threat flags, and confidence
  percentages returned from Markie's Node.js bridge.

**Sprint report name:**
`docs/reports/role-3-phase-3-amber-frontend-backend-integration.md`

---

## Phase 4: Presentation Delivery

**Documents to reference:**
- `docs/reports/presentation_script.md` — Kenneth's script outline
- `docs/reports/paper_structure.md` section VI — figures for the demo
- `outputs/03_evaluation/confusion_matrix_rf.png` — RF confusion matrix for the segment

- **Instructions:** Record the assigned video segment. Present the
  Random Forest architecture, its baseline performance comparison, and
  conduct the live demonstration of the TSX UI dashboard.

**Sprint report name:**
`docs/reports/role-3-phase-4-amber-presentation.md`
