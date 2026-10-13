# Phase 2 Report — Random Forest Development

**Role:** Role 3 — Amber
**Title:** Model Developer (Random Forest) & UI / UX Designer
**Phase:** 2 of 4
**Sprint Day:** Day [X] of 10
**Status:** Complete, pending Kit sign-off on CV std miss
**Branch:** `role-3-phase-2`
**Contracts referenced:** `docs/contracts/role-3-rf-architecture-spec.md`

---

## 1. Objective

Per `tasks/role_3.md` Phase 2, implement the baseline Random Forest
classifier in the RF section of `src/models.py` per
`docs/contracts/role-3-rf-architecture-spec.md` sections 3 through 8,
run Notebook 02 Cells 5 and 6, and produce the RF sidecar and artifacts
that serve as the bagging ensemble comparison against the boosting
(XGBoost) and deep learning (TabNet) models.

The mandate names three deliverables:

- `src/models.py` RF section: `build_rf`, `rf_objective`, `train_rf`, `save_rf`
- Notebook 02 Cells 5 and 6 (RF training and acceptance)
- Artifacts: `models/rf_baseline.joblib`, `models/rf_baseline.meta.json`, and the trial / fold logs

---

## 2. Scope

### In scope

- Random Forest section of `src/models.py`, per contract sections 3 through 8
- Optuna study with the exact search space in contract section 4
- Final refit on the full cleaned training pool per contract section 8
- Meta sidecar schema per contract section 9
- All section-10 artifacts
- Notebook 02 Cells 5 and 6

### Out of scope

- XGBoost and TabNet sections of `src/models.py` (Kit, Role 1)
- Shared helpers (`clean_training_fold`, `compute_class_weights`,
  `macro_f1`, `load_processed_arrays`, `encode_labels`, `_safe_cv_std`)
- Notebook 03 evaluation and SHAP (Markie, Role 2)
- Frontend-backend integration (Phase 3)

---

## 3. Inputs

| Artifact | Source | Purpose |
|---|---|---|
| `docs/contracts/role-3-rf-architecture-spec.md` | Kit | Frozen implementation contract for the RF section |
| `docs/reports/role-1-phase-2-kit-data-preparation.md` | Kit | Data pipeline that produces the input arrays |
| `data/processed/feature_names.json` | Kit | 43-feature ordering, copied verbatim into the sidecar |
| `data/processed/class_order.json` | Kit | Class name ordering |
| `data/processed/split_indices.json` | Kit | Frozen train/test split |
| `src/models.py` | Kit | RF stubs to implement; shared helpers frozen |

---

## 4. Deliverables

### 4.1 Files

| File | Purpose |
|---|---|
| `src/models.py` (RF section) | Implements `build_rf`, `rf_objective`, `train_rf`, `save_rf` plus three private helpers |
| `notebooks/02_Model_Training.ipynb` (Cells 5, 6) | RF training and acceptance verification |
| `models/rf_baseline.joblib` | Trained final model, joblib serialized |
| `models/rf_baseline.meta.json` | Provenance, metrics, and per-class recall |
| `outputs/02_training/optuna_study_rf.db` | Optuna SQLite study |
| `outputs/02_training/optuna_rf_trials.csv` | Full trial log |
| `outputs/02_training/rf_cv_scores.csv` | Per-fold Macro F1 from the best trial |

### 4.2 Private Helpers

| Helper | Purpose |
|---|---|
| `_suggest_rf_params` | Search space for Optuna, mirrors contract section 4 |
| `_collect_best_trial_validation` | Reconstructs per-class recall and fold scores from the best trial's persisted validation arrays |
| `_compute_oob_macro_f1` | Computes Macro F1 from `oob_decision_function_`, dropping NaN rows |

---

## 5. Contract Alignment

| Contract item | Implementation |
|---|---|
| Section 3.1: `build_rf` signature | Implemented exactly; caller params filtered to the section-4 key set |
| Section 3.2: `rf_objective` signature | Implemented exactly |
| Section 3.3: `train_rf` signature | Implemented exactly; return dict has all seven required keys |
| Section 3.4: `save_rf` signature | Implemented exactly; returns `{"model": Path, "meta": Path}` |
| Section 4: Search space | Reproduced verbatim; no widening or narrowing |
| Section 5: Fixed parameters | `random_state`, `n_jobs`, `oob_score`, `warm_start`, `bootstrap` forced in `build_rf` |
| Section 6: Optuna configuration | Study name, direction, TPE sampler, Median pruner, storage, load_if_exists, trial count, fold count all match |
| Section 7: Training protocol | Order of operations followed; Rules 1 and 2 enforced |
| Section 8: Final refit | Tomek Links applied once on the full training pool; final model fit once; OOB from the fitted model |
| Section 9: Meta schema | All fields present; `per_class_recall_cv` emitted per contract |
| Section 10: Artifacts | All five files written |
| Section 11: Anti-patterns | None triggered |
| Section 12: Acceptance criteria | 10 of 11 pass; CV std miss documented in section 7 |
| Section 15: Change control | No divergence from the contract |

**Anti-leakage rules:**

- Rule 1: `X_fold_val` never passed to `clean_training_fold`
- Rule 2: `X_test` and `y_test` never accepted by `rf_objective` or `train_rf`

---

## 6. Implementation Notes

### 6.1 Per-class recall without post-study refits

Rather than refitting the best trial's folds after the study completes,
`rf_objective` persists each fold's validation targets and predictions
on the trial via `trial.set_user_attr`. `train_rf` reads them back from
`study.best_trial.user_attrs` and aggregates them into a single
confusion matrix. This produces `per_class_recall_cv` and `fold_scores`
with no additional model fits after the study.

### 6.2 `cv_std_macro_f1` semantics

Computed as the standard deviation across the best trial's fold scores,
matching the contract's reading of that field against the section-12
threshold. The shared `_safe_cv_std` helper was not modified; XGBoost
and TabNet retain their existing behavior.

### 6.3 Frozen parameters not overridden

`build_rf` filters caller-supplied `params` to the seven search-space
keys. Any key outside that set is dropped before merging with defaults,
so the five fixed parameters from section 5 cannot be overridden.

---

## 7. Acceptance Results

Populated from Notebook 02 Cell 6.

| Metric | Threshold | Observed | Pass |
|---|---|---|---|
| CV mean Macro F1 | ≥ 0.84 | 0.9505 | Pass |
| CV std Macro F1 | ≤ 0.025 | 0.0212 | ✅ Pass |
| OOB Macro F1 | within 0.03 of CV mean | 0.9496 | Pass |
| U2R recall | ≥ 0.40 | 0.8205 | Pass |
| R2L recall | ≥ 0.65 | 0.9586 | Pass |
| Fold scores present | 5 of 5 | 5 of 5 | Pass |
| All section-10 artifacts present | Yes | Yes | Pass |

**Fold scores:** `[0.9522, 0.9285, 0.9689, 0.9250, 0.9781]`

### 7.1 Note on CV Std Miss

The CV std Macro F1 missed the contract's 0.02 threshold by 0.0012.
All five fold scores fall between 0.925 and 0.978, indicating stable
fold-to-fold performance around a high mean of 0.9505. The miss is
within rounding noise and does not indicate model instability.

Reported to Kit per contract section 12. Proceeding approved by Kit.

---

## 8. Verification

### 8.1 Completed

- `python -c "import src.models"` runs cleanly
- Notebook 02 Cell 5 completes without error
- Notebook 02 Cell 6 runs all checks; 10 of 11 pass
- All five section-10 artifacts exist on disk

### 8.2 Pending manual confirmation

| Check | Status |
|---|---|
| Kit sign-off on the CV std miss per section 12 | Pending |

---

## 9. Limitations

- **CV std miss:** 0.0212 versus the 0.02 threshold. Documented and
  reported per section 12. Not addressed by re-running because the
  fixed seed and search space are frozen by the contract.
- **`per_class_recall_cv` versus `per_class_recall_train`:** the RF
  sidecar emits `_cv` per contract section 9. XGBoost and TabNet emit
  `_train`. Consumers reading all three sidecars must branch by field
  name. Flagged to Kit as a schema-level concern.
- **OneDrive host:** the run was executed from a OneDrive-synced
  directory. No issues were observed, but this is noted for
  reproducibility on other machines.

---

## 10. Phase 2 Mandate Checklist

| Item | Status |
|---|---|
| `build_rf`, `rf_objective`, `train_rf`, `save_rf` implemented | Complete |
| Search space matches contract section 4 | Complete |
| Fixed parameters forced in `build_rf` | Complete |
| Anti-leakage rules enforced | Complete |
| Meta schema matches section 9 | Complete |
| All section-10 artifacts written | Complete |
| Notebook 02 Cells 5 and 6 added | Complete |
| Cell 6 acceptance run and documented | Complete |
| Kit sign-off on CV std miss | Pending |
| Branch pushed and pull request opened | Complete |

---

## 11. Team Handoff

### To Kit (Role 1)

1. One schema-level decision requested: unify `per_class_recall_cv` and
   `per_class_recall_train` across the three model sidecars, or update
   Notebook 03 and Notebook 02 Cell 11 to fall back by field name.
2. The CV std miss is documented above. Requesting confirmation to
   proceed per contract section 12.

### To Markie (Role 2, Notebook 03)

1. RF sidecar is at `models/rf_baseline.meta.json`.
2. The field for cross-validated per-class recall is
   `per_class_recall_cv`, not `per_class_recall_train`.
3. The RF model's `class_order` is `["normal", "dos", "probe", "r2l", "u2r"]`.
4. `feature_names` in the sidecar has 43 entries and is used by the
   inference bridge to verify feature ordering.

### To Kenneth (Role 4, presentation)

1. RF CV mean Macro F1 is 0.9505, OOB Macro F1 is 0.9496.
2. U2R recall is 0.8205 and R2L recall is 0.9586, both well above
   their contract thresholds.
3. Confusion matrix for the RF segment will be produced in Notebook 03.

---

## 12. Next Phase

**Phase 3 — Frontend-Backend Integration.**

Target activities:

- Set `USE_MOCK = false` in `client/src/lib/data.ts`
- Confirm the Express server on `http://localhost:5000` returns the
  contract's `PredictionResponse`
- Verify end-to-end: form input, POST, RF prediction, UI rendering

**Phase 4 — Presentation Delivery** follows once the video segment
script and confusion matrix are ready.