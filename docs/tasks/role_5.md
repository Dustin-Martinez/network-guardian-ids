
# Operational Mandate: Role 5 - Dwayne

**Title:** Evaluation Engineer, Explainability Contributor & TabNet
Executor

---
## Phase 1: Onboarding and Environment

**Documents to reference:**
- `docs/SETUP.md` — onboarding guide; complete this before any other task
- `docs/README.md` — documentation hierarchy and escalation
- `docs/contracts/role-5-training-execution-spec.md` — the TabNet execution contract
- `docs/contracts/role-4-training-execution-spec.md` — the XGBoost execution contract, for reference on sibling format
- `requirements.txt` — pinned dependencies
- `src/verify_env.py` — verification script
- `src/utils.py` — the environment setup, including the LOKY_MAX_CPU_COUNT default

- **Dependencies:** GitHub repository access.
- **Target Files:** Local `.venv` on Python 3.11.9.
- **Instructions:**
  1. Complete `docs/SETUP.md` sections 1 through 10. This covers
     cloning the repository, creating `.venv` on Python 3.11.9,
     installing `requirements.txt`, running `python src/verify_env.py`,
     running Notebook 01 to generate `data/processed/`, verifying the
     data shapes, and verifying the four frozen hashes.
  2. Confirm the laptop is available for a continuous 8-hour run.
  3. Confirm sleep and hibernate timers are disabled.
  4. Post in the team channel when all steps are complete.
- **Handoff:** Phase 1 completion noted in the sprint report.

**Environment tuning — optional but recommended:**

`src/utils.py` sets a default value for the joblib worker count:

```python
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "8")
```

This default works on any machine but is conservative. If your laptop
has more physical cores than eight, raise the value to match. On
Windows, physical core count can be checked via Task Manager
(Performance tab, CPU, "Cores" field) or by running:

```powershell
Get-CimInstance -ClassName Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors
```

Change the number to your physical core count. The result is faster
Tomek Links resampling during TabNet's cross-validation folds. The
change affects only your local copy of `src/utils.py`. It does not
need to be committed, and it does not affect anyone else's runs.

If you do not change it, the default of eight is used and the pipeline
still works correctly. The only effect is a modest increase in
training wall time.

**Sprint report name:**
`docs/reports/role-5-phase-1-dwayne-onboarding.md`

---

## Phase 2: TabNet Execution

**Documents to reference:**
- `docs/contracts/role-5-training-execution-spec.md` — authoritative execution contract, sections 3 through 15
- `src/models.py` — the frozen model code
- `notebooks/02_Model_Training.ipynb` — the notebook Dwayne runs
- `data/processed/split_indices.json` — the frozen split
- `docs/reports/role-1-phase-3-kit-model-architecture.md` section 5.2 — TabNet configuration and rationale

- **Dependencies:** Phase 1 complete. Data present in
  `data/processed/`. Notebook 02 present.
- **Contract:** `docs/contracts/role-5-training-execution-spec.md`.
- **Target Files:** `notebooks/02_Model_Training.ipynb`, Cells 9 and 10.
- **Instructions:**
  1. Follow the pre-run checklist in section 15 of the contract.
  2. Run Cell 9 (TabNet tuning). Estimated wall time: 6 to 8 hours.
  3. Run Cell 10 (TabNet save).
  4. Verify outputs per section 9 of the contract.
  5. Post the TabNet summary block per section 10 in the team channel.
- **Handoff:** Notify Kit that the TabNet artifacts are on disk.

**Sprint report name:**
`docs/reports/role-5-phase-2-dwayne-tabnet-execution.md`

---

## Phase 3: Evaluation Suite

**Documents to reference:**
- `docs/reports/paper_structure.md` section VI — the exact figure and table inventory for this phase
- `docs/reports/paper_narrative_context.md` section 13 — source pointer index
- `docs/reports/role-1-phase-3-kit-model-architecture.md` section 7 — metrics definitions
- `data/processed/X_test.npy`, `data/processed/y_test.npy` — the frozen test set
- `data/processed/feature_names.json` — feature ordering for plots
- `data/processed/class_order.json` — class ordering for confusion matrix labels
- `models/rf_baseline.joblib` — Random Forest
- `models/xgb_optuna.joblib` — XGBoost
- `models/tabnet_best.zip` — TabNet
- `notebooks/03_Evaluation_and_XAI.ipynb` — the notebook Dwayne runs

- **Dependencies:** All three models trained.
  `models/rf_baseline.joblib` from Amber.
  `models/xgb_optuna.joblib` from Kenneth.
  `models/tabnet_best.zip` from Phase 2.
- **Target Files:** `notebooks/03_Evaluation_and_XAI.ipynb`,
  `outputs/03_evaluation/*`.
- **Instructions:**
  1. Load the frozen test set from `data/processed/X_test.npy` and
     `data/processed/y_test.npy`. Do not re-split.
  2. For each model, compute predictions and generate a confusion
     matrix. Save to
     `outputs/03_evaluation/confusion_matrix_<model>.png`.
  3. Compute per-class precision, recall, and F1. Save to
     `outputs/03_evaluation/per_class_metrics.csv` and
     `outputs/03_evaluation/per_class_metrics_normalized.csv`.
  4. Generate precision-recall curves for the U2R and R2L classes.
     Save to `outputs/03_evaluation/pr_curve_u2r.png` and
     `outputs/03_evaluation/pr_curve_r2l.png`.
  5. Compute the comparison figure summarizing Macro F1 across the
     three models. Save to
     `outputs/03_evaluation/model_comparison_visual.png`.
- **Handoff:** Notify Markie that evaluation figures are ready for the
  paper.

**Sprint report name:**
`docs/reports/role-5-phase-3-dwayne-evaluation-suite.md`

---

## Phase 4: Explainability Outputs

**Documents to reference:**
- `docs/reports/paper_structure.md` section VI — figure inventory
- `docs/reports/paper_narrative_context.md` section 9 — explainability approach
- `models/rf_baseline.joblib`, `models/xgb_optuna.joblib`, `models/tabnet_best.zip` — the models to explain
- `data/processed/X_test.npy` — the test data for SHAP computation
- `data/processed/feature_names.json` — feature labels for plots

- **Dependencies:** Phase 3 complete.
- **Target Files:** `outputs/03_evaluation/shap_*.png`,
  `outputs/03_evaluation/tabnet_attention_mask.png`.
- **Instructions:**
  1. Use `shap.TreeExplainer` to compute SHAP values for Random Forest
     and XGBoost on the test set.
  2. Generate a global SHAP summary plot per tree model. Save to
     `shap_summary_rf.png` and `shap_summary_xgb.png`.
  3. Pick one high-confidence prediction for a U2R or R2L packet and
     generate a local SHAP waterfall plot. Save to
     `shap_local_example.png`.
  4. Extract TabNet's attention masks and produce a feature-importance
     visualization. Save to `tabnet_attention_mask.png`.
- **Handoff:** Notify Markie that XAI figures are ready.

**Sprint report name:**
`docs/reports/role-5-phase-4-dwayne-explainability.md`

---

## Phase 5: Paper Contribution

**Documents to reference:**
- `docs/reports/paper_structure.md` — the exact target sections
- `docs/reports/paper_narrative_context.md` — framing and terminology
- `outputs/03_evaluation/*` — the figures and metrics the drafts describe

- **Dependencies:** Phases 3 and 4 complete.
- **Target Files:** Draft sections handed to Markie.
- **Instructions:**
  1. Write a 600 to 1200 word draft of the paper's "Results" section,
     covering the confusion matrices and per-class metrics.
  2. Write a 500 to 900 word draft of the "Explainability" section,
     covering SHAP findings and TabNet attention.
  3. Hand both drafts to Markie for editing and integration.
- **Handoff:** Markie integrates. Role 5 is done with paper work.

**Sprint report name:**
`docs/reports/role-5-phase-5-dwayne-paper-drafts.md`

---

## Phase 6: Presentation Segment

**Documents to reference:**
- `docs/reports/presentation_script.md` — Kenneth's script
- `docs/reports/paper.md` — the paper for on-screen references
- `outputs/03_evaluation/*` — the figures to display

- **Dependencies:** Finalization of the paper.
- **Instructions:** Present the Evaluation and Explainability segments
  during the final video recording. Coordinate with Kenneth for
  scheduling.

**Sprint report name:**
`docs/reports/role-5-phase-6-dwayne-presentation.md`
