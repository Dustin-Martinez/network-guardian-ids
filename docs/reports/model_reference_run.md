# Model Reference Run

**Purpose:** Record the output of a clean training run on the frozen
data with the frozen seed. Teammates compare their own runs against
the values here. Deviations greater than two percent indicate a
problem and must be reported to Kit before proceeding.

**Owner:** Kit (Role 1). Updated only by Kit.

**Last updated:** Day 5 of the sprint (partial; full update after
execution).

**Related documents:**
- `docs/contracts/role-4-training-execution-spec.md` — XGBoost run
- `docs/contracts/role-5-training-execution-spec.md` — TabNet run
- `docs/contracts/role-3-rf-architecture-spec.md` — Random Forest run
- `data/processed/split_indices.json` — frozen split contract
- `docs/SETUP.md` — onboarding and first-run guide

---

## 1. Reference Environment

The values below reflect the machine on which the reference run is
performed. Teammates on different machines may see different wall-clock
times. The metrics (Macro F1, per-class recall) are hardware-independent
and must match.

| Component | Value |
|---|---|
| Operating System | Windows 10 (AMD64) |
| Python | 3.11.9 |
| CPU | AMD Ryzen 7 5700U with Radeon Graphics |
| Physical cores | 8 |
| Logical cores | 16 |
| RAM | 15.34 GB |
| GPU | None (CPU-only training) |
| torch version | 2.1.0+cpu |
| xgboost version | 2.0.0 |
| pytorch-tabnet version | 4.1.0 |
| scikit-learn version | 1.3.1 |
| Commit hash | 9daadc2fcf328f60a0844f6d03ebc84ac8f4a0b9 |
| Date of run | 2026-10-08 |

---

## 2. Frozen Inputs

These values are fixed and must match on every machine.

| Input | Value |
|---|---|
| Data file | `data/raw/kddcup.csv` |
| Raw rows | 494,021 |
| Raw columns | 42 (41 features + 1 label) |
| Post-dedup rows | 145,584 |
| Training rows | 109,188 |
| Test rows | 36,396 |
| Feature count after encoding | 43 |
| Class order | `["normal", "dos", "probe", "r2l", "u2r"]` |
| Random state | 42 |
| Split contract | `data/processed/split_indices.json` |

### Class Distribution

**Train (109,188 rows):**

| Class | Count |
|---|---|
| normal | 65,874 |
| dos | 40,928 |
| probe | 1,598 |
| r2l | 749 |
| u2r | 39 |

**Test (36,396 rows):**

| Class | Count |
|---|---|
| normal | 21,958 |
| dos | 13,643 |
| probe | 532 |
| r2l | 250 |
| u2r | 13 |

If any teammate's split produces different counts, the split contract
is not being honored. Stop and report to Kit.

---

## 3. Random Forest Reference

Run performed by Amber (Role 3). Values recorded after the run
completes.

| Metric | Value |
|---|---|
| Best trial number | <PENDING> |
| Best CV Macro F1 (mean) | <PENDING> |
| Best CV Macro F1 (std) | <PENDING> |
| OOB Macro F1 | <PENDING> |
| Wall time | <PENDING> |

**Per-class recall on CV validation folds:**

| Class | Recall |
|---|---|
| normal | <PENDING> |
| dos | <PENDING> |
| probe | <PENDING> |
| r2l | <PENDING> |
| u2r | <PENDING> |

**Best hyperparameters:**

| Parameter | Value |
|---|---|
| `n_estimators` | <PENDING> |
| `max_depth` | <PENDING> |
| `min_samples_split` | <PENDING> |
| `min_samples_leaf` | <PENDING> |
| `max_features` | <PENDING> |
| `criterion` | <PENDING> |
| `class_weight` | <PENDING> |

**Artifacts produced:**

- `models/rf_baseline.joblib`
- `models/rf_baseline.meta.json`
- `outputs/02_training/optuna_study_rf.db`
- `outputs/02_training/optuna_rf_trials.csv`
- `outputs/02_training/rf_cv_scores.csv`

---

## 4. XGBoost Reference

Run performed by Kenneth (Role 4). Values recorded after the run
completes.

| Metric | Value |
|---|---|
| Best trial number | <PENDING> |
| Best CV Macro F1 (mean) | <PENDING> |
| Best CV Macro F1 (std) | <PENDING> |
| Wall time | <PENDING> |

**Per-class recall on CV validation folds:**

| Class | Recall |
|---|---|
| normal | <PENDING> |
| dos | <PENDING> |
| probe | <PENDING> |
| r2l | <PENDING> |
| u2r | <PENDING> |

**Best hyperparameters:**

| Parameter | Value |
|---|---|
| `learning_rate` | <PENDING> |
| `max_depth` | <PENDING> |
| `min_child_weight` | <PENDING> |
| `gamma` | <PENDING> |
| `subsample` | <PENDING> |
| `colsample_bytree` | <PENDING> |
| `reg_alpha` | <PENDING> |
| `reg_lambda` | <PENDING> |
| `max_delta_step` | <PENDING> |
| `n_estimators` | <PENDING> |

**Artifacts produced:**

- `models/xgb_optuna.joblib`
- `models/xgb_optuna.meta.json`
- `outputs/02_training/optuna_study_xgb.db`
- `outputs/02_training/optuna_xgb_trials.csv`
- `outputs/02_training/xgb_cv_scores.csv`

---

## 5. TabNet Reference

Run performed by Dwayne (Role 5). Values recorded after the run
completes.

### 5.1 Feasibility Test (already measured)

A preliminary single-run test was performed on Day 3 to calibrate the
trial budget. This is not the reference run; it is provided as a
starting benchmark.

| Metric | Value |
|---|---|
| Training rows | 109,188 |
| Feature count | 43 |
| Epochs trained | 30 |
| Mean epoch time | 22.09 seconds |
| Total training time | 662.67 seconds (approximately 11 minutes) |
| Test Macro F1 (single run) | 0.8911 |
| Best val_accuracy | 0.99835 |
| n_d | 16 |
| n_a | 16 |
| n_steps | 5 |
| gamma | 1.5 |
| lambda_sparse | 1e-3 |
| batch_size | 1024 |
| virtual_batch_size | 128 |

Source: `scripts/feasibility_tabnet.py`, run on Day 3.

### 5.2 Full Optuna Study (to be recorded)

| Metric | Value |
|---|---|
| Best trial number | <PENDING> |
| Best CV Macro F1 (mean) | <PENDING> |
| Best CV Macro F1 (std) | <PENDING> |
| Wall time | <PENDING> |

**Per-class recall on CV validation folds:**

| Class | Recall |
|---|---|
| normal | <PENDING> |
| dos | <PENDING> |
| probe | <PENDING> |
| r2l | <PENDING> |
| u2r | <PENDING> |

**Best architecture:**

| Parameter | Value |
|---|---|
| `n_d` | <PENDING> |
| `n_a` | <PENDING> |
| `n_steps` | <PENDING> |
| `gamma` | <PENDING> |
| `lambda_sparse` | <PENDING> |
| `n_independent` | <PENDING> |
| `n_shared` | <PENDING> |
| `momentum` | <PENDING> |
| `mask_type` | <PENDING> |
| `batch_size` | <PENDING> |
| `virtual_batch_size` | <PENDING> |

**Artifacts produced:**

- `models/tabnet_best.zip`
- `models/tabnet_best.meta.json`
- `outputs/02_training/optuna_study_tabnet.db`
- `outputs/02_training/optuna_tabnet_trials.csv`
- `outputs/02_training/tabnet_cv_scores.csv`

---

## 6. Cross-Model Comparison Reference

Filled after all three runs complete. Populated from
`outputs/02_training/model_comparison.csv`.

| Metric | Random Forest | XGBoost | TabNet |
|---|---|---|---|
| CV Macro F1 (mean) | <PENDING> | <PENDING> | <PENDING> |
| CV Macro F1 (std) | <PENDING> | <PENDING> | <PENDING> |
| U2R recall | <PENDING> | <PENDING> | <PENDING> |
| R2L recall | <PENDING> | <PENDING> | <PENDING> |
| Probe recall | <PENDING> | <PENDING> | <PENDING> |
| DoS recall | <PENDING> | <PENDING> | <PENDING> |
| Normal recall | <PENDING> | <PENDING> | <PENDING> |
| Training time | <PENDING> | <PENDING> | <PENDING> |

---

## 7. How to Compare Your Run

Prerequisite: `docs/SETUP.md` sections 1 through 9 must be complete.
This ensures `data/processed/` has been generated and the frozen
hashes verified.

After running a model's training cell, read the corresponding meta
sidecar and compare against the values in sections 3, 4, or 5 above.
### 7.1 For Random Forest

```powershell
python -c "
import json
from src.utils import PATHS
meta = json.load(open(PATHS.models / 'rf_baseline.meta.json'))
print('CV Macro F1 :', meta['cv_mean_macro_f1'])
print('CV std      :', meta['cv_std_macro_f1'])
print('OOB F1      :', meta['oob_macro_f1'])
print('Per class   :', meta['per_class_recall_train'])
"
```

### 7.2 For XGBoost

```powershell
python -c "
import json
from src.utils import PATHS
meta = json.load(open(PATHS.models / 'xgb_optuna.meta.json'))
print('CV Macro F1 :', meta['cv_mean_macro_f1'])
print('CV std      :', meta['cv_std_macro_f1'])
print('Best trial  :', meta['best_trial_number'])
print('Per class   :', meta['per_class_recall_train'])
"
```

### 7.3 For TabNet

```powershell
python -c "
import json
from pytorch_tabnet.tab_model import TabNetClassifier
from src.utils import PATHS
model = TabNetClassifier()
model.load_model(str(PATHS.models / 'tabnet_best.zip'))
meta = json.load(open(PATHS.models / 'tabnet_best.meta.json'))
print('CV Macro F1 :', meta['cv_mean_macro_f1'])
print('CV std      :', meta['cv_std_macro_f1'])
print('Best trial  :', meta['best_trial_number'])
print('Per class   :', meta['per_class_recall_train'])
"
```

### 7.4 Tolerance

- **CV Macro F1:** should match the reference within ±0.02 absolute.
- **Per-class recall:** should match within ±0.05 absolute for the
  three majority classes, ±0.10 for r2l and u2r.
- **Best trial number:** will differ between runs because TPE sampling
  is seeded but the search space is large. Ignore the trial number; only
  the metrics matter.
- **Wall time:** will differ based on machine. Not a source of alarm.

### 7.5 What to Do If Values Diverge

If any metric is outside the tolerance band:

1. Do not re-run yet.
2. Check that `class_order.json` and `split_indices.json` are
   unchanged. Hash them against the versions in this document (see
   section 8).
3. Check that `src/models.py` has not been modified. Run
   `git diff HEAD -- src/models.py`.
4. If both checks pass and the divergence remains, report to Kit with
   the observed values and the meta sidecar contents.

---

## 8. Frozen Artifact Hashes

These hashes define the frozen inputs. If a teammate's environment
produces different hashes, the artifacts have been modified and the
divergence must be reported.

| File | SHA256 |
|---|---|
| `data/processed/class_order.json` | `63b3d7da8141a720abd0fb006c5ab285b4d4f6c2068bcc67304c35a40d08f52a` |
| `data/processed/split_indices.json` | `6b1272a7063348b1ba26ce60be2a6c492df6464fb228e1eb42e452011971f5db` |
| `data/processed/feature_names.json` | `d014bf4733de5e439169d5a5d346be4a0c2bef8080379ef27da6149357f2cef8` |
| `src/models.py` (at reference commit) | `38c8e622642e2f77cefe9b704639e9c1fb448d46dde2453876175feefbaa4d2d` |

To compute a hash:

```powershell
python -c "
from src.utils import compute_file_sha256, PATHS
print(compute_file_sha256(PATHS.processed / 'class_order.json'))
print(compute_file_sha256(PATHS.processed / 'split_indices.json'))
print(compute_file_sha256(PATHS.processed / 'feature_names.json'))
"
```

To compare the frozen `src/models.py` hash:

```powershell
python -c "
from src.utils import compute_file_sha256, PATHS
print(compute_file_sha256(PATHS.repo_root / 'src' / 'models.py'))
"
```

---

## 9. Change Log

| Date | Change | Author |
|---|---|---|
| Day 3 | Feasibility test recorded (section 5.1) | Kit |
| Day 5 | Reference environment recorded (section 1) | Kit |
| Day 5 | Frozen artifact hashes recorded (section 8) | Kit |
| Day 5 | Random Forest, XGBoost, and TabNet runs pending | Kit |

---

## 10. What Not to Do

- Do not modify this file to match your own run's numbers. This file
  is the reference. If your numbers diverge, your environment or
  configuration differs from the reference. Report the divergence; do
  not adjust the reference.
- Do not re-run training multiple times in search of "nicer" numbers.
  One run, one record.
- Do not skip the comparison in section 7. Silent divergence is the
  most common cause of downstream evaluation errors.

## 11. Verification Commands

Consolidated commands for teammates. Run these before, during, and
after your assigned training run. Every command is copy-paste ready.

---

### 11.1 Before You Start — Confirm the Frozen Inputs

Run this from the repo root, with `.venv` active. It checks that your
local copies of the frozen artifacts match the reference. All four
lines must print `OK`. If any line prints `MISMATCH`, stop and report
to Kit before running any training cell.

```powershell
python -c "
from src.utils import compute_file_sha256, PATHS
expected = {
    'class_order.json':   '63b3d7da8141a720abd0fb006c5ab285b4d4f6c2068bcc67304c35a40d08f52a',
    'split_indices.json': '6b1272a7063348b1ba26ce60be2a6c492df6464fb228e1eb42e452011971f5db',
    'feature_names.json': 'd014bf4733de5e439169d5a5d346be4a0c2bef8080379ef27da6149357f2cef8',
}
for name, exp in expected.items():
    actual = compute_file_sha256(PATHS.processed / name)
    status = 'OK' if actual == exp else 'MISMATCH'
    print(f'{name:<24} {status}')

models_hash = compute_file_sha256(PATHS.repo_root / 'src' / 'models.py')
expected_models = '38c8e622642e2f77cefe9b704639e9c1fb448d46dde2453876175feefbaa4d2d'
status = 'OK' if models_hash == expected_models else 'MISMATCH'
print(f'{\"src/models.py\":<24} {status}')
"
```

---

### 11.2 Before You Start — Confirm the Environment

Confirms your Python interpreter, package versions, and data shapes
match the reference environment.

```powershell
python -c "
import platform, json
import numpy as np
import torch, xgboost, sklearn
from importlib.metadata import version
from src.utils import PATHS

print('OS       :', platform.system(), platform.release())
print('Python   :', platform.python_version())
print('torch    :', torch.__version__)
print('xgboost  :', xgboost.__version__)
print('sklearn  :', sklearn.__version__)
print('tabnet   :', version('pytorch-tabnet'))
print()

X_train = np.load(PATHS.processed / 'X_train.npy')
X_test  = np.load(PATHS.processed / 'X_test.npy')
y_train = np.load(PATHS.processed / 'y_train.npy', allow_pickle=False)
y_test  = np.load(PATHS.processed / 'y_test.npy',  allow_pickle=False)
class_order = json.load(open(PATHS.processed / 'class_order.json'))

print('X_train  :', X_train.shape, X_train.dtype)
print('X_test   :', X_test.shape,  X_test.dtype)
print('y_train  :', y_train.shape, y_train.dtype)
print('y_test   :', y_test.shape,  y_test.dtype)
print('class_order :', class_order)
"
```

Expected values:

- `X_train`: `(109188, 43)` `float64`
- `X_test`: `(36396, 43)` `float64`
- `y_train`: `(109188,)` `<U6`
- `y_test`: `(36396,)` `<U6`
- `class_order`: `['normal', 'dos', 'probe', 'r2l', 'u2r']`

---

### 11.3 During the Run — Monitor Progress

Optuna is configured at WARNING log level, so it does not print
per-trial progress. Watch the SQLite study database instead. Its
modification time advances after each completed trial.

#### XGBoost (Kenneth)

```powershell
while ($true) {
    Get-Item outputs\02_training\optuna_study_xgb.db |
        Select-Object LastWriteTime, @{N='Size_MB';E={[math]::Round($_.Length/1MB,2)}}
    Start-Sleep -Seconds 60
}
```

#### TabNet (Dwayne)

```powershell
while ($true) {
    Get-Item outputs\02_training\optuna_study_tabnet.db |
        Select-Object LastWriteTime, @{N='Size_MB';E={[math]::Round($_.Length/1MB,2)}}
    Start-Sleep -Seconds 60
}
```

Press `Ctrl+C` to stop monitoring. The training continues in the
notebook.

If the file has not been modified for over 90 minutes and CPU usage is
near zero, the run has stalled. See the failure-modes section of your
execution contract.

---

### 11.4 After the Run — XGBoost Verification (Kenneth)

```powershell
python -c "
import joblib, json
from src.utils import PATHS
model = joblib.load(PATHS.models / 'xgb_optuna.joblib')
meta = json.load(open(PATHS.models / 'xgb_optuna.meta.json'))
print('CV Macro F1 :', meta['cv_mean_macro_f1'])
print('CV std      :', meta['cv_std_macro_f1'])
print('Best trial  :', meta['best_trial_number'])
print('Per class   :', meta['per_class_recall_train'])
print()
print('Artifacts:')
for p in [
    PATHS.models / 'xgb_optuna.joblib',
    PATHS.models / 'xgb_optuna.meta.json',
    PATHS.outputs / '02_training' / 'optuna_study_xgb.db',
    PATHS.outputs / '02_training' / 'optuna_xgb_trials.csv',
    PATHS.outputs / '02_training' / 'xgb_cv_scores.csv',
]:
    print(f'  {p.name:<32} {\"OK\" if p.exists() else \"MISSING\"}')
"
```

---

### 11.5 After the Run — TabNet Verification (Dwayne)

```powershell
python -c "
import json
from pytorch_tabnet.tab_model import TabNetClassifier
from src.utils import PATHS
model = TabNetClassifier()
model.load_model(str(PATHS.models / 'tabnet_best.zip'))
meta = json.load(open(PATHS.models / 'tabnet_best.meta.json'))
print('CV Macro F1 :', meta['cv_mean_macro_f1'])
print('CV std      :', meta['cv_std_macro_f1'])
print('Best trial  :', meta['best_trial_number'])
print('Per class   :', meta['per_class_recall_train'])
print()
print('Artifacts:')
for p in [
    PATHS.models / 'tabnet_best.zip',
    PATHS.models / 'tabnet_best.meta.json',
    PATHS.outputs / '02_training' / 'optuna_study_tabnet.db',
    PATHS.outputs / '02_training' / 'optuna_tabnet_trials.csv',
    PATHS.outputs / '02_training' / 'tabnet_cv_scores.csv',
]:
    print(f'  {p.name:<32} {\"OK\" if p.exists() else \"MISSING\"}')
"
```

---

### 11.6 After the Run — Random Forest Verification (Amber)

```powershell
python -c "
import joblib, json
from src.utils import PATHS
model = joblib.load(PATHS.models / 'rf_baseline.joblib')
meta = json.load(open(PATHS.models / 'rf_baseline.meta.json'))
print('CV Macro F1 :', meta['cv_mean_macro_f1'])
print('CV std      :', meta['cv_std_macro_f1'])
print('OOB Macro F1:', meta['oob_macro_f1'])
print('Best trial  :', meta['best_trial_number'])
print('Per class   :', meta['per_class_recall_train'])
print()
print('Artifacts:')
for p in [
    PATHS.models / 'rf_baseline.joblib',
    PATHS.models / 'rf_baseline.meta.json',
    PATHS.outputs / '02_training' / 'optuna_study_rf.db',
    PATHS.outputs / '02_training' / 'optuna_rf_trials.csv',
    PATHS.outputs / '02_training' / 'rf_cv_scores.csv',
]:
    print(f'  {p.name:<32} {\"OK\" if p.exists() else \"MISSING\"}')
"
```

---

### 11.7 After the Run — Cross-Model Comparison (Kit)

Run after all three models are trained. Reads every meta sidecar and
prints a single comparison table.

```powershell
python -c "
import json
from src.utils import PATHS

models = {
    'RandomForest': 'rf_baseline.meta.json',
    'XGBoost':      'xgb_optuna.meta.json',
    'TabNet':       'tabnet_best.meta.json',
}

rows = []
for name, fname in models.items():
    p = PATHS.models / fname
    if not p.exists():
        rows.append((name, 'MISSING', '', '', '', '', '', ''))
        continue
    m = json.load(open(p))
    pc = m.get('per_class_recall_train', {})
    rows.append((
        name,
        f\"{m['cv_mean_macro_f1']:.4f}\",
        f\"{m['cv_std_macro_f1']:.4f}\",
        f\"{pc.get('u2r', 0):.3f}\",
        f\"{pc.get('r2l', 0):.3f}\",
        f\"{pc.get('probe', 0):.3f}\",
        f\"{pc.get('dos', 0):.3f}\",
        f\"{pc.get('normal', 0):.3f}\",
    ))

hdr = ('Model', 'CV_F1', 'CV_std', 'U2R', 'R2L', 'Probe', 'DoS', 'Normal')
print(f'{hdr[0]:<14} {hdr[1]:>7} {hdr[2]:>7} {hdr[3]:>6} {hdr[4]:>6} {hdr[5]:>6} {hdr[6]:>6} {hdr[7]:>7}')
print('-' * 76)
for r in rows:
    print(f'{r[0]:<14} {r[1]:>7} {r[2]:>7} {r[3]:>6} {r[4]:>6} {r[5]:>6} {r[6]:>6} {r[7]:>7}')
"
```

---

### 11.8 Troubleshooting

#### `MISMATCH` on a frozen hash

One of the files in `data/processed/` or `src/models.py` has been
modified since the reference was recorded. Do not proceed with
training. Report the exact line that mismatched to Kit.

#### `MISSING` on an artifact

The training cell did not complete, or the save cell (Cell 8 or Cell
10) was not run. Re-run the training cell in the same session as the
save cell. Do not close the notebook between them.

#### `KeyError: 'per_class_recall_train'`

Your local `src/models.py` is out of date. Pull the latest from the
Phase 3 branch and rerun the verification.

#### `FileNotFoundError: optuna_study_xgb.db`

The training cell has not been run yet. Run Cell 7 first.
