# Phase 3 Report — Advanced Model Architecture

**Role:** Role 1 — Kit Dustin
**Title:** Project Manager, Data Preparation Engineer & Core Model Developer
**Phase:** 3 of 4
**Sprint Day:** Day 3 of 10
**Status:** In progress — code complete, model training pending teammate handoffs
**Branch:** `feature/role-1-phase-3-model-architecture`
**Contracts referenced:** `docs/contracts/api_data_contract.md`,
`docs/contracts/role-3-rf-architecture-spec.md`,
`docs/contracts/role-4-training-execution-spec.md`

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
- Test-set evaluation (Notebook 03, Role 2)
- Explainability outputs (Role 2)

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
| Random Forest | `build_rf`, `rf_objective`, `train_rf`, `save_rf` | Amber (stubs) |
| XGBoost | `build_xgb`, `xgb_objective`, `train_xgb`, `save_xgb` | Kit |
| TabNet | `build_tabnet`, `tabnet_objective`, `train_tabnet`, `save_tabnet` | Kit |
| Orchestration | `run_full_training` | Kit |

Every function is pure with respect to global state, accepts explicit
arguments, and uses `RANDOM_STATE` imported from `src.utils`.

### 4.2 Contracts

| File | Owner | Governs |
|---|---|---|
| `docs/contracts/role-3-rf-architecture-spec.md` | Kit | Random Forest implementation, search space, protocol, meta schema, acceptance criteria |
| `docs/contracts/role-4-training-execution-spec.md` | Kit | Execution sequence, monitoring, failure modes, reporting |

### 4.3 Documentation

| File | Purpose |
|---|---|
| `docs/README.md` | Documentation precedence and conflict resolution |

---

## 5. Model Configuration

### 5.1 XGBoost

| Aspect | Configuration |
|---|---|
| Objective | `multi:softprob` |
| Evaluation metric | `mlogloss` |
| Early stopping rounds | 20 |
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
Neither model trains to a fixed iteration count.

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
| Random Forest | `class_weight="balanced_subsample"` (Role 3) |

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
truncated training budgets used for verification. The full runs use the
complete training pool and 30 epochs (TabNet) / 300 estimators
(XGBoost).

### 9.4 Warning handling

A `UserWarning` from joblib about physical core detection appears on
Windows. It is cosmetic. It does not affect results and does not require
intervention. Documented in the execution contract (section 9).

---

## 10. Model Results

**Status:** pending. This section is filled from the artifacts produced
by Role 3 (Random Forest) and Role 4 (XGBoost, TabNet) training runs.

### 10.1 Cross-validation summary

| Model | CV Macro F1 (mean) | CV Macro F1 (std) | Best trial | U2R recall | R2L recall |
|---|---|---|---|---|---|
| Random Forest | <RF_CV_MEAN> | <RF_CV_STD> | <RF_TRIAL> | <RF_U2R> | <RF_R2L> |
| XGBoost | <XGB_CV_MEAN> | <XGB_CV_STD> | <XGB_TRIAL> | <XGB_U2R> | <XGB_R2L> |
| TabNet | <TAB_CV_MEAN> | <TAB_CV_STD> | <TAB_TRIAL> | <TAB_U2R> | <TAB_R2L> |

Source: `outputs/02_training/model_comparison.csv`.

### 10.2 Per-class recall comparison

| Class | RF | XGBoost | TabNet |
|---|---|---|---|
| normal | <RF_NORMAL> | <XGB_NORMAL> | <TAB_NORMAL> |
| dos | <RF_DOS> | <XGB_DOS> | <TAB_DOS> |
| probe | <RF_PROBE> | <XGB_PROBE> | <TAB_PROBE> |
| r2l | <RF_R2L> | <XGB_R2L> | <TAB_R2L> |
| u2r | <RF_U2R> | <XGB_U2R> | <TAB_U2R> |

Source: `models/*.meta.json`, `per_class_recall_cv` field.

### 10.3 Training time

| Model | Wall time | Trials | Folds |
|---|---|---|---|
| Random Forest | <RF_TIME> | 20 | 5 |
| XGBoost | <XGB_TIME> | 30 | 5 |
| TabNet | <TAB_TIME> | 20 | 3 |

Source: execution reports from Role 4 and Role 3.

---

## 11. Overfitting Diagnostics

**Status:** pending final results.

For each model, the training-versus-validation Macro F1 gap is reported.

| Model | Train Macro F1 | Validation Macro F1 | Gap |
|---|---|---|---|
| Random Forest | <RF_TRAIN> | <RF_VAL> | <RF_GAP> |
| XGBoost | <XGB_TRAIN> | <XGB_VAL> | <XGB_GAP> |
| TabNet | <TAB_TRAIN> | <TAB_VAL> | <TAB_GAP> |

A gap under 0.10 is healthy. Above 0.15 indicates material overfitting
and the model would need to be retrained with tighter regularization.

If any gap exceeds 0.15, this is documented in section 15 as a
limitation.

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
Amber implements the four RF functions in `src/models.py` and runs
Notebook 02 Cells 5 and 6. The stubs in the module raise
`NotImplementedError` until then and do not block imports of the
XGBoost or TabNet sections.

### 14.2 To Kenneth (Role 4)

Execution contract: `docs/contracts/role-4-training-execution-spec.md`.
Kenneth runs Notebook 02 Cells 7–10 for XGBoost and TabNet, following
the pre-run checklist in section 16 and reporting via the templates in
section 11.

### 14.3 To Markie (Role 2)

After all three models exist, Notebook 03 uses the model artifacts to
produce the evaluation and explainability outputs. The bridge
(`server/predict_bridge.py`) loads the same artifacts. The contract
`api_data_contract.md` documents the exact loading and transformation
path.

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
| Handoff notification to Kenneth | Pending (message ready) |
| Amber implements RF | Pending (Role 3) |
| Kenneth runs XGBoost and TabNet | Pending (Role 4) |
| Model results populated (section 10) | Pending |
| Overfitting diagnostics populated (section 11) | Pending |

Phase 3 code and documentation work is complete. Model training and
result population depend on the Role 3 and Role 4 handoffs.

---

## 17. Next Phase

**Phase 4 — Project Management Oversight.**

Target activities:

- Monitor `docs/contracts/rubric_compliance.md` for alignment
- Coordinate the final merge of the Phase 3 branch to `main`
- Ensure every member is prepared for their video segment
- Author the submission package (`SUBMISSION.md`, `README.md`)
- Final review pass before the Day 10 deadline

Phase 4 produces no code. It produces coordination artifacts, a final
README, and the submission package.
```
