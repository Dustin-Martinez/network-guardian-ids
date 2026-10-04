```markdown
# Training Execution Specification

**Owner of the execution process:** Kenneth (Role 4)
**Owner of this specification:** Kit (Role 1)
**Effective date:** Day 3 of 10-day sprint
**Status:** Frozen for the sprint. Changes require a PR and Kit's sign-off.

---

## 1. Purpose

This document is the authoritative specification for how Kenneth executes
the XGBoost and TabNet training runs in Notebook 02. It defines what to
run, in what order, expected durations, how to monitor progress, how to
intervene when something goes wrong, and what to report back.

The specification exists so that the training runs happen reliably,
without guesswork, and without risk of accidental test-set exposure or
partial commits.

---

## 2. Responsibility Boundary

| Item | Owner |
|---|---|
| Running Notebook 02 Cells 7 and 8 (XGBoost) | Kenneth |
| Running Notebook 02 Cells 9 and 10 (TabNet) | Kenneth |
| Monitoring training output and reporting anomalies | Kenneth |
| Not modifying `src/models.py` | Anyone — it is frozen for Phase 3 |
| Not modifying Notebook 02 cells | Anyone — the cells call frozen functions |
| Not evaluating on the test set | Anyone — test evaluation happens in Notebook 03 |

Kenneth does not write code. Kenneth executes code that Kit has written
and verified. If a cell fails, Kenneth reports the error; Kenneth does
not attempt to fix it.

---

## 3. Prerequisites

Before starting any training run, verify all of the following.

### 3.1 Environment

- Python 3.11.9 running inside `.venv`
- `requirements.txt` fully installed
- All 13 critical packages import without error (test with `python src/verify_env.py`)
- At least **8 GB** of free RAM
- At least **5 GB** of free disk space in `outputs/02_training/`

### 3.2 Data

Run this check before proceeding:

```powershell
python -c "
import numpy as np, json
from src.utils import PATHS
X = np.load(PATHS.processed / 'X_train.npy')
y = np.load(PATHS.processed / 'y_train.npy', allow_pickle=False)
co = json.load(open(PATHS.processed / 'class_order.json'))
assert X.shape == (109188, 43), f'Unexpected X_train shape: {X.shape}'
assert y.shape == (109188,), f'Unexpected y_train shape: {y.shape}'
assert len(co) == 5, f'Unexpected class_order length: {len(co)}'
print('Data OK. X_train', X.shape, 'classes', co)
"
```

Expected output:

```
Data OK. X_train (109188, 43) classes ['normal', 'dos', 'probe', 'r2l', 'u2r']
```

If this fails, stop and contact Kit.

### 3.3 Notebook

- Open `notebooks/02_Model_Training.ipynb`
- Confirm the path-fix cell (Cell 2) runs and prints the repo root
- Confirm Cells 1 through 4 run without error

If any cell fails, stop and paste the error into the team channel.

---

## 4. Run Sequence

The full training sequence has four required cells. Run them in order.

| Order | Cell | Task | Duration |
|---|---|---|---|
| 1 | Cell 5 | Random Forest tuning | 1.5–3 hours |
| 2 | Cell 6 | Random Forest save | < 1 minute |
| 3 | Cell 7 | XGBoost tuning | 4–6 hours |
| 4 | Cell 8 | XGBoost save | < 1 minute |
| 5 | Cell 9 | TabNet tuning | 6–8 hours |
| 6 | Cell 10 | TabNet save | < 1 minute |
| 7 | Cell 11 | Cross-model comparison | < 1 minute |
| 8 | Cell 12 | Summary | < 1 minute |

Cells 5, 7, and 9 may be run on separate days. Cells 6, 8, 10 must be
run immediately after their corresponding tuning cell, in the same
session, or the trained model will not be persisted.

**Critical rule:** do not close the notebook between a tuning cell and
its save cell. If the session ends accidentally, re-run the tuning cell
from scratch. Partial models are not recoverable.

---

## 5. Running the XGBoost Cell (Cell 7)

### 5.1 What the cell does

Calls `train_xgb()` from `src/models.py`. That function:

1. Runs an Optuna study with 30 trials, 5-fold stratified CV each.
2. Applies Tomek Links inside each fold's training partition.
3. Uses class-weighted sample weights.
4. Targets Macro F1 as the objective.
5. Prunes trials whose running fold mean falls below the median.
6. Refits the best configuration on the full cleaned training pool.
7. Saves the model and meta sidecar.

### 5.2 Expected console output

The cell prints at the start:

```
Training XGBoost...
Running 30 Optuna trials with 5-fold CV each.
Estimated wall time: 4 to 6 hours.
```

Then during training, Optuna prints trial summaries periodically:

```
[I 2026-10-05 08:12:31,072] Trial 0 finished with value: 0.8842 and parameters: {...}.
[I 2026-10-05 08:25:14,331] Trial 1 finished with value: 0.8891 and parameters: {...}.
...
```

At the end, a summary block:

```
XGBoost study complete.
Best trial: 17
Best CV Macro F1: 0.9012
Final model refit on 108,432 rows.
Saved: models/xgb_optuna.joblib
Saved: models/xgb_optuna.meta.json
```

### 5.3 Expected duration

| Machine state | Duration |
|---|---|
| Fresh boot, nothing else running | 4 to 5 hours |
| Normal background load | 5 to 6 hours |
| Heavy load (other apps, browser tabs) | 6 to 8 hours |

If it runs beyond 10 hours, something is wrong. See section 8.

### 5.4 Monitoring during the run

The cell output refreshes as each trial completes. Kenneth checks in
periodically and notes:

- Which trial number is currently running
- The best score so far
- Whether the score is improving across trials

If the best score has not changed in the last 10 trials, that's normal —
Optuna's TPE sampler concentrates on promising regions and often plateaus.
Continue to completion.

---

## 6. Running the TabNet Cell (Cell 9)

### 6.1 What the cell does

Calls `train_tabnet()` from `src/models.py`. That function:

1. Runs an Optuna study with 20 trials, 3-fold stratified CV each.
2. Applies Tomek Links inside each fold's training partition.
3. Uses class-weighted loss via the `weights` argument of `fit()`.
4. Targets Macro F1 as the objective.
5. Prunes trials aggressively.
6. Refits the best configuration on the full cleaned training pool.
7. Saves the model (native `.zip` format) and meta sidecar.

### 6.2 Expected console output

The cell prints at the start:

```
Training TabNet...
Running 20 Optuna trials with 3-fold CV each.
Estimated wall time: 6 to 8 hours.
This run is CPU-bound and will produce heavy CPU load.
```

During training, pytorch-tabnet may print per-epoch progress for each
fold, but this is suppressed by the default `verbose=0`. Optuna prints
trial summaries:

```
[I 2026-10-06 02:15:44,912] Trial 0 finished with value: 0.8612 and parameters: {...}.
[I 2026-10-06 02:48:19,233] Trial 1 finished with value: 0.8734 and parameters: {...}.
...
```

At the end:

```
TabNet study complete.
Best trial: 11
Best CV Macro F1: 0.8911
Final model refit on 108,432 rows.
Saved: models/tabnet_best.zip
Saved: models/tabnet_best.meta.json
```

### 6.3 Expected duration

| Machine state | Duration |
|---|---|
| Fresh boot, nothing else running | 6 to 7 hours |
| Normal background load | 7 to 8 hours |
| Heavy load | 9 to 10 hours |

TabNet is CPU-intensive. During the run, expect:

- CPU usage near 100% on all cores
- Fan noise
- Machine may be sluggish for other tasks
- Do not run other heavy applications during this window

If it runs beyond 12 hours, something is wrong. See section 8.

### 6.4 Monitoring during the run

TabNet trials are longer than XGBoost trials. Checking every 60–90
minutes is sufficient. The key signal is that trials are completing and
Optuna is printing trial summaries.

If nothing prints for over 90 minutes, and CPU usage is still high, the
run is working on a slow trial. This is expected occasionally.

If nothing prints for over 120 minutes AND CPU usage is near zero, the
run has stalled. See section 8.

---

## 7. Handling Interruptions

### 7.1 Laptop sleep or shutdown during training

If the machine sleeps during a training run, the process is usually
paused but not killed. On wake, the run continues from where it left off.
Verify by checking that Optuna still prints trial summaries.

If the machine shuts down, the process is killed. On restart:

1. Check `outputs/02_training/optuna_study_xgb.db` or
   `optuna_study_tabnet.db` for completed trials.
2. If the study database exists and has trials, the study can be resumed.
3. If not, the run must be restarted from scratch.

**Prevention:** disable sleep for the duration of the run. On Windows:

```powershell
powercfg /change standby-timeout-ac 0
powercfg /change hibernate-timeout-ac 0
```

Reverse after training:

```powershell
powercfg /change standby-timeout-ac 30
powercfg /change hibernate-timeout-ac 60
```

### 7.2 Cell execution error mid-run

If a cell raises an exception, the training stops. Kenneth captures the
full traceback and pastes it in the team channel. Kenneth does not
attempt to modify the code.

### 7.3 Machine crash or restart

If the machine reboots unexpectedly:

1. Check which artifacts exist in `models/` and `outputs/02_training/`.
2. Report the current state to Kit.
3. Wait for Kit's guidance before re-running.

---

## 8. Failure Modes and Diagnostics

### 8.1 XGBoost trial taking more than 30 minutes

Normal trial time: 8 to 12 minutes.

A single trial exceeding 30 minutes indicates either an unusually deep
tree configuration or a machine resource issue. Do not intervene. Let
the trial complete. Optuna will log it and move on.

If three consecutive trials exceed 30 minutes, stop and report to Kit.

### 8.2 TabNet trial taking more than 90 minutes

Normal trial time: 20 to 30 minutes.

A single trial exceeding 90 minutes is unusual. Do not intervene unless
CPU usage drops to near zero. If CPU is idle for more than 10 minutes
during a TabNet trial, the process has stalled. Stop the cell and report.

### 8.3 Out of memory errors

Symptom: `MemoryError` or the process being killed by the OS.

Actions:
1. Close all other applications (browsers, Slack, Teams, etc.).
2. Free RAM by restarting the notebook kernel.
3. Re-run from the beginning of the failed cell.
4. If the error recurs on a fresh session, report to Kit. Memory
   constraints may require reducing the trial budget.

### 8.4 Disk full

Symptom: SQLite write errors, or failure to write `.joblib` / `.zip`.

Actions:
1. Check free space:

```powershell
Get-PSDrive C | Select-Object Used, Free
```

2. If under 2 GB free, empty the recycle bin, clear temp files, and
   retry.
3. If under 500 MB free, stop training and report to Kit.

### 8.5 Loss of network connectivity

Training runs locally and does not require internet. Network loss does
not affect training. Ignore.

### 8.6 Fan noise and high CPU temperature

Normal during TabNet runs. Ensure the laptop is on a hard surface with
airflow. Do not place it on a bed or cushion. If the machine shuts down
from thermal protection, see section 7.3.

---

## 9. Expected Console Anomalies (Not Errors)

The following messages are expected and should be ignored.

| Message | Meaning |
|---|---|
| `UserWarning: Could not find the number of physical cores` | Cosmetic. Harmless. |
| `Device used : cpu` | Expected. Running on CPU. |
| `Stop training because you reached max_epochs` | Normal TabNet early-stop message |
| `[LightGBM] ...` | Not applicable — XGBoost does not print this. If seen, report. |
| `FutureWarning` from sklearn | Cosmetic. Note the message and continue. |
| `ConvergenceWarning` | Possibly serious. Report to Kit. |

**Distinguish:** any line starting with `Traceback (most recent call last):`
is a real error. Stop and report.

---

## 10. Post-Run Verification

After each training cell completes, run the following checks.

### 10.1 XGBoost post-run

```powershell
python -c "
import joblib, json
from src.utils import PATHS
model = joblib.load(PATHS.models / 'xgb_optuna.joblib')
meta = json.load(open(PATHS.models / 'xgb_optuna.meta.json'))
print('CV Macro F1 :', meta['cv_mean_macro_f1'])
print('CV std      :', meta['cv_std_macro_f1'])
print('Best trial  :', meta['best_trial_number'])
print('U2R recall  :', meta['per_class_recall_cv']['u2r'])
print('R2L recall  :', meta['per_class_recall_cv']['r2l'])
"
```

Expected: CV Macro F1 in the range 0.85 to 0.95.

### 10.2 TabNet post-run

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
print('U2R recall  :', meta['per_class_recall_cv']['u2r'])
print('R2L recall  :', meta['per_class_recall_cv']['r2l'])
"
```

Expected: model loads without error, CV Macro F1 in the range 0.80 to 0.92.

### 10.3 File existence

```powershell
Get-ChildItem models\xgb_optuna.*Get-ChildItem models\tabnet_best.*
Get-ChildItem outputs\02_training\optuna_study_*.db
Get-ChildItem outputs\02_training\optuna_*_trials.csv
Get-ChildItem outputs\02_training\*_cv_scores.csv
```

Expected: all files present.

If a verification fails, capture the full output and paste into the team
channel. Do not attempt to fix.

---

## 11. What Kenneth Reports

After each model's training run completes, Kenneth posts the following
in the team channel.

### After XGBoost

> XGBoost training complete.
>
> - Wall time: X hours Y minutes
> - Best trial: N
> - CV mean Macro F1: X.XXXX
> - CV std: X.XXXX
> - U2R recall: X.XX
> - R2L recall: X.XX
> - Artifacts verified: `models/xgb_optuna.joblib`, `models/xgb_optuna.meta.json`, `outputs/02_training/optuna_xgb_trials.csv`

### After TabNet

> TabNet training complete.
>
> - Wall time: X hours Y minutes
> - Best trial: N
> - CV mean Macro F1: X.XXXX
> - CV std: X.XXXX
> - U2R recall: X.XX
> - R2L recall: X.XX
> - Artifacts verified: `models/tabnet_best.zip`, `models/tabnet_best.meta.json`, `outputs/02_training/optuna_tabnet_trials.csv`

Kenneth does not interpret the metrics or suggest changes. Kenneth
reports numbers. Kit and Markie interpret.

---

## 12. What Kenneth Must Not Do

| Prohibited action | Reason |
|---|---|
| Modify `src/models.py` | Frozen for Phase 3 |
| Modify Notebook 02 cells | Calls frozen functions |
| Read `X_test.npy` or `y_test.npy` | Test-set access only in Notebook 03 |
| Evaluate on the test set | Same reason |
| Commit models or artifacts | Kit handles commits |
| Retry a failed cell without reporting | Kit needs the traceback |
| Change trial counts or hyperparameters | Specified by Kit |
| Terminate a long trial | Even slow trials contribute information |
| Run two training cells simultaneously | Resource contention distorts timing |
| Skip the save cell after a tuning cell | Model is not persisted |

---

## 13. Coordination

Kenneth coordinates with Kit on the following:

- **Before starting:** confirm the machine is available for the full duration of the run.
- **After each model:** post the summary block from section 11.
- **On any error:** paste the traceback and stop.
- **Before re-running any cell:** wait for Kit's guidance.

Kit coordinates with Kenneth on the following:

- **Trial budget changes:** if Kit adjusts budgets, Kenneth is notified before the run.
- **Code changes:** if Kit patches `src/models.py`, Kenneth re-pulls before running.
- **Schedule:** Kit sets the target window for each run.

---

## 14. Timeline

Assumes a fresh start on Day 3 of the sprint.

| Day | Activity | Wall time |
|---|---|---|
| Day 3 evening | XGBoost run | 4–6 hours |
| Day 4 morning | XGBoost verification and report | 15 minutes |
| Day 4 evening | TabNet run | 6–8 hours |
| Day 5 morning | TabNet verification and report | 15 minutes |
| Day 5 morning | Notebook 02 Cell 11 comparison | 5 minutes |

Kenneth completes Phase 3 execution work by end of Day 5.

---

## 15. Change Control

This spec is frozen for the sprint. Any change requires:

1. A pull request that modifies this file.
2. A corresponding note in `docs/reports/`.
3. Kit's approval as the spec's owner.

If a change to `src/models.py` is required, Kit makes the change,
Kenneth re-pulls, and Kenneth re-runs from the affected cell.

---

## 16. Verification Checklist

Kenneth runs through this checklist before beginning any training run.

- [ ] `.venv` active, Python 3.11.9 confirmed
- [ ] `python src/verify_env.py` prints PASSED
- [ ] Data integrity check (section 3.2) passes
- [ ] Notebook 02 opens, path-fix cell runs
- [ ] Cells 1–4 complete without error
- [ ] Machine has been restarted or closed to free RAM
- [ ] Sleep and hibernate timers disabled (section 7.1)
- [ ] No other heavy applications running
- [ ] Enough disk space free in `outputs/02_training/`
- [ ] A note has been posted in the team channel that training is starting

After the checklist passes, Kenneth runs Cell 5 (or 7 or 9, depending
on which model is being trained) and monitors as described.
