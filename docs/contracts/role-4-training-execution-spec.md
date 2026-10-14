# XGBoost Training Execution Specification

**Owner of the execution process:** Kit Dustin (Role 1) — reassigned
from Kenneth (Role 4) on Day 6. See
`docs/decision/decision_role4_xgboost_reassignment_20261014.md`.
**Owner of this specification:** Kit (Role 1)
**Effective date:** Day 5 of the 10-day sprint
**Status:** Frozen for the sprint. Changes require a PR and Kit's
sign-off.
**Related documents:**
- `docs/contracts/role-5-training-execution-spec.md` — TabNet execution
- `docs/contracts/api_data_contract.md` — feature ordering and payloads
- `docs/contracts/artifact_transfer_policy.md` — meta sidecar and CSV transfer procedure
- `docs/README.md` — documentation hierarchy and escalation
- `docs/decision/Decision Template.md` — how to raise a decision
- `docs/SETUP.md` — prerequisite onboarding guide

---

## 1. Purpose

This document is the authoritative specification for how the XGBoost
training run in Notebook 02 is executed. The original executor was
Kenneth (Role 4). Execution was reassigned to Kit Dustin (Role 1) on
Day 6 of the sprint.

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
| Running Notebook 02 Cells 7 and 8 (XGBoost) | Executor |
| Monitoring XGBoost training output | Executor |
| Reporting anomalies to Kit | Executor |
| Writing Cells 7 and 8 in Notebook 02 | Kit — the executor runs them as written |
| Not modifying `src/models.py` | Anyone — frozen for Phase 3 |
| Not modifying Cells 5, 6, 9, or 10 of Notebook 02 | Executor — those are Amber's and Dwayne's |
| Not evaluating on the test set | Anyone — test evaluation happens in Notebook 03 |
| Not running Cells 5, 6, 9, or 10 | Executor — those belong to Amber and Dwayne |

The executor does not write code. The executor runs code that Kit has
written and verified. If a cell fails, the executor reports the error;
the executor does not attempt to fix it.

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
- Confirm Cells 3 and 4 run without error. Cell 3 loads the arrays
  and encodes the labels. Cell 4 asserts the class order.
- **Do not run Cells 5 or 6.** Those are Amber's Random Forest cells.
- **Do not run Cells 9 or 10.** Those are Dwayne's TabNet cells.

If any of Cells 2 through 4 fail, stop and paste the error into the
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

The executor runs exactly two cells.

| Order | Cell | Task | Duration |
|---|---|---|---|
| 1 | Cell 7 | XGBoost tuning | 4–6 hours |
| 2 | Cell 8 | XGBoost save | under 1 minute |

Cell 8 must be run immediately after Cell 7, in the same session, or
the trained model will not be persisted.

**Critical rule:** do not close the notebook between Cell 7 and Cell 8.
If the session ends accidentally, re-run Cell 7 from scratch. Partial
models are not recoverable.

The executor does not run Cells 5, 6, 9, or 10. They belong to Amber
and Dwayne, and running them on the executor's machine would duplicate
or conflict with artifacts on other machines.

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
   full cleaned training pool with early stopping disabled. The number
   of boosting rounds is fixed to the best trial's `n_estimators`.
8. The final model, its meta sidecar, the trial log, and the fold
   scores are written to disk.

### 5.2 Expected console output

At the start, the cell prints:

```
XGBoost CV Macro F1: <value>
```

Optuna is configured at WARNING log level and does not print per-trial
progress to stdout. During the run the terminal appears idle except
for the initial notification.

To monitor progress without terminal output, watch the SQLite study
database:

```powershell
Get-ChildItem outputs\02_training\optuna_study_xgb.db |
    Select-Object LastWriteTime, Length
```

The file's modification time advances after each completed trial. A
stalled study shows no modification for over 90 minutes.

### 5.3 Expected duration

| Machine state | Duration |
|---|---|
| Fresh boot, nothing else running | 4 to 5 hours |
| Normal background load | 5 to 6 hours |
| Heavy load (browsers, video calls, etc.) | 6 to 8 hours |

If the run exceeds 10 hours, something is wrong. See section 7.

### 5.4 Monitoring during the run

Because Optuna is at WARNING level, per-trial lines do not appear in
the terminal. Check the SQLite file every 30 to 45 minutes as shown
in section 5.2.

If the file has not been modified for over 90 minutes and CPU usage is
near zero, the run has stalled. See section 7.1.

### 5.5 Required Notebook Cell Content

Cells 7 and 8 of `notebooks/02_Model_Training.ipynb` must contain
exactly the following code. No additions, no reordering, no changes.

#### Cell 7 — XGBoost Tuning

```python
# XGBoost training (Kit, Role 4 — reassigned from Kenneth)
# Contract: docs/contracts/role-4-training-execution-spec.md
# Estimated wall time: 4 to 6 hours

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
# XGBoost artifact verification (Kit, Role 4 — reassigned from Kenneth)

assert (PATHS.models / "xgb_optuna.joblib").is_file(), "XGBoost model missing"
assert (PATHS.models / "xgb_optuna.meta.json").is_file(), "XGBoost meta missing"
print("XGBoost artifacts verified.")
```

Rationale: the arrays `X_train`, `y_train`, and `class_order` are
provided by shared setup Cells 3 and 4. Cell 7 calls `train_xgb`
directly. If the executor or any future executor modifies these cells,
the resulting model diverges from the reference and the change must be
raised as a decision.

---

## 6. Handling Interruptions and Machine State

### 6.1 Laptop sleep or shutdown during training

If the machine sleeps during the run, the process is usually paused
but not killed. On wake, the run continues from where it left off.
Verify by checking that the SQLite study database's modification time
advances.

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

The executor does not need to coordinate timing with Dwayne. If the
two runs happen to be on the same home network, no shared resource is
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
print('U2R recall  :', meta['per_class_recall_train']['u2r'])
print('R2L recall  :', meta['per_class_recall_train']['r2l'])
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

### 9.3 Artifact transfer

After verification passes, the executor pushes the three artifact
files to an artifact branch per
`docs/contracts/artifact_transfer_policy.md` section 5:

- `models/xgb_optuna.meta.json`
- `outputs/02_training/optuna_xgb_trials.csv`
- `outputs/02_training/xgb_cv_scores.csv`

The binary `models/xgb_optuna.joblib` is not pushed. It is uploaded to
the shared drive per
`docs/contracts/artifact_transfer_policy.md` section 8.

---

## 10. What the Executor Reports

After the XGBoost run completes, the executor posts the following in
the team channel.

> XGBoost training complete.
>
> - Wall time: X hours Y minutes
> - Best trial: N
> - CV mean Macro F1: X.XXXX
> - CV std: X.XXXX
> - U2R recall (train pool): X.XX
> - R2L recall (train pool): X.XX
> - Artifacts verified: `models/xgb_optuna.joblib`,
>   `models/xgb_optuna.meta.json`,
>   `outputs/02_training/optuna_xgb_trials.csv`
>
> Note: `per_class_recall_train` measures recall on the training pool
> after the refit. It is not a generalization metric. Test-set recall
> is produced by Notebook 03.

The executor does not interpret the metrics or suggest changes. The
executor reports numbers. Kit and Markie interpret.

---

## 11. What the Executor Must Not Do

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

The executor coordinates with Kit on the following:

- **Before starting:** confirm the machine is available for the full
  duration of the run.
- **After the run:** post the summary block from section 10.
- **On any error:** paste the traceback and stop.
- **Before re-running Cell 7:** wait for Kit's guidance.

Kit coordinates with the executor on the following:

- **Trial budget changes:** if Kit adjusts budgets, the executor is
  notified before the run.
- **Code changes:** if Kit patches `src/models.py`, the executor
  re-pulls before running.
- **Schedule:** Kit sets the target window for the run.

The executor does not coordinate directly with Dwayne. Any conflict
between the two execution owners is resolved by Kit.

---

## 13. Timeline

| Day | Activity | Wall time |
|---|---|---|
| Day 5 morning | Complete pre-run checklist | 30 minutes |
| Day 5 evening | XGBoost run (Cell 7) | 4 to 6 hours |
| Day 6 morning | XGBoost save (Cell 8) | under 1 minute |
| Day 6 morning | Post-run verification and report | 15 minutes |

The executor completes the XGBoost execution portion of Phase 3 by end
of Day 6.

---

## 14. Change Control

This spec is frozen for the sprint. Any change requires:

1. A pull request that modifies this file.
2. A corresponding note in `docs/reports/`.
3. Kit's approval as the spec's owner.

If a change to `src/models.py` is required, Kit makes the change, the
executor re-pulls, and the executor re-runs from the affected cell.

If the executor encounters an ambiguity not covered by this spec, the
escalation path is `docs/README.md` section 10 and the decision
template at `docs/decision/Decision Template.md`. Do not improvise.

---

## 15. Verification Checklist

The executor runs through this checklist before beginning the training
run.

- [ ] `.venv` active, Python 3.11.9 confirmed
- [ ] `python src/verify_env.py` prints PASSED
- [ ] Data integrity check (section 3.2) passes
- [ ] Notebook 02 opens, path-fix cell runs
- [ ] Cells 3 and 4 complete without error
- [ ] Cells 7 and 8 contain exactly the code in section 5.5
- [ ] Machine has been restarted or RAM freed within the last 6 hours
- [ ] Sleep and hibernate timers disabled (section 6.1)
- [ ] No other heavy applications running
- [ ] Enough disk space free in `outputs/02_training/`
- [ ] A note has been posted in the team channel that training is
      starting

After the checklist passes, the executor runs Cell 7 and monitors as
described in section 5.4.

---

## 16. Ownership History

| Date | Owner | Change |
|---|---|---|
| Day 5 | Kenneth (Role 4) | Initial assignment |
| Day 6 | Kit Dustin (Role 1) | Reassigned due to Kenneth's unavailability |

The reassignment is documented in
`docs/decision/decision_role4_xgboost_reassignment_20261014.md`. The
technical specification (sections 1 through 15) was not modified by
the reassignment. Only the executor identity changed.

See also `docs/contracts/artifact_transfer_policy.md` for the
procedure the executor follows after the training run completes.

--END OF DOCUMENT--