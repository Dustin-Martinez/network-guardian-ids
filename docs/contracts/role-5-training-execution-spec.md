# TabNet Training Execution Specification

**Owner of the execution process:** Dwayne (Role 5)
**Owner of this specification:** Kit (Role 1)
**Effective date:** Day 5 of the 10-day sprint
**Status:** Frozen for the sprint. Changes require a PR and Kit's
sign-off.
**Related documents:**
- `docs/contracts/role-4-training-execution-spec.md` — XGBoost execution
- `docs/contracts/api_data_contract.md` — feature ordering and payloads
- `docs/README.md` — documentation hierarchy and escalation
- `docs/decision/Decision Template.md` — how to raise a decision
- `docs/SETUP.md` — prerequisite onboarding guide

---

## 1. Purpose

This document is the authoritative specification for how Dwayne
executes the TabNet training run in Notebook 02. It defines what to
run, in what order, expected duration, how to monitor progress, how to
intervene when something goes wrong, and what to report back.

The specification exists so that the TabNet run happens reliably,
without guesswork, and without risk of accidental test-set exposure or
partial artifacts.

XGBoost execution is covered separately in
`docs/contracts/role-4-training-execution-spec.md` and is not the
responsibility of Role 5 for training.

---

## 2. Responsibility Boundary

| Item | Owner |
|---|---|
| Running Notebook 02 Cells 9 and 10 (TabNet) | Dwayne |
| Monitoring TabNet training output | Dwayne |
| Reporting anomalies to Kit | Dwayne |
| Writing Cells 9 and 10 in Notebook 02 | Kit — Dwayne executes them as written |
| Not modifying `src/models.py` | Anyone — frozen for Phase 3 |
| Not modifying Cells 5, 6, 7, or 8 of Notebook 02 | Dwayne — those are Amber's and Kenneth's |
| Not modifying Cells 1 through 4 or Cells 11 and 12 | Those are shared and controlled by Kit |
| Not evaluating on the test set | Anyone — test evaluation happens in Notebook 03 |
| Not running Cells 5, 6, 7, or 8 | Dwayne — those belong to Amber and Kenneth |

Dwayne does not write code for the model. Dwayne executes code that Kit
has written and verified. If a cell fails, Dwayne reports the error;
Dwayne does not attempt to fix it.

Dwayne does write code for the evaluation and explainability phases
(Phases 3, 4, and 5 of `docs/tasks/5.md`). Those are separate from this
execution contract and are governed by the respective sections of the
Task 5 mandate.

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
- **Do not run Cells 7 or 8.** Those are Kenneth's XGBoost cells.

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
- Laptop is plugged into power (TabNet runs 6 to 8 hours continuously)

---

## 4. Run Sequence

Dwayne runs exactly two cells.

| Order | Cell | Task | Duration |
|---|---|---|---|
| 1 | Cell 9 | TabNet tuning | 6–8 hours |
| 2 | Cell 10 | TabNet save | under 1 minute |

Cell 10 must be run immediately after Cell 9, in the same session, or
the trained model will not be persisted.

**Critical rule:** do not close the notebook between Cell 9 and Cell
10. If the session ends accidentally, re-run Cell 9 from scratch.
Partial models are not recoverable.

Dwayne does not run Cells 5, 6, 7, or 8. They belong to Amber and
Kenneth, and running them on Dwayne's machine would duplicate or
conflict with artifacts on other machines.

---

## 5. Running the TabNet Cells

### 5.1 What the tuning cell does

Cell 9 calls `train_tabnet()` from `src/models.py`. That function
performs the following sequence:

1. Runs an Optuna study with 20 trials.
2. Each trial performs 3-fold stratified cross-validation.
3. Inside each fold, Tomek Links is applied only to the training
   partition. The validation partition is never resampled.
4. Class weights are computed from the post-Tomek-Links training
   partition and passed to the model as a per-class weight dictionary
   via the `weights` argument of `TabNetClassifier.fit`.
5. The objective is Macro F1, averaged across the 3 folds.
6. Trials whose running fold mean falls below the median are pruned.
7. After the study completes, the best configuration is refit on the
   full cleaned training pool.
8. The final model, its meta sidecar, the trial log, and the fold
   scores are written to disk. The model is saved in TabNet's native
   `.zip` format, which encapsulates the state dict, constructor
   parameters, optimizer state, and training history.

The fold count is 3 for TabNet, not 5 as with XGBoost. This is
deliberate. With only 39 U2R training examples, 5-fold would leave
approximately 7 U2R per validation fold, which is too few for a
stable per-class recall estimate. The reduction to 3-fold is
documented in the Phase 3 report section 5.3.

### 5.2 Expected console output

At the start, the cell prints:

```
Training TabNet...
Running 20 Optuna trials with 3-fold CV each.
Estimated wall time: 6 to 8 hours.
This run is CPU-bound and will produce heavy CPU load.
```

During training, pytorch-tabnet's per-epoch progress output is
suppressed because `verbose=0` is set in `build_tabnet`. Optuna prints
one trial summary per completed trial:

```
[I 2026-10-06 02:15:44,912] Trial 0 finished with value: 0.8612 and parameters: {...}.
[I 2026-10-06 02:48:19,233] Trial 1 finished with value: 0.8734 and parameters: {...}.
[I 2026-10-06 03:22:11,554] Trial 2 finished with value: 0.8801 and parameters: {...}.
...
```

At the end, the cell prints a summary block:

```
TabNet study complete.
Best trial: 11
Best CV Macro F1: 0.8911
Final model refit on the full cleaned training pool.
Saved: models/tabnet_best.zip
Saved: models/tabnet_best.meta.json
Saved: outputs/02_training/optuna_tabnet_trials.csv
Saved: outputs/02_training/tabnet_cv_scores.csv
```

The exact numbers will differ. The structure of the output will not.

### 5.3 Expected duration

| Machine state | Duration |
|---|---|
| Fresh boot, nothing else running | 6 to 7 hours |
| Normal background load | 7 to 8 hours |
| Heavy load (browsers, video calls, etc.) | 9 to 10 hours |

TabNet is CPU-intensive. During the run, expect:

- CPU usage near 100% on all available cores
- Audible fan noise
- The machine may be sluggish for any other work
- Do not run other heavy applications during this window

If the run exceeds 12 hours, something is wrong. See section 7.

### 5.4 Monitoring during the run

TabNet trials are longer than XGBoost trials. Check in every 60 to 90
minutes. The key signals are:

- Optuna continues to print trial summaries
- CPU usage remains near 100%

If nothing prints for over 90 minutes and CPU usage is still high, the
run is working on a slow trial. This is expected occasionally.

If nothing prints for over 120 minutes AND CPU usage is near zero, the
run has stalled. See section 7.1.

### 5.5 Required Notebook Cell Content

Cells 9 and 10 of `notebooks/02_Model_Training.ipynb` must contain
exactly the following code. No additions, no reordering, no changes.

#### Cell 9 — TabNet Tuning

```python
import json
import numpy as np
from src.models import (
    load_processed_arrays,
    encode_labels,
    train_tabnet,
)
from src.utils import PATHS, RANDOM_STATE, set_seed

set_seed(RANDOM_STATE)

X_train, y_train_str, _, _, class_order = load_processed_arrays()
y_train = encode_labels(y_train_str, class_order)

assert class_order == ["normal", "dos", "probe", "r2l", "u2r"], (
    f"Class order mismatch: {class_order}"
)

tabnet_result = train_tabnet(
    X_train=X_train,
    y_train=y_train,
    class_order=class_order,
    n_trials=20,
    n_folds=3,
)
print("TabNet CV Macro F1:", tabnet_result["cv_mean_macro_f1"])
```

#### Cell 10 — TabNet Save Verification

```python
from src.utils import PATHS

assert (PATHS.models / "tabnet_best.zip").is_file(), "Model missing"
assert (PATHS.models / "tabnet_best.meta.json").is_file(), "Meta missing"
print("TabNet artifacts verified.")
```

Rationale: pinning the cell bodies removes any ambiguity about how the
arrays are loaded, how the labels are encoded, and how `train_tabnet`
is invoked. If Dwayne or any future executor modifies these cells, the
resulting model diverges from the reference and the change must be
raised as a decision.

---

## 6. Handling Interruptions and Machine State

### 6.1 Laptop sleep or shutdown during training

If the machine sleeps during the run, the process is usually paused
but not killed. On wake, the run continues from where it left off.
Verify by checking that Optuna still prints trial summaries.

If the machine shuts down, the process is killed. On restart:

1. Check `outputs/02_training/optuna_study_tabnet.db` for completed
   trials.
2. If the study database exists and has trials, the study can be
   resumed by re-running Cell 9.
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

### 6.4 Coexistence With the XGBoost Run

Kenneth runs the XGBoost cells on a different machine. The two runs
are independent and do not conflict:

- TabNet writes to `models/tabnet_best.*` and
  `outputs/02_training/optuna_study_tabnet.db`.
- XGBoost writes to `models/xgb_optuna.*` and
  `outputs/02_training/optuna_study_xgb.db`.

Dwayne does not need to coordinate timing with Kenneth. If the two
runs happen to be on the same home network, no shared resource is
contended.

### 6.5 Laptop Power

TabNet runs for 6 to 8 hours continuously and consumes near-100% CPU
for the duration. Plug the laptop into power before starting. Running
on battery will not survive the full training window, and a mid-run
battery shutdown is treated the same as a machine crash (section 6.3).

---

## 7. Failure Modes and Diagnostics

### 7.1 A trial taking more than 90 minutes

Normal trial time is 20 to 30 minutes.

A single trial exceeding 90 minutes is unusual. Do not intervene
unless CPU usage drops to near zero. If CPU is idle for more than 10
minutes during a TabNet trial, the process has stalled. Stop the cell
and report.

### 7.2 Out of memory errors

Symptom: `MemoryError` or the process being killed by the operating
system.

Actions:

1. Close all other applications.
2. Free RAM by restarting the notebook kernel.
3. Re-run Cell 9 from the beginning.
4. If the error recurs on a fresh session, report to Kit. Memory
   constraints may require reducing the trial budget, which is a
   decision Kit must make before re-running.

### 7.3 Disk full

Symptom: SQLite write errors, or failure to write the `.zip` model
file.

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

### 7.5 Fan noise and high CPU temperature

Normal during TabNet runs. Ensure the laptop is on a hard surface with
airflow. Do not place it on a bed or cushion. If the machine shuts
down from thermal protection, see section 6.3.

---

## 8. Expected Console Anomalies (Not Errors)

The following messages are expected and should be ignored.

| Message | Meaning |
|---|---|
| `UserWarning: Could not find the number of physical cores` | Cosmetic. Harmless. |
| `Device used : cpu` | Expected. Running on CPU. |
| `Stop training because you reached max_epochs` | Normal TabNet early-stop message. Not an error. |
| `FutureWarning` from scikit-learn or pandas | Cosmetic. Note the message and continue. |
| `ConvergenceWarning` | Possibly serious. Report to Kit. |

Any line starting with `Traceback (most recent call last):` is a real
error. Stop and report.

---

## 9. Post-Run Verification

After Cell 10 completes, run the following checks.

### 9.1 Model and meta

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

Expected: model loads without error, CV Macro F1 in the range 0.80 to
0.92.

### 9.2 File existence

```powershell
Get-ChildItem models\tabnet_best.zip
Get-ChildItem models\tabnet_best.meta.json
Get-ChildItem outputs\02_training\optuna_study_tabnet.db
Get-ChildItem outputs\02_training\optuna_tabnet_trials.csv
Get-ChildItem outputs\02_training\tabnet_cv_scores.csv
```

Expected: all files present.

If a verification fails, capture the full output and paste into the
team channel. Do not attempt to fix.

---

## 10. What Dwayne Reports

After the TabNet run completes, Dwayne posts the following in the team
channel.

> TabNet training complete.
>
> - Wall time: X hours Y minutes
> - Best trial: N
> - CV mean Macro F1: X.XXXX
> - CV std: X.XXXX
> - U2R recall: X.XX
> - R2L recall: X.XX
> - Artifacts verified: `models/tabnet_best.zip`,
>   `models/tabnet_best.meta.json`,
>   `outputs/02_training/optuna_tabnet_trials.csv`

Dwayne does not interpret the metrics or suggest changes. Dwayne
reports numbers. Kit and Markie interpret.

---

## 11. What Dwayne Must Not Do

| Prohibited action | Reason |
|---|---|
| Modify `src/models.py` | Frozen for Phase 3 |
| Modify Cells 5, 6, 7, or 8 of Notebook 02 | Those belong to Amber and Kenneth |
| Modify Cells 1 through 4 or Cells 11 and 12 | Those are shared and controlled by Kit |
| Read `X_test.npy` or `y_test.npy` | Test-set access only in Notebook 03 |
| Evaluate on the test set | Same reason |
| Run Cells 5, 6, 7, or 8 | Those belong to Amber and Kenneth |
| Commit models or artifacts to git | Kit handles commits |
| Retry a failed cell without reporting | Kit needs the traceback |
| Change trial counts or hyperparameters | Specified by Kit |
| Terminate a long trial | Even slow trials contribute information |
| Run other heavy applications during training | Resource contention distorts timing |
| Run the XGBoost cells | Kenneth owns those |
| Run the Random Forest cells | Amber owns those |

---

## 12. Coordination

Dwayne coordinates with Kit on the following:

- **Before starting:** confirm the machine is available for the full
  duration of the run.
- **After the run:** post the summary block from section 10.
- **On any error:** paste the traceback and stop.
- **Before re-running Cell 9:** wait for Kit's guidance.

Kit coordinates with Dwayne on the following:

- **Trial budget changes:** if Kit adjusts budgets, Dwayne is notified
  before the run.
- **Code changes:** if Kit patches `src/models.py`, Dwayne re-pulls
  before running.
- **Schedule:** Kit sets the target window for the run.

Dwayne does not coordinate directly with Kenneth. Any conflict between
the two execution owners is resolved by Kit.

---

## 13. Timeline

| Day | Activity | Wall time |
|---|---|---|
| Day 5 morning | Complete pre-run checklist | 30 minutes |
| Day 5 evening | TabNet run (Cell 9) | 6 to 8 hours |
| Day 6 morning | TabNet save (Cell 10) | under 1 minute |
| Day 6 morning | Post-run verification and report | 15 minutes |

Dwayne completes the TabNet execution portion of Phase 3 by end of
Day 6.

After the report is posted, Dwayne proceeds to Phase 3 of
`docs/tasks/5.md` (the evaluation suite). That is not covered by this
contract.

---

## 14. Change Control

This spec is frozen for the sprint. Any change requires:

1. A pull request that modifies this file.
2. A corresponding note in `docs/reports/`.
3. Kit's approval as the spec's owner.

If a change to `src/models.py` is required, Kit makes the change,
Dwayne re-pulls, and Dwayne re-runs from the affected cell.

If Dwayne encounters an ambiguity not covered by this spec, the
escalation path is `docs/README.md` section 10 and the decision
template at `docs/decision/Decision Template.md`. Do not improvise.

---

## 15. Verification Checklist

Dwayne runs through this checklist before beginning the training run.

- [ ] `.venv` active, Python 3.11.9 confirmed
- [ ] `python src/verify_env.py` prints PASSED
- [ ] Data integrity check (section 3.2) passes
- [ ] Notebook 02 opens, path-fix cell runs
- [ ] Cells 1 through 4 complete without error
- [ ] Cells 9 and 10 contain exactly the code in section 5.5
- [ ] Machine has been restarted or RAM freed within the last 6 hours
- [ ] Sleep and hibernate timers disabled (section 6.1)
- [ ] Laptop is plugged into power (section 6.5)
- [ ] No other heavy applications running
- [ ] Enough disk space free in `outputs/02_training/`
- [ ] A note has been posted in the team channel that training is
      starting

After the checklist passes, Dwayne runs Cell 9 and monitors as
described in section 5.4.
