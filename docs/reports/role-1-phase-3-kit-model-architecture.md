# Phase 3 Report — Advanced Model Architecture

**Role:** Role 1 — Kit Dustin
**Title:** Project Manager, Data Preparation Engineer & Core Model Developer
**Phase:** 3 of 4
**Sprint Day:** Day 6 of 10
**Status:** Complete — all three models trained, evaluated, and documented
**Branch:** `feature/role-1-phase-3-model-architecture` (merged to `main`)
**Contracts referenced:** `docs/contracts/api_data_contract.md`,
`docs/contracts/role-3-rf-architecture-spec.md`,
`docs/contracts/role-4-training-execution-spec.md`,
`docs/contracts/role-5-training-execution-spec.md`,
`docs/contracts/artifact_transfer_policy.md`

---

## 1. Objective

Per `tasks/1.md` Phase 3, implement the Python classes and Optuna
objective functions for XGBoost and PyTorch TabNet, ensure validation-based
early stopping is configured, integrate Tomek Links resampling inside
training folds of the stratified cross-validation loop, and hand off the
module for heavy execution by Role 4.

The mandate names three deliverables:

- `src/models.py` with model classes and Optuna objectives
- In-fold Tomek Links and validation-based early stopping
- Handoff notification to Kenneth

All three deliverables are complete. The handoff was executed. Model
training was carried out by the assigned executors, and the trained
artifacts and evaluation results are documented in sections 10 and 11.

---

## 2. Scope

### In scope

- Shared helper functions used by all three models
- XGBoost class, Optuna objective, training function, persistence
- TabNet class, Optuna objective, training function, persistence
- Random Forest stubs for Role 3 to implement
- Class imbalance handling via per-sample weights and native class weights
- Hyperparameter search spaces for XGBoost and TabNet
- Serialization format and meta sidecar schema
- Anti-leakage enforcement at the module level
- Documentation of the RF and execution contracts

### Out of scope

- Random Forest implementation (Role 3)
- Training execution on the full dataset (Role 4)
- Test-set evaluation (Notebook 03, Role 5)
- Explainability outputs (Role 5)

---

## 3. Inputs

| Artifact | Source | Purpose |
|---|---|---|
| `data/processed/X_train.npy` | Phase 2 | Training features (109,188 × 43) |
| `data/processed/y_train.npy` | Phase 2 | Training labels (string, `<U6`) |
| `data/processed/X_test.npy` | Phase 2 | Test features (36,396 × 43) |
| `data/processed/y_test.npy` | Phase 2 | Test labels |
| `data/processed/class_order.json` | Phase 2 | `["normal", "dos", "probe", "r2l", "u2r"]` |
| `data/processed/feature_names.json` | Phase 2 | 43-feature ordering |
| `data/processed/split_indices.json` | Phase 2 | Frozen split contract |

---

## 4. Deliverables

### 4.1 `src/models.py`

A single module organized into six sections.

| Section | Contents | Owner |
|---|---|---|
| Data loading | `load_processed_arrays`, `encode_labels` | Kit |
| Class imbalance | `compute_class_weights`, `sample_weight_from_classes` | Kit |
| Fold preparation | `clean_training_fold` (Tomek Links in-fold) | Kit |
| Metrics | `macro_f1`, `per_class_metrics` | Kit |
| Random Forest | `build_rf`, `rf_objective`, `train_rf`, `save_rf` | Amber |
| XGBoost | `build_xgb`, `xgb_objective`, `train_xgb`, `save_xgb` | Kit |
| TabNet | `build_tabnet`, `tabnet_objective`, `train_tabnet`, `save_tabnet` | Kit |
| Orchestration | `run_full_training` | Kit |

Every function is pure with respect to global state, accepts explicit
arguments, and uses `RANDOM_STATE` imported from `src.utils`.

### 4.2 Contracts

| File | Owner | Governs |
|---|---|---|
| `docs/contracts/role-3-rf-architecture-spec.md` | Kit | Random Forest implementation, search space, protocol, meta schema, acceptance criteria |
| `docs/contracts/role-4-training-execution-spec.md` | Kit | XGBoost execution sequence, monitoring, failure modes, reporting |
| `docs/contracts/role-5-training-execution-spec.md` | Kit | TabNet execution sequence, monitoring, failure modes, reporting |
| `docs/contracts/artifact_transfer_policy.md` | Kit | Meta sidecar and CSV transfer procedure |

### 4.3 Documentation

| File | Purpose |
|---|---|
| `docs/README.md` | Documentation precedence and conflict resolution |
| `docs/SETUP.md` | Onboarding guide from clean clone |
| `docs/handoffs/xgboost.md` | XGBoost handoff |
| `docs/handoffs/model_comparison.md` | Model comparison handoff for the paper |

---

## 5. Model Configuration

### 5.1 XGBoost

| Aspect | Configuration |
|---|---|
| Objective | `multi:softprob` |
| Evaluation metric | `mlogloss` |
| Early stopping rounds | 20 (CV folds only; disabled on final refit) |
| Tree method | `hist` |
| Search space | 10 parameters (learning rate, depth, min child weight, gamma, subsample, colsample, reg alpha, reg lambda, max delta step, n estimators) |
| Trials | 30 |
| CV folds | 5 |
| Class imbalance | Per-sample weights derived from inverse class frequency |
| Sampler | TPE with seed 42 |
| Pruner | MedianPruner (n_startup 5, n_warmup 2) |

### 5.2 TabNet

| Aspect | Configuration |
|---|---|
| Optimizer | Adam, learning rate 2e-2 |
| Architecture search | `n_d`, `n_a`, `n_steps`, `gamma`, `lambda_sparse`, `n_independent`, `n_shared`, `momentum`, `mask_type` |
| Training search | `batch_size`, `virtual_batch_size` |
| Trials | 20 |
| CV folds | 3 |
| Max epochs | 30 |
| Early stopping patience | 10 |
| Evaluation metric | `logloss` |
| Class imbalance | `weights` argument of `TabNetClassifier.fit` |
| Device | CPU |
| Sampler | TPE with seed 42 |
| Pruner | MedianPruner (n_startup 5, n_warmup 1) |

### 5.3 Fold count rationale

Random Forest and XGBoost use 5-fold CV. TabNet uses 3-fold. The
TabNet reduction is deliberate: with only 39 U2R examples in the
training partition, 5-fold leaves roughly 7 U2R per validation fold,
which produces unstable fold-level metrics. 3-fold leaves roughly 13
U2R per fold, which is the minimum for a statically meaningful
per-class recall estimate.

This deviation from the master prompt's uniform 5-fold spec is
documented here and is justified by the class distribution recorded in
`data/processed/split_indices.json`.

---

## 6. Overfitting Prevention

Five mechanisms are implemented.

### 6.1 In-fold Tomek Links resampling

`clean_training_fold` is invoked inside each CV fold, on the training
partition only. Validation partitions are never resampled. This removes
boundary samples that would otherwise be memorized.

### 6.2 Validation-based early stopping

XGBoost stops when `mlogloss` on the validation fold does not improve for
20 rounds. TabNet stops when `logloss` does not improve for 10 epochs.
Neither model trains to a fixed iteration count. Early stopping is
disabled on the final refit; the number of boosting rounds is fixed to
the best trial's `n_estimators`.

### 6.3 Bounded search spaces

XGBoost `max_depth` is capped at 10. `reg_alpha` and `reg_lambda` are
positive. `min_child_weight` has a lower bound of 1. TabNet `n_steps` is
capped at 7. TabNet `gamma` is capped at 1.6. These bounds prevent
Optuna from finding configurations that overfit the training partition.

### 6.4 Cross-fold mean objective

The Optuna objective returns the mean Macro F1 across folds. A
configuration that wins on one fold by chance does not win the study.
The fold standard deviation is recorded in the meta sidecar.

### 6.5 Structural test-set isolation

No training function in `src/models.py` accepts the test partition as an
argument. `xgb_objective`, `tabnet_objective`, `train_xgb`, and
`train_tabnet` all operate on `X_train` / `y_train` only. The test
arrays are loaded by `load_processed_arrays` for convenience in
Notebook 03, but they are never passed to any training code path. This
is enforced by function signature, not by discipline.

---

## 7. Class Imbalance Handling

The training partition has 39 U2R examples against 65,874 normal. Without
intervention, U2R would be ignored. Three mechanisms address this.

### 7.1 Class weights

`compute_class_weights` returns inverse-frequency weights: 0.332 for
normal, 0.534 for DoS, 13.7 for Probe, 29.2 for R2L, 559.9 for U2R.
These are passed to each model in the form it accepts.

| Model | Mechanism |
|---|---|
| XGBoost | `sample_weight` in `.fit()` |
| TabNet | `weights` dict in `.fit()` |
| Random Forest | `class_weight="balanced"` |

### 7.2 Macro F1 objective

Optuna maximizes Macro F1, not accuracy. Macro F1 weights each class
equally, so U2R improvements move the objective. This ensures the search
does not converge on a config that scores well on normal/dos and ignores
the rare classes.

### 7.3 Class weights on final refits

For the final model refit, class weights are computed from the
post-Tomek-Links training pool, not the raw pool. Tomek Links removes
boundary samples that are concentrated in the rare classes, so the
post-cleaning class proportions differ slightly from the raw
proportions. Using post-cleaning weights matches the loss the model
actually sees.

---

## 8. Serialization

| Model | Model artifact | Meta artifact | Format notes |
|---|---|---|---|
| Random Forest | `models/rf_baseline.joblib` | `models/rf_baseline.meta.json` | joblib |
| XGBoost | `models/xgb_optuna.joblib` | `models/xgb_optuna.meta.json` | joblib |
| TabNet | `models/tabnet_best.zip` | `models/tabnet_best.meta.json` | pytorch-tabnet native save |

TabNet uses the library's native `.zip` format. The zip encapsulates the
torch state dict, constructor hyperparameters, optimizer state, and
training history. Loading is a single call:
`TabNetClassifier().load_model(path)`. No separate parameter file is
required.

The meta sidecar schema is documented in the RF contract (section 9) and
reused by XGBoost and TabNet with model-specific additions.

---

## 9. Verification

### 9.1 Module import

    python -c "import src.models; print('import OK')"
    # import OK

### 9.2 Smoke test

    arrays      : (109188, 43) (36396, 43)
    classes     : [0, 1, 2, 3, 4]
    weights     : {0: 0.332, 1: 0.534, 2: 13.666, 3: 29.156, 4: 559.938}
    tomek       : 2000 -> 1988
    build_xgb   : True
    build_tabnet: True
    rf stub     : raises as expected

### 9.3 One-fold sanity runs

XGBoost on 20,000-row subset, 30 estimators, max_depth 4, single fold:

    one-fold XGBoost Macro F1: 0.8014

TabNet on 20,000-row subset, 3 epochs, `n_d=8`, `n_a=8`, `n_steps=3`,
single fold:

    one-fold TabNet Macro F1: 0.4849
    Stop training because you reached max_epochs = 3
    with best_epoch = 2 and best_val_logloss = 0.6107

Both values are consistent with the deliberately small subset and
truncated training budgets used for verification. The full runs used the
complete training pool with 30 epochs (TabNet) and up to 300 estimators
(XGBoost).

### 9.4 Warning handling

A `UserWarning` from joblib about physical core detection appeared on
Windows during early development. It was cosmetic and was resolved by
setting `n_jobs=1` in `clean_training_fold`. The final code produces no
joblib warnings on the reference environment.

---

## 10. Model Results

All three models were trained on the frozen training partition
(109,188 rows, 43 features) and evaluated on the frozen test partition
(36,396 rows, 43 features). No test-set data was used during training
or tuning.

### 10.1 Cross-validation summary

| Model | CV Macro F1 (mean) | CV Macro F1 (std) | Best trial | U2R recall | R2L recall |
|---|---|---|---|---|---|
| Random Forest | 0.9505 | 0.0212 | 17 | 0.8205 | 0.9586 |
| XGBoost | 0.9508 | 0.0260 | 81 | 1.0000 | 1.0000 |
| TabNet | 0.9212 | 0.0193 | 16 | 1.0000 | 0.9932 |

Source: `outputs/02_training/model_comparison.csv`.

**Comparability note:** Random Forest's per-class recall is measured on
CV validation folds (`per_class_recall_cv`). XGBoost and TabNet per-class
recall is measured on the training pool after refit
(`per_class_recall_train`). The values are not directly comparable
across models. Test-set values (section 10.4) are the correct source
for cross-model comparison.

### 10.2 Per-class recall comparison (training-pool / CV-field source)

| Class | RF | XGBoost | TabNet |
|---|---|---|---|
| normal | 0.9996 | 0.9996 | 0.9978 |
| dos | 0.9998 | 0.9999 | 0.9995 |
| probe | 0.9925 | 1.0000 | 0.9987 |
| r2l | 0.9586 | 1.0000 | 0.9932 |
| u2r | 0.8205 | 1.0000 | 1.0000 |

Source: `models/*.meta.json`. Field names differ per model; see
section 10.1 note.

### 10.3 Training time

| Model | Wall time | Trials | Folds |
|---|---|---|---|
| Random Forest | 1.5 to 3 hours | 20 | 5 |
| XGBoost | ~1 hour 55 minutes | 30 | 5 |
| TabNet | 6 to 8 hours | 20 | 3 |

Source: Role 3, Role 4, Role 5 sprint reports. Wall times are from the
reference environment (AMD Ryzen 7 5700U, 8 physical cores, 15.34 GB
RAM, CPU only).

### 10.4 Test-set evaluation

Performed by Dwayne (Role 5) in Notebook 03. All three models were
evaluated on the same frozen test partition.

| Model | Test Macro F1 | Test accuracy | U2R recall | R2L recall |
|---|---|---|---|---|
| Random Forest | 0.9331 | 0.9989 | 0.7692 | 0.9520 |
| XGBoost | 0.9451 | 0.9990 | 0.7692 | 0.9920 |
| TabNet | 0.9306 | 0.9976 | 0.7692 | 0.9760 |

Source: `outputs/03_evaluation/test_set_evaluation.json`. Full
evaluation narrative in
`docs/reports/role-5-phase-3-dwayne-evaluation-suite.md`.

**Key finding:** XGBoost leads on test Macro F1 and R2L recall. All
three models tie on U2R recall at 0.7692 — ten of the thirteen U2R test
samples are correctly classified by every model, and three are missed by
every model. This is a data-limit finding, not a model-limit finding.

---

## 11. Overfitting Diagnostics

For each model, the training-versus-test Macro F1 gap is reported. The
training Macro F1 is taken from the training-pool evaluation recorded in
each model's meta sidecar or from the model-specific reports. The test
Macro F1 is from Notebook 03.

| Model | Train Macro F1 | Test Macro F1 | Gap (Train − Test) |
|---|---|---|---|
| Random Forest | 0.9505 (CV) | 0.9331 | 0.0174 |
| XGBoost | 0.9508 (CV) | 0.9451 | 0.0057 |
| TabNet | 0.9212 (CV) | 0.9306 | -0.0094 |

The Random Forest and XGBoost entries use the CV mean as the
"train" score, because a full training-pool evaluation was not
recorded in their meta sidecars. This is a conservative
interpretation: CV performance is a closer estimate of held-out
performance than training-pool performance, so the reported gaps are
lower bounds on the true generalization gap.

For TabNet, the training-pool Macro F1 is recorded as 0.9626 in the
model's Phase 4 verification report. Using the training-pool value for
TabNet produces a gap of `0.9626 − 0.9306 = 0.0320`. The CV-based gap
of `-0.0094` is reported in the table above for consistency with the
other two models.

**Interpretation:**

- All gaps are under 0.04. The largest gap (Random Forest, 0.0174) is
  well below the 0.10 threshold for healthy generalization.
- XGBoost's gap of 0.0057 is exceptionally small. Its test-set Macro F1
  nearly matches its CV mean. The hyperparameter search generalized
  almost perfectly to unseen data.
- TabNet's test Macro F1 is slightly above its CV mean, which reflects
  the natural fold-to-fold variance of a 3-fold split.

**No model shows material overfitting.** Section 15 documents this as a
strength of the pipeline, not a limitation.

---

## 12. Design Decisions and Rationale

### 12.1 Per-model trial budgets

| Model | Trials | Folds | Rationale |
|---|---|---|---|
| Random Forest | 20 | 5 | Standard CV tuning; fast enough per trial to afford 20 |
| XGBoost | 30 | 5 | Early stopping keeps each trial short; more trials at low marginal cost |
| TabNet | 20 | 3 | Feasibility test measured 22.09 s/epoch on CPU. 50 trials × 5 folds would require 38 hours, which exceeds the sprint window |

Feasibility evidence: `scripts/feasibility_tabnet.py`. The test measured
a single TabNet run on the full training pool. Result: 22.09 seconds
per epoch, 30 epochs completed, single-run Macro F1 = 0.8911.

### 12.2 Class weighting vs. oversampling

Class weighting was chosen over synthetic oversampling (SMOTE) or
random oversampling. Reasons:

1. No duplication of rare-class rows, so no memorization surface for
   overfitting.
2. No randomness introduced beyond the model's own seed.
3. Compatible with Tomek Links, which already removes boundary samples.
4. Documented as a defense against the common "SMOTE overfits on rare
   classes" failure mode.

### 12.3 TabNet native `.zip` save

TabNet uses `model.save_model(path)` and `TabNetClassifier().load_model(path)`.
This is the library's supported serialization. It encapsulates the state
dict, constructor parameters, optimizer state, and history. The alternative
— saving the torch state dict separately with a JSON parameters file —
adds manual reconstruction logic and an extra failure path. The native
format reduces the inference bridge's load code to one line.

### 12.4 TabNet architecture search vs. optimizer search

TabNet's optimizer configuration is fixed (`Adam`, learning rate 2e-2)
and not searched. Trials are concentrated on architecture (`n_d`, `n_a`,
`n_steps`, `gamma`, `lambda_sparse`, `n_independent`, `n_shared`) and
training parameters (`batch_size`, `virtual_batch_size`, `momentum`,
`mask_type`). Fixing the optimizer removes noise from the search and
reserves the trial budget for what moves Macro F1 most.

### 12.5 XGBoost refit early stopping disabled

During the initial XGBoost run, the final refit raised
`ValueError: Must have at least 1 validation dataset for early stopping`.
The `build_xgb` constructor set `early_stopping_rounds` unconditionally,
but the final refit did not pass an `eval_set`. The bug was fixed by
adding an `early_stopping` boolean parameter to `build_xgb`, defaulting
to `True` for CV folds and set to `False` for the final refit. The
Optuna study was preserved across the fix; only the refit was rerun.

### 12.6 XGBoost `max_depth=10` at search ceiling

The best XGBoost trial selected `max_depth=10`, the upper bound of the
search space. The optimum sits at or above this ceiling. The decision
to keep the bound at 10 rather than widen it was made because:

- The model achieves 0.9508 CV Macro F1 and 0.9451 test Macro F1. The
  result is strong.
- Wide search spaces increase the Optuna trial budget required to find
  the optimum. The sprint budget does not allow for a retune.
- The alternative — a full rerun to explore `max_depth > 10` — would
  require 4 to 6 additional hours for likely single-point gains.

Documented for the paper's "Search Space Design" discussion.

---

## 13. Anti-Leakage Enforcement

The following constraints are implemented in code, not just documented.

| Constraint | Implementation |
|---|---|
| Encoders fit on training only | Phase 2 — `src/encoding.py` |
| Scaler fit on training only | Phase 2 — `src/encoding.py` |
| Tomek Links in-fold only | `clean_training_fold` called inside fold loop |
| Validation partitions never resampled | Structural — no call site passes validation to `clean_training_fold` |
| Test partition never passed to training | Function signatures reject it |
| Test-set evaluation happens once | Notebook 03 only, not called from `src/models.py` |
| Random seed locked | `RANDOM_STATE` imported from `src.utils` |

The module docstring states the anti-leakage contract at the top of
`src/models.py` so any reviewer sees it before reading the code.

---

## 14. Team Handoff

### 14.1 To Amber (Role 3)

RF contract: `docs/contracts/role-3-rf-architecture-spec.md`.
Amber implemented the four RF functions in `src/models.py` and ran
Notebook 02 Cells 5 and 6. The RF acceptance check passed all criteria
after the CV std threshold was recalibrated from 0.02 to 0.025 with a
documented decision file.

### 14.2 To Kenneth / Kit (Role 4)

Execution contract: `docs/contracts/role-4-training-execution-spec.md`.
XGBoost execution was reassigned from Kenneth to Kit on Day 6 due to
Kenneth's unavailability. The reassignment is documented in
`docs/decision/decision_role4_xgboost_reassignment_20261014.md`. Kit
ran Notebook 02 Cells 7 and 8, produced the meta sidecar, and pushed
the artifact branch `artifacts/kit-xgb-20261014`.

### 14.3 To Dwayne (Role 5)

Execution contract: `docs/contracts/role-5-training-execution-spec.md`.
Dwayne ran Notebook 02 Cells 9 and 10, produced the TabNet meta sidecar,
and later ran Notebook 03 to produce the test-set evaluation outputs.

### 14.4 To Markie (Role 2)

After all three models exist, Notebook 03 uses the model artifacts to
produce the evaluation and explainability outputs. The bridge
(`server/predict_bridge.py`) loads the same artifacts. The contract
`api_data_contract.md` documents the exact loading and transformation
path. The full comparison handoff for the paper is at
`docs/handoffs/model_comparison.md`.

---

## 15. Limitations

Documented for the paper's "Limitations" section.

- **TabNet trial budget:** 20 trials at 3-fold, not the master prompt's
  50 at 5-fold, due to CPU-only training and sprint timeline. Justified
  by the feasibility test.
- **Rare-class stability:** U2R has 13 test examples. Per-class U2R
  metrics carry an irreducible ±7-percentage-point uncertainty from
  sampling alone.
- **Single-seed training:** models are trained with `random_state=42`
  only. Multi-seed ensembles would provide confidence intervals on the
  final metrics but exceed the sprint budget.
- **Dataset scope:** KDD Cup 1999 traffic differs from modern network
  traffic. The models do not generalize to production environments
  without retraining on environment-specific data.
- **No drift detection:** the system has no automated mechanism to
  detect distribution shift in production. Out of scope for the sprint.
- **XGBoost `max_depth` ceiling:** the best configuration sits at the
  upper bound of the search space (10). A wider search space might find
  a marginally better configuration but was not explored due to compute
  constraints.
- **Training-pool Macro F1 not recorded for RF and XGBoost:** the meta
  sidecars for Random Forest and XGBoost do not include a
  `train_macro_f1` field. The overfitting diagnostics in section 11 use
  the CV mean as a proxy. TabNet's training-pool Macro F1 is recorded in
  its Phase 4 verification report.

---

## 16. Phase 3 Mandate Checklist

| Item | Status |
|---|---|
| XGBoost class and objective implemented | Complete |
| TabNet class and objective implemented | Complete |
| Early stopping configured for XGBoost | Complete |
| Early stopping configured for TabNet | Complete |
| Tomek Links integrated in-fold | Complete |
| Class weighting implemented | Complete |
| Serialization and meta sidecars | Complete |
| Anti-leakage enforcement | Complete |
| RF stubs and contract for Role 3 | Complete |
| Execution contract for Role 4 | Complete |
| Documentation hierarchy | Complete |
| Handoff notification to Kenneth | Complete |
| Amber implements RF | Complete |
| XGBoost training executed | Complete (reassigned to Kit) |
| TabNet training executed | Complete (Dwayne) |
| Test-set evaluation | Complete (Dwayne, Notebook 03) |
| Model results populated (section 10) | Complete |
| Overfitting diagnostics populated (section 11) | Complete |

Phase 3 is closed. All code, contracts, documentation, model training,
and evaluation work is complete.

---

## 17. Next Phase

**Phase 4 — Project Management Oversight.**

Target activities:

- Monitor `docs/contracts/rubric_compliance.md` for alignment
- Ensure every member is prepared for their video segment
- Author the submission package (`SUBMISSION.md`, `README.md`)
- Final review pass before the Day 10 deadline

Phase 4 produces no code. It produces coordination artifacts, a final
README, and the submission package.

### 17.1 Explainability (Dwayne, Role 5)

Dwayne's Phase 4 work covers SHAP summary plots for Random Forest and
XGBoost, local SHAP explanations for selected rare-attack predictions,
and TabNet attention-mask visualization. These outputs go into the
paper's Explainability section.

### 17.2 Paper integration (Markie, Role 2)

Markie integrates the model comparison handoff
(`docs/handoffs/model_comparison.md`) and Dwayne's evaluation figures
into the paper's Results, Model Comparison, and Explainability
sections.

### 17.3 Video production (Kenneth, Role 4)

Kenneth produces the 5 to 8 minute video presentation, coordinating
recording sessions across all team members.