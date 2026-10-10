# XGBoost Training Execution Specification

**Owner of the execution process:** Kenneth (Role 4)
**Owner of this specification:** Kit (Role 1)
**Effective date:** Day 5 of the 10-day sprint
**Status:** Frozen for the sprint. Changes require a PR and Kit's
sign-off.
**Related documents:**
- `docs/contracts/role-5-training-execution-spec.md` — TabNet execution
- `docs/contracts/api_data_contract.md` — feature ordering and payloads
- `docs/README.md` — documentation hierarchy and escalation
- `docs/decision/Decision Template.md` — how to raise a decision
- `docs/SETUP.md` — prerequisite onboarding guide
  
---

## 1. Purpose

This document is the authoritative specification for how Kenneth
executes the XGBoost training run in Notebook 02. It defines what to
run, in what order, expected duration, how to monitor progress, how to
intervene when something goes wrong, and what to report back.

The specification exists so that the XGBoost run happens reliably,
without guesswork, and without risk of accidental test-set exposure or
partial artifacts.

TabNet execution is covered separately in
`docs/contracts/role-5-training-execution-spec.md` and is not the
responsibility of Role 4.

---

## 2. Responsibility Boundary

| Item | Owner |
|---|---|
| Running Notebook 02 Cells 7 and 8 (XGBoost) | Kenneth |
| Monitoring XGBoost training output | Kenneth |
| Reporting anomalies to Kit | Kenneth |
| Writing Cells 7 and 8 in Notebook 02 | Kit — Kenneth executes them as written |
| Not modifying `src/models.py` | Anyone — frozen for Phase 3 |
| Not modifying Cells 5, 6, 9, or 10 of Notebook 02 | Kenneth — those are Amber's and Dwayne's |
| Not evaluating on the test set | Anyone — test evaluation happens in Notebook 03 |
| Not running Cells 5, 6, 9, or 10 | Kenneth — those belong to Amber and Dwayne |

Kenneth does not write code. Kenneth executes code that Kit has written
and verified. If a cell fails, Kenneth reports the error; Kenneth does
not attempt to fix it.

---

## 3. Prerequisites

Before starting the run, verify all of the following.

### 3.1 Environment

- Python 3.11.9 running inside `.venv`
- `requirements.txt` fully installed
- All critical packages import without error. Test with:
  `python src/verify_env.py`. Expected final line:
  `RESULT: Phase 1 environment verification PASSED.`
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

Before opening the notebook, confirm that `docs/SETUP.md` sections 1
through 10 are complete. In particular:

- `python src/verify_env.py` prints `RESULT: Phase 1 environment
  verification PASSED.`
- `data/processed/` exists with all expected files.
- The four frozen hashes print `OK`.

Then:

- Open `notebooks/02_Model_Training.ipynb`
- Confirm the path-fix cell (Cell 2) runs and prints the repository
  root
- Confirm Cells 1 through 4 run without error
- **Do not run Cells 5 or 6.** Those are Amber's Random Forest cells.
- **Do not run Cells 9 or 10.** Those are Dwayne's TabNet cells.

If any of Cells 1 through 4 fail, stop and paste the error into the
team channel.

### 3.4 Machine State

- Laptop has been restarted or RAM has been freed within the last 6
  hours
- Sleep and hibernate timers disabled for the duration of the run
  (see section 6.1)
- No other heavy applications running (browsers with many tabs, video
  editors, other training jobs)
- Laptop is on a hard surface with airflow

---

## 4. Run Sequence

Kenneth runs exactly two cells.

| Order | Cell | Task | Duration |
|---|---|---|---|
| 1 | Cell 7 | XGBoost tuning | 4–6 hours |
| 2 | Cell 8 | XGBoost save | under 1 minute |

Cell 8 must be run immediately after Cell 7, in the same session, or
the trained model will not be persisted.

**Critical rule:** do not close the notebook between Cell 7 and Cell 8.
If the session ends accidentally, re-run Cell 7 from scratch. Partial
models are not recoverable.

Kenneth does not run Cells 5, 6, 9, or 10. They belong to Amber and
Dwayne, and running them on Kenneth's machine would duplicate or
conflict with artifacts on other machines.

---

## 5. Running the XGBoost Cells

### 5.1 What the tuning cell does

Cell 7 calls `train_xgb()` from `src/models.py`. That function performs
the following sequence:

1. Runs an Optuna study with 30 trials.
2. Each trial performs 5-fold stratified cross-validation.
3. Inside each fold, Tomek Links is applied only to the training
   partition. The validation partition is never resampled.
4. Class weights are computed from the post-Tomek-Links training
   partition and passed to the model as per-sample weights.
5. The objective is Macro F1, averaged across the 5 folds.
6. Trials whose running fold mean falls below the median are pruned.
7. After the study completes, the best configuration is refit on the
   full cleaned training pool.
8. The final model, its meta sidecar, the trial log, and the fold
   scores are written to disk.

### 5.2 Expected console output

At the start, the cell prints:

```
Training XGBoost...
Running 30 Optuna trials with 5-fold CV each.
Estimated wall time: 4 to 6 hours.
```

During training, Optuna prints one trial summary per completed trial:

```
[I 2026-10-05 08:12:31,072] Trial 0 finished with value: 0.8842 and parameters: {...}.
[I 2026-10-05 08:25:14,331] Trial 1 finished with value: 0.8891 and parameters: {...}.
[I 2026-10-05 08:37:52,011] Trial 2 finished with value: 0.8913 and parameters: {...}.
...
```

At the end, the cell prints a summary block:

```
XGBoost study complete.
Best trial: 17
Best CV Macro F1: 0.9012
Final model refit on the full cleaned training pool.
Saved: models/xgb_optuna.joblib
Saved: models/xgb_optuna.meta.json
Saved: outputs/02_training/optuna_xgb_trials.csv
Saved: outputs/02_training/xgb_cv_scores.csv
```

The exact numbers will differ. The structure of the output will not.

### 5.3 Expected duration

| Machine state | Duration |
|---|---|
| Fresh boot, nothing else running | 4 to 5 hours |
| Normal background load | 5 to 6 hours |
| Heavy load (browsers, video calls, etc.) | 6 to 8 hours |

If the run exceeds 10 hours, something is wrong. See section 7.

### 5.4 Monitoring during the run

The cell output refreshes as each trial completes. Check in every 30
to 45 minutes and note three values:

- Which trial number is currently running
- The best score so far
- Whether the best score is still improving across trials

If the best score has not changed in the last 10 trials, that is
normal. Optuna's TPE sampler concentrates on promising regions and
often plateaus near the end. Continue to completion.

### 5.5 Required Notebook Cell Content

Cells 7 and 8 of `notebooks/02_Model_Training.ipynb` must contain
exactly the following code. No additions, no reordering, no changes.

#### Cell 7 — XGBoost Tuning

```python
import json
import numpy as np
from src.models import (
    load_processed_arrays,
    encode_labels,
    train_xgb,
)
from src.utils import PATHS, RANDOM_STATE, set_seed

set_seed(RANDOM_STATE)

X_train, y_train_str, _, _, class_order = load_processed_arrays()
y_train = encode_labels(y_train_str, class_order)

assert class_order == ["normal", "dos", "probe", "r2l", "u2r"], (
    f"Class order mismatch: {class_order}"
)

xgb_result = train_xgb(
    X_train=X_train,
    y_train=y_train,
    class_order=class_order,
    n_trials=30,
    n_folds=5,
)
print("XGBoost CV Macro F1:", xgb_result["cv_mean_macro_f1"])
```

#### Cell 8 — XGBoost Save Verification

```python
from src.utils import PATHS

assert (PATHS.models / "xgb_optuna.joblib").is_file(), "Model missing"
assert (PATHS.models / "xgb_optuna.meta.json").is_file(), "Meta missing"
print("XGBoost artifacts verified.")
```

Rationale: pinning the cell bodies removes any ambiguity about how the
arrays are loaded, how the labels are encoded, and how `train_xgb` is
invoked. If Kenneth or any future executor modifies these cells, the
resulting model diverges from the reference and the change must be
raised as a decision.

---

## 6. Handling Interruptions and Machine State

### 6.1 Laptop sleep or shutdown during training

If the machine sleeps during the run, the process is usually paused
but not killed. On wake, the run continues from where it left off.
Verify by checking that Optuna still prints trial summaries.

If the machine shuts down, the process is killed. On restart:

1. Check `outputs/02_training/optuna_study_xgb.db` for completed
   trials.
2. If the study database exists and has trials, the study can be
   resumed by re-running Cell 7.
3. If the study database does not exist or is empty, the run must be
   restarted from scratch.

**Prevention:** disable sleep for the duration of the run.

```powershell
powercfg /change standby-timeout-ac 0
powercfg /change hibernate-timeout-ac 0
```

Reverse after training:

```powershell
powercfg /change standby-timeout-ac 30
powercfg /change hibernate-timeout-ac 60
```

### 6.2 Cell execution error mid-run

If a cell raises an exception, the training stops. Capture the full
traceback and paste it in the team channel. Do not attempt to modify
the code.

### 6.3 Machine crash or restart

If the machine reboots unexpectedly:

1. Check which artifacts exist in `models/` and `outputs/02_training/`.
2. Report the current state to Kit.
3. Wait for Kit's guidance before re-running.

### 6.4 Coexistence With the TabNet Run

Dwayne runs the TabNet cells on a different machine. The two runs are
independent and do not conflict:

- XGBoost writes to `models/xgb_optuna.*` and
  `outputs/02_training/optuna_study_xgb.db`.
- TabNet writes to `models/tabnet_best.*` and
  `outputs/02_training/optuna_study_tabnet.db`.

Kenneth does not need to coordinate timing with Dwayne. If the two
runs happen to be on the same home network, no shared resource is
contended.

---

## 7. Failure Modes and Diagnostics

### 7.1 A trial taking more than 30 minutes

Normal trial time is 8 to 12 minutes.

A single trial exceeding 30 minutes indicates either an unusually deep
tree configuration or a machine resource issue. Do not intervene. Let
the trial complete. Optuna will log it and move on.

If three consecutive trials exceed 30 minutes, stop and report to Kit.

### 7.2 Out of memory errors

Symptom: `MemoryError` or the process being killed by the operating
system.

Actions:

1. Close all other applications.
2. Free RAM by restarting the notebook kernel.
3. Re-run Cell 7 from the beginning.
4. If the error recurs on a fresh session, report to Kit.

### 7.3 Disk full

Symptom: SQLite write errors, or failure to write `.joblib`.

Actions:

1. Check free space:

```powershell
Get-PSDrive C | Select-Object Used, Free
```

2. If under 2 GB free, empty the recycle bin, clear temp files, and
   retry.
3. If under 500 MB free, stop training and report to Kit.

### 7.4 Loss of network connectivity

Training runs locally and does not require internet. Network loss does
not affect training. Ignore.

### 7.5 CPU fan noise

Normal during training. Ensure the laptop is on a hard surface with
airflow. Do not place it on a bed or cushion. If the machine shuts
down from thermal protection, see section 6.3.

---

## 8. Expected Console Anomalies (Not Errors)

The following messages are expected and should be ignored.

| Message | Meaning |
|---|---|
| `UserWarning: Could not find the number of physical cores` | Cosmetic. Harmless. |
| `FutureWarning` from scikit-learn | Cosmetic. Note the message and continue. |
| `ConvergenceWarning` | Possibly serious. Report to Kit. |

Any line starting with `Traceback (most recent call last):` is a real
error. Stop and report.

---

## 9. Post-Run Verification

After Cell 8 completes, run the following checks.

### 9.1 Model and meta

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

### 9.2 File existence

```powershell
Get-ChildItem models\xgb_optuna.joblib
Get-ChildItem models\xgb_optuna.meta.json
Get-ChildItem outputs\02_training\optuna_study_xgb.db
Get-ChildItem outputs\02_training\optuna_xgb_trials.csv
Get-ChildItem outputs\02_training\xgb_cv_scores.csv
```

Expected: all files present.

If a verification fails, capture the full output and paste into the
team channel. Do not attempt to fix.

---

## 10. What Kenneth Reports

After the XGBoost run completes, Kenneth posts the following in the
team channel.

> XGBoost training complete.
>
> - Wall time: X hours Y minutes
> - Best trial: N
> - CV mean Macro F1: X.XXXX
> - CV std: X.XXXX
> - U2R recall: X.XX
> - R2L recall: X.XX
> - Artifacts verified: `models/xgb_optuna.joblib`,
>   `models/xgb_optuna.meta.json`,
>   `outputs/02_training/optuna_xgb_trials.csv`

Kenneth does not interpret the metrics or suggest changes. Kenneth
reports numbers. Kit and Markie interpret.

---

## 11. What Kenneth Must Not Do

| Prohibited action | Reason |
|---|---|
| Modify `src/models.py` | Frozen for Phase 3 |
| Modify Cells 5, 6, 9, or 10 of Notebook 02 | Those belong to Amber and Dwayne |
| Modify Cells 1 through 4 or Cells 11 and 12 | Those are shared and controlled by Kit |
| Read `X_test.npy` or `y_test.npy` | Test-set access only in Notebook 03 |
| Evaluate on the test set | Same reason |
| Run Cells 5, 6, 9, or 10 | Those belong to Amber and Dwayne |
| Commit models or artifacts to git | Kit handles commits |
| Retry a failed cell without reporting | Kit needs the traceback |
| Change trial counts or hyperparameters | Specified by Kit |
| Terminate a long trial | Even slow trials contribute information |
| Run other heavy applications during training | Resource contention distorts timing |
| Run the TabNet cells | Dwayne owns those |
| Run the Random Forest cells | Amber owns those |

---

## 12. Coordination

Kenneth coordinates with Kit on the following:

- **Before starting:** confirm the machine is available for the full
  duration of the run.
- **After the run:** post the summary block from section 10.
- **On any error:** paste the traceback and stop.
- **Before re-running Cell 7:** wait for Kit's guidance.

Kit coordinates with Kenneth on the following:

- **Trial budget changes:** if Kit adjusts budgets, Kenneth is notified
  before the run.
- **Code changes:** if Kit patches `src/models.py`, Kenneth re-pulls
  before running.
- **Schedule:** Kit sets the target window for the run.

Kenneth does not coordinate directly with Dwayne. Any conflict between
the two execution owners is resolved by Kit.

---

## 13. Timeline

| Day | Activity | Wall time |
|---|---|---|
| Day 5 morning | Complete pre-run checklist | 30 minutes |
| Day 5 evening | XGBoost run (Cell 7) | 4 to 6 hours |
| Day 6 morning | XGBoost save (Cell 8) | under 1 minute |
| Day 6 morning | Post-run verification and report | 15 minutes |

Kenneth completes the XGBoost execution portion of Phase 3 by end of
Day 6.

---

## 14. Change Control

This spec is frozen for the sprint. Any change requires:

1. A pull request that modifies this file.
2. A corresponding note in `docs/reports/`.
3. Kit's approval as the spec's owner.

If a change to `src/models.py` is required, Kit makes the change,
Kenneth re-pulls, and Kenneth re-runs from the affected cell.

If Kenneth encounters an ambiguity not covered by this spec, the
escalation path is `docs/README.md` section 10 and the decision
template at `docs/decision/Decision Template.md`. Do not improvise.

---

## 15. Verification Checklist

Kenneth runs through this checklist before beginning the training run.

- [ ] `.venv` active, Python 3.11.9 confirmed
- [ ] `python src/verify_env.py` prints PASSED
- [ ] Data integrity check (section 3.2) passes
- [ ] Notebook 02 opens, path-fix cell runs
- [ ] Cells 1 through 4 complete without error
- [ ] Cells 7 and 8 contain exactly the code in section 5.5
- [ ] Machine has been restarted or RAM freed within the last 6 hours
- [ ] Sleep and hibernate timers disabled (section 6.1)
- [ ] No other heavy applications running
- [ ] Enough disk space free in `outputs/02_training/`
- [ ] A note has been posted in the team channel that training is
      starting

After the checklist passes, Kenneth runs Cell 7 and monitors as
described in section 5.4.
