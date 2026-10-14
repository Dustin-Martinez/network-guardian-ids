# Operational Mandate: Role 4 - Kenneth

**Title:** Technical Tester & Video Producer

**Note on ownership:** The XGBoost execution phase was originally
assigned to Role 4. Execution was reassigned to Kit Dustin (Role 1)
on Day 6 of the sprint. See
`docs/decision/decision_role4_xgboost_reassignment_20261014.md`.
Kenneth retains Phase 1 onboarding (as a prerequisite reference),
Phase 3 documentation verification, and Phase 4 video production.

---

## Phase 1: Environment and Test Automation Setup

**Documents to reference:**
- `docs/SETUP.md` — onboarding guide; complete this before any other task
- `requirements.txt` — the pinned dependencies
- `src/verify_env.py` — the environment verification script
- `docs/README.md` — documentation hierarchy
- `docs/contracts/role-4-training-execution-spec.md` — the execution contract for the XGBoost run, now executed by Kit

- **Dependencies:** GitHub repository access.
- **Target Files:** Local `.venv`, cloned repository.
- **Instructions:**
  1. Complete `docs/SETUP.md` sections 1 through 10. This covers
     cloning the repository, creating `.venv` on Python 3.11.9,
     installing `requirements.txt`, running `python src/verify_env.py`,
     running Notebook 01 to generate `data/processed/`, verifying the
     data shapes, and verifying the four frozen hashes.
  2. Confirm the machine can allocate sufficient memory for a
     continuous 6-hour job.
  3. Confirm sleep and hibernate timers are disabled.
  4. Post in the team channel when all steps are complete.
- **Handoff:** Phase 1 completion noted in the sprint report.

**Sprint report name:**
`docs/reports/role-4-phase-1-kenneth-environment-setup.md`

---

## Phase 2: XGBoost Execution and Verification

**Ownership change:** This phase was originally assigned to Kenneth
(Role 4). Execution was reassigned to Kit Dustin (Role 1) on Day 6 of
the sprint. The mandate content is unchanged. The reassignment is
documented in
`docs/decision/decision_role4_xgboost_reassignment_20261014.md`.

**Documents to reference:**
- `docs/contracts/role-4-training-execution-spec.md` — authoritative execution contract, sections 3 through 16
- `docs/contracts/role-5-training-execution-spec.md` — TabNet contract, for reference on how the sibling run is documented
- `docs/contracts/artifact_transfer_policy.md` — the procedure for pushing meta sidecars and CSVs
- `src/models.py` — the frozen model code
- `notebooks/02_Model_Training.ipynb` — the notebook the executor runs
- `data/processed/split_indices.json` — the frozen split

- **Dependencies:** Kit has finalized `src/models.py`. Amber's Random
  Forest implementation is independent and does not block this phase.
- **Contract:** `docs/contracts/role-4-training-execution-spec.md`.
- **Target Files:** `notebooks/02_Model_Training.ipynb`, Cells 7 and 8.
- **Instructions:**
  1. Complete the pre-run checklist in section 15 of the execution
     contract.
  2. Run Cell 7 (XGBoost tuning). Estimated wall time: 4 to 6 hours.
  3. Run Cell 8 (XGBoost save).
  4. Verify outputs per section 9 of the contract.
  5. Post the XGBoost summary block per section 10 in the team channel.
  6. Push the three artifact files (meta sidecar, trial log, fold
     scores) to an artifact branch per
     `docs/contracts/artifact_transfer_policy.md` section 5.
- **Handoff:** Notify the team channel that the XGBoost artifacts are
  on disk and the artifact branch has been pushed.

**Note:** TabNet execution is owned by Role 5 (Dwayne). The XGBoost
executor does not run TabNet cells.

**Sprint report name:**
`docs/reports/role-4-phase-2-kit-xgboost-execution.md`

---

## Phase 3: Documentation Verification

**Documents to reference:**
- `docs/reports/discovery_log.md` — the discovery log to verify
- `docs/reports/executive_summary.md` — the executive summary to verify
- `docs/reports/role-4-phase-2-kit-xgboost-execution.md` — the
  execution record for the XGBoost run
- `docs/contracts/role-4-training-execution-spec.md` — the contract
  against which results are verified

- **Dependencies:** Markie's draft of the discovery log and executive
  summary. The XGBoost execution report must be complete.
- **Target Files:** `docs/reports/discovery_log.md`,
  `docs/reports/executive_summary.md`.
- **Instructions:** Review the documentation to confirm the empirical
  results (training times, hardware limits, optimization barriers)
  recorded match what was actually observed during the XGBoost run.
  Verify that Notebook 02 executes top-to-bottom without error on a
  fresh environment.

**Sprint report name:**
`docs/reports/role-4-phase-3-kenneth-documentation-verification.md`

---

## Phase 4: Video Production and Editing

**Documents to reference:**
- `docs/reports/presentation_script.md` — the script
- `docs/reports/paper.md` — the paper for on-screen references
- `docs/reports/paper_structure.md` section VI — the figure list for on-screen display
- `outputs/03_evaluation/*` — the figures to display
- `docs/reports/role-1-orientation-script.md` — orientation structure, if useful

- **Dependencies:** Finalization of all code and presentation scripts.
- **Target Files:** Final `.mp4` video file (5 to 8 minutes).
- **Instructions:** Coordinate recording sessions. Ensure every member
  is visible on camera and speaks. Splice the technical screen shares
  (UI demonstration, confusion matrices) with the speaker feeds. Edit
  for clarity, flow, and strict adherence to the 5 to 8 minute time
  limit.

**Sprint report name:**
`docs/reports/role-4-phase-4-kenneth-video-production.md`