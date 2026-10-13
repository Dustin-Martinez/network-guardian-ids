# Handoff — XGBoost Phase 2

**Model:** XGBoost Classifier
**Owner of the run:** Kit Dustin (Role 1) — reassigned from Kenneth (Role 4) on Day 6
**Status:** Complete
**Date closed:** 2026-10-14
**Contract:** `docs/contracts/role-4-training-execution-spec.md`
**Sprint report:** `docs/reports/role-4-phase-2-kit-xgboost-execution.md`
**Decision file:** `docs/decision/decision_role4_xgboost_reassignment_20261014.md`

---

## 1. Result Summary

| Metric | Value |
|---|---|
| CV mean Macro F1 | **0.9508** |
| CV standard deviation | 0.0260 |
| Best trial number | 81 |
| Best trial duration | 3 minutes 44 seconds |
| Wall time (full run) | approximately 1 hour 55 minutes |
| Fold scores | 0.9416 / 0.9416 / 0.9472 / 0.9460 / 0.9508 |
| Fold range | 0.0092 |

No fold is an outlier. Every fold scored above 0.94.

---

## 2. Best Hyperparameters

```python
{
  'colsample_bytree': 0.7884,
  'gamma': 0.0095,
  'learning_rate': 0.0435,
  'max_delta_step': 4,
  'min_child_weight': 2,
  'max_depth': 10,
  'n_estimators': 250,
  'reg_alpha': 0.6338,
  'reg_lambda': 7.2469,
  'subsample': 0.8088,
}
```

`max_depth=10` is the upper bound of the search space. The optimum
sits at or above this ceiling. Documented in the sprint report
section 7.5.

---

## 3. Artifacts

### 3.1 On the repository (artifact branch `artifacts/kit-xgb-20261014`)

| File | Purpose |
|---|---|
| `models/xgb_optuna.meta.json` | Provenance and metrics |
| `outputs/02_training/optuna_xgb_trials.csv` | Trial history |
| `outputs/02_training/xgb_cv_scores.csv` | Per-fold scores |

### 3.2 On the shared drive (folder `NetworkGuardian-Models`)

| File | Size | Purpose |
|---|---|---|
| `xgb_optuna.joblib` | 2.7 MB | Trained model binary |
| `xgb_optuna.meta.json` | 2 KB | Provenance copy |

### 3.3 Local only (not transferred)

| File | Purpose | Reason not transferred |
|---|---|---|
| `outputs/02_training/optuna_study_xgb.db` | Full study database | Regenerable from trial log |

---

## 4. Verification

Performed per section 9 of the execution contract.

| Check | Result |
|---|---|
| Model file exists | Pass |
| Meta sidecar exists | Pass |
| Study database exists | Pass |
| Trial log exists | Pass |
| Fold scores CSV exists | Pass |
| CV Macro F1 in expected range | Pass — 0.9508 |
| Meta and CSV fold scores match | Pass — identical |

---

## 5. Handoff Actions

### 5.1 To Dwayne (Role 5) — evaluation

Dwayne downloads two files from the shared drive before running
Notebook 03:

- `xgb_optuna.joblib`
- `xgb_optuna.meta.json`

Both files belong in his local `models/` folder alongside
`rf_baseline.*` and `tabnet_best.*`. After downloading, his
`models/` folder must contain all six files:

```
models/
├── rf_baseline.joblib              (downloaded from shared drive)
├── rf_baseline.meta.json           (downloaded from shared drive)
├── xgb_optuna.joblib               (downloaded from shared drive)
├── xgb_optuna.meta.json            (downloaded from shared drive)
├── tabnet_best.zip                 (produced locally)
└── tabnet_best.meta.json           (produced locally)
```

Once all six are present, Notebook 03 can evaluate the XGBoost model
alongside the other two.

### 5.2 To Kit — comparison table

The comparison table in Notebook 02 Cell 11 reads
`models/xgb_optuna.meta.json` from the artifact branch. Once Amber's
RF and Dwayne's TabNet meta sidecars are on Kit's machine, Cell 11
can populate the full comparison.

### 5.3 To Markie — paper

Source numbers for the paper's Results section:

- CV mean Macro F1: 0.9508
- CV standard deviation: 0.0260
- Fold scores: as documented in section 1
- Best trial: 81
- Best hyperparameters: as documented in section 2

**Important caveat.** The meta sidecar field
`per_class_recall_train` measures recall on the training pool after
the refit. It is not a generalization metric. Test-set recall is
produced by Notebook 03. Do not cite `per_class_recall_train` as if
it were generalization performance.

---

## 6. Known Issues and Resolutions

### 6.1 Early stopping guard on the final refit

The first attempt at the final refit failed with
`ValueError: Must have at least 1 validation dataset for early stopping`.
Cause: `build_xgb` set `early_stopping_rounds` on the model
constructor, but the refit call did not pass an `eval_set`.

Resolution: `build_xgb` now accepts an `early_stopping` flag.
The CV folds pass `eval_set` and leave the flag at its default
(`True`). The final refit passes `early_stopping=False`. The fix is
documented in commit history and in `src/models.py`.

The study database was preserved across the failed attempt. Only the
refit step was rerun, taking under 5 minutes.

### 6.2 Long refit duration with no visible output

The refit took approximately 40 minutes of wall time. Optuna is
configured at WARNING log level, so no per-round output appears in
the terminal. The process was confirmed healthy by watching CPU
usage via `Get-Process`. The refit completed successfully.

Future executors should expect this and monitor via process CPU
rather than terminal output. See section 5.2 of the execution
contract.

---

## 7. Cross-References

| Document | Purpose |
|---|---|
| `docs/contracts/role-4-training-execution-spec.md` | Full execution contract |
| `docs/contracts/artifact_transfer_policy.md` | File transfer procedure |
| `docs/reports/role-4-phase-2-kit-xgboost-execution.md` | Full sprint report |
| `docs/decision/decision_role4_xgboost_reassignment_20261014.md` | Ownership transfer |
| `docs/reports/role-3-phase-2-amber-rf-baseline.md` | RF reference for comparison |
| `docs/handoffs/random_forest.md` | RF handoff, once available |
| `docs/handoffs/tabnet.md` | TabNet handoff, once available |

---

## 8. Confirmation

The XGBoost model is trained, verified, and available for downstream
work. The artifact branch is pushed. The shared drive contains the
binary and sidecar. The sprint report documents the run.

Phase 2 of Role 4 is closed.

---

**Signed off by:** Kit Dustin, Project Manager (Role 1)
**Date:** 2026-10-14