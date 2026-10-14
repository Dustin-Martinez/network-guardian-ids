# Model Artifact Transfer Policy

**Owner of this specification:** Kit (Role 1)
**Effective date:** Day 6 of the 10-day sprint
**Status:** Frozen for the sprint. Changes require a PR and Kit's
sign-off.
**Related documents:**
- `docs/README.md` — documentation hierarchy
- `docs/contracts/role-3-rf-architecture-spec.md` — Random Forest
- `docs/contracts/role-4-training-execution-spec.md` — XGBoost
- `docs/contracts/role-5-training-execution-spec.md` — TabNet
- `.gitignore` — repository exclusion policy

---

## 1. Purpose

This document defines exactly which files each role transfers to the
team repository after their training run completes. It resolves any
ambiguity about what gets committed, what stays local, and how the
comparison table is populated on Kit's machine.

The policy exists because trained model binaries are large, opaque,
and regenerable, and therefore are not committed to git. The evidence
for every number in the paper lives in the small JSON and CSV files
that are committed.

---

## 2. Policy Summary

| Category | Committed? | Reason |
|---|---|---|
| Source code (`src/*.py`) | Yes | Source |
| Notebooks (`notebooks/*.ipynb`) | Yes | Execution records |
| Documentation (`docs/**/*.md`) | Yes | Reports and contracts |
| Raw data (`data/raw/*`) | Yes | Source dataset and manifests |
| Frozen contracts (`data/processed/*.json`) | Yes | Reproducibility contract |
| Processed arrays (`data/processed/*.npy`, `*.pkl`) | No | Regenerable by Notebook 01 |
| **Model meta sidecars (`models/*.meta.json`)** | **Yes** | Evidence trail |
| Model binaries (`models/*.joblib`, `*.zip`, `*.pt`) | No | Large, regenerable |
| Trial logs (`outputs/02_training/optuna_*_trials.csv`) | Yes | Optimization record |
| Fold scores (`outputs/02_training/*_cv_scores.csv`) | Yes | Per-fold evidence |
| Study databases (`outputs/02_training/*.db`) | No | Regenerable, potentially large |
| Evaluation figures (`outputs/03_evaluation/*`) | Yes | Graded deliverables |
| Sprint reports (`docs/reports/role-*`) | Yes | Documentation |

---

## 3. Required Files Per Model

Each model produces three required files that must be transferred. All
three are already trackable under the current `.gitignore`. No `-f`
flag is needed.

### 3.1 Random Forest — Owner: Amber (Role 3)

| File | Purpose |
|---|---|
| `models/rf_baseline.meta.json` | Provenance: hyperparameters, CV metrics, per-class recall, feature order, class order |
| `outputs/02_training/optuna_rf_trials.csv` | Every Optuna trial's parameters and score |
| `outputs/02_training/rf_cv_scores.csv` | Per-fold Macro F1 for the best trial |

### 3.2 XGBoost — Owner: Kit Dustin (Role 1)

Originally assigned to Kenneth (Role 4). Execution was reassigned to
Kit Dustin on Day 6 of the sprint. See
`docs/decision/decision_role4_xgboost_reassignment_20261014.md`.

| File | Purpose |
|---|---|
| `models/xgb_optuna.meta.json` | Provenance: hyperparameters, CV metrics, per-class recall |
| `outputs/02_training/optuna_xgb_trials.csv` | Every Optuna trial's parameters and score |
| `outputs/02_training/xgb_cv_scores.csv` | Per-fold Macro F1 for the best trial |

### 3.3 TabNet — Owner: Dwayne (Role 5)

| File | Purpose |
|---|---|
| `models/tabnet_best.meta.json` | Provenance: architecture, hyperparameters, CV metrics, per-class recall |
| `outputs/02_training/optuna_tabnet_trials.csv` | Every Optuna trial's parameters and score |
| `outputs/02_training/tabnet_cv_scores.csv` | Per-fold Macro F1 for the best trial |

---

## 4. Files Not Transferred

These files exist after a training run but are not committed.

### 4.1 Model binaries

| File | Typical size | Reason not committed |
|---|---|---|
| `models/rf_baseline.joblib` | 10–50 MB | Regenerable, opaque |
| `models/xgb_optuna.joblib` | 30–80 MB | Regenerable, opaque, exceeds GitHub soft limit |
| `models/tabnet_best.zip` | 5–20 MB | Regenerable, opaque |

### 4.2 Study databases

| File | Typical size | Reason not committed |
|---|---|---|
| `outputs/02_training/optuna_study_rf.db` | 5–20 MB | Regenerable from trial log |
| `outputs/02_training/optuna_study_xgb.db` | 5–20 MB | Regenerable from trial log |
| `outputs/02_training/optuna_study_tabnet.db` | 5–20 MB | Regenerable from trial log |

### 4.3 Pre-encoded CSV backups

| File | Reason not committed |
|---|---|
| `data/processed/train_preencoded.csv` | Regenerable by Notebook 01 |
| `data/processed/test_preencoded.csv` | Regenerable by Notebook 01 |

---

## 5. Transfer Procedure

Each training-run contributor follows this procedure after their
training cell and verification cell complete successfully.

### Step 1 — Confirm the three files exist

```powershell
# Amber — Random Forest
Get-ChildItem models\rf_baseline.meta.json
Get-ChildItem outputs\02_training\optuna_rf_trials.csv
Get-ChildItem outputs\02_training\rf_cv_scores.csv

# Kit — XGBoost
Get-ChildItem models\xgb_optuna.meta.json
Get-ChildItem outputs\02_training\optuna_xgb_trials.csv
Get-ChildItem outputs\02_training\xgb_cv_scores.csv

# Dwayne — TabNet
Get-ChildItem models\tabnet_best.meta.json
Get-ChildItem outputs\02_training\optuna_tabnet_trials.csv
Get-ChildItem outputs\02_training\tabnet_cv_scores.csv
```

All three must exist. If any is missing, the training cell did not
complete or the meta sidecar write failed. Rerun the training cell
before transferring.

### Step 2 — Create the artifact branch

Branch naming follows the pattern
`artifacts/<role>-<model>-<YYYYMMDD>`.

```powershell
# Amber
git checkout -b artifacts/amber-rf-20261013

# Kit
git checkout -b artifacts/kit-xgb-20261014

# Dwayne
git checkout -b artifacts/dwayne-tabnet-20261013
```

Replace the date with the actual date of the transfer.

### Step 3 — Stage exactly three files

```powershell
# Amber
git add models/rf_baseline.meta.json
git add outputs/02_training/optuna_rf_trials.csv
git add outputs/02_training/rf_cv_scores.csv

# Kit
git add models/xgb_optuna.meta.json
git add outputs/02_training/optuna_xgb_trials.csv
git add outputs/02_training/xgb_cv_scores.csv

# Dwayne
git add models/tabnet_best.meta.json
git add outputs/02_training/optuna_tabnet_trials.csv
git add outputs/02_training/tabnet_cv_scores.csv
```

### Step 4 — Verify the staging area

```powershell
git status --short
```

Expected: exactly three lines, each beginning with `A ` or `M `.
If any additional file appears, unstage it:

```powershell
git reset HEAD <unwanted-file>
```

### Step 5 — Commit

```powershell
# Amber
git commit -m "artifacts(rf): Random Forest training results"

# Kit
git commit -m "artifacts(xgb): XGBoost training results"

# Dwayne
git commit -m "artifacts(tabnet): TabNet training results"
```

### Step 6 — Push the artifact branch

```powershell
git push -u origin artifacts/<role>-<model>-<YYYYMMDD>
```

### Step 7 — Notify Kit

Post in the team channel with the branch name:

> Artifact branch pushed: `artifacts/amber-rf-20261013`. Three files included: meta sidecar, trial log, fold scores.

> Artifact branch pushed: `artifacts/kit-xgb-20261014`. Three files included: meta sidecar, trial log, fold scores.

> Artifact branch pushed: `artifacts/dwayne-tabnet-20261013`. Three files included: meta sidecar, trial log, fold scores.

### Step 8 — Kit merges

Kit pulls each artifact branch, verifies the three files, and merges
into `main`.

---

## 6. What Each File Contains

### 6.1 Meta sidecar structure

All three models write the same core fields. Some fields differ by
model.

```json
{
  "model": "<random_forest | xgboost | tabnet>",
  "trained_at": "ISO-8601 UTC timestamp",
  "optuna_trials": <int>,
  "cv_folds": <int>,
  "best_trial_number": <int>,
  "best_params": { ... },
  "cv_mean_macro_f1": <float>,
  "cv_std_macro_f1": <float>,
  "fold_scores": [<float>, ...],
  "per_class_recall_train": {
    "normal": <float>,
    "dos": <float>,
    "probe": <float>,
    "r2l": <float>,
    "u2r": <float>
  },
  "feature_names": [<str>, ...],
  "class_order": ["normal", "dos", "probe", "r2l", "u2r"],
  "n_train": <int>,
  "n_features": <int>,
  "random_state": 42,
  "notes": "<str>"
}
```

The Random Forest meta sidecar uses a different key for per-class
recall: `per_class_recall_cv`. This reflects that the RF's per-class
recall is computed from the CV folds, while XGBoost and TabNet compute
it on the training pool.

The two fields measure the same concept — per-class recall — but on
different data. The distinction matters when the paper cites the
numbers:

- `per_class_recall_cv` — generalization estimate from held-out CV
  folds
- `per_class_recall_train` — training-pool fit, not a generalization
  metric

When citing per-class recall in the paper, prefer the CV value if it
is available. Otherwise, cite the test-set value produced by
Notebook 03. Do not cite `per_class_recall_train` as a generalization
metric.

### 6.2 Trial log structure

The Optuna trial log is a CSV with one row per trial. Columns include:

- `number` — trial index
- `value` — Macro F1 achieved by the trial
- `state` — COMPLETE, PRUNED, or FAIL
- `params_*` — one column per hyperparameter
- `datetime_start`, `datetime_complete`, `duration` — timing

### 6.3 Fold scores structure

The fold scores CSV has one row per fold:

- `fold` — fold index (0-based)
- `macro_f1` — Macro F1 achieved on that fold's validation partition

For Random Forest the fold scores come from the best trial's persisted
arrays. For XGBoost and TabNet they come from the best trial's
intermediate values.

---

## 7. What the Comparison Table Requires

Notebook 02 Cell 11 reads exactly three files:

- `models/rf_baseline.meta.json`
- `models/xgb_optuna.meta.json`
- `models/tabnet_best.meta.json`

If all three exist on Kit's machine, the comparison table populates.
The binaries are not read.

Notebook 03 (evaluation) reads the binaries for the confusion matrices
and SHAP plots. If the binaries are not on Kit's machine when Notebook
03 runs, the evaluation step must be coordinated so that it runs on
a machine that has all three binaries.

---

## 8. Binary Transfer via Shared Drive

If a downstream step requires an actual binary and it is not present
locally, the binary is transferred via the shared drive. It is never
committed to git.

### 8.1 Drive Location

**Folder name:** `NetworkGuardian-Models`

**Contents after all three models trained:**

    NetworkGuardian-Models/
    ├── rf_baseline.joblib           (Amber)
    ├── rf_baseline.meta.json        (Amber)
    ├── xgb_optuna.joblib            (Kit)
    ├── xgb_optuna.meta.json         (Kit)
    ├── tabnet_best.zip              (Dwayne)
    └── tabnet_best.meta.json        (Dwayne)

### 8.2 Upload Procedure

After the training run completes and the artifact branch is pushed,
the training-run contributor uploads both the binary and the meta
sidecar to the shared drive folder. Post in the team channel when
done.

### 8.3 Download Procedure

Before running Notebook 03 (evaluation), download the binaries and
meta sidecars that are not already present locally. The evaluation
step requires all three binaries and all three meta sidecars to be
present in the local `models/` folder.

---

## 9. What Happens If a File Is Missing

If a required file is missing at Kit's machine after the artifact
branches are merged:

| Missing file | Impact | Resolution |
|---|---|---|
| Meta sidecar | Comparison table has a MISSING row for that model | Teammate reruns the training cell or pushes the meta sidecar from their local copy |
| Trial log | No trial history for the paper's appendix | Teammate pushes the CSV from their local copy |
| Fold scores | No per-fold evidence | Teammate pushes the CSV from their local copy |
| Binary | Notebook 03 cannot evaluate that model locally | Coordinate binary transfer via shared drive |

---

## 10. `.gitignore` Alignment

The `.gitignore` was verified against this policy during the XGBoost
phase. Current state:

| Pattern | Status | Effect |
|---|---|---|
| `models/*.joblib` | Present | Ignores RF and XGBoost binaries |
| `models/*.zip` | Present | Ignores the TabNet binary |
| `models/*.pt` | Present | Ignores any future PyTorch binary |
| `models/*.meta.json` | Not present (tracked) | Meta sidecars are committed |
| `outputs/02_training/*.db` | Present | Study databases are ignored |
| `!outputs/**/*.csv` | Present | Trial logs and fold CSVs are tracked |

No `.gitignore` change is needed for the standard workflow. If a new
artifact type is introduced, update this section.

---

## 11. Change Control

This policy is frozen for the sprint. Any change requires:

1. A pull request that modifies this file.
2. A note in `docs/reports/` describing the change and the reason.
3. Kit's approval as the policy owner.

If a teammate encounters an ambiguity not covered by this policy, the
escalation path is `docs/README.md` section 10 and the decision
template at `docs/decision/Decision Template.md`.

---

## 12. Quick Reference

**Files to push per model:**

```
models/<model>.meta.json
outputs/02_training/optuna_<model>_trials.csv
outputs/02_training/<model>_cv_scores.csv
```

Where `<model>` is `rf_baseline`, `xgb_optuna`, or `tabnet_best`.

**Files to not push:**

```
models/*.joblib
models/*.zip
models/*.pt
outputs/02_training/*.db
data/processed/*.npy
data/processed/*.pkl
```

**Branch name format:**

```
artifacts/<role>-<model>-<YYYYMMDD>
```

**Commit message format:**

```
artifacts(<model>): training results
```

---END OF DOCUMENT---