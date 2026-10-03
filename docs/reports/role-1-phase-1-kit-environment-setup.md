# Phase 1 Report — Environment & Scaffolding

**Role:** Role 1 — Kit Dustin
**Title:** Project Manager, Data Preparation Engineer & Core Model Developer
**Phase:** 1 of 4
**Sprint Day:** Day 1 of 10
**Status:** Complete
**Branch:** `feature/role-1-phase-1-env-scaffolding`

---

## 1. Objective

Per `tasks/1.md` Phase 1, initialize the isolated Python environment,
install every dependency required by the hybrid ML/Web architecture, and
verify that the two primary model backends (PyTorch and XGBoost) execute
correctly before any data or modeling work begins.

The mandate lists three target files:

- `src/verify_env.py` — environment verification script
- `requirements.txt` — locked dependency manifest
- Git repository — scaffold initialized and pushed

---

## 2. Scope

### In scope

- Create `.venv` on a Python version compatible with the pinned package set
- Pin every dependency to an exact version
- Author a verification script that imports every dependency and exercises
  PyTorch and XGBoost runtimes
- Establish `.gitignore` policy for the repository
- Confirm the environment is reproducible from a clean clone

### Out of scope (deferred to later phases)

- Data loading, cleaning, or transformation (Phase 2)
- Model instantiation or hyperparameter tuning (Phase 3)
- Evaluation metrics and XAI (Role 2)
- Frontend and backend integration (Roles 2 and 3)

---

## 3. Environment

| Component | Value |
|---|---|
| Operating System | Windows 10 (AMD64) |
| Shell | PowerShell |
| Python Version | 3.11.9 |
| Virtual Environment Path | `.venv\Scripts\python.exe` |
| Package Manager | pip (upgraded inside the venv) |

Python 3.11.9 was selected because every pinned package in
`requirements.txt` publishes a prebuilt Windows wheel for CPython 3.11.
An initial attempt on Python 3.13 failed — pandas 2.1.1 has no CPython 3.13
wheel, causing pip to fall back to a Meson source build that aborted during
Cython compilation. Recreating the environment on Python 3.11.9 resolved
the issue and required no changes to any pinned version.

---

## 4. Deliverables

### 4.1 `requirements.txt`

Fifteen packages pinned to exact versions, covering the full pipeline:

| Package | Version | Role |
|---|---|---|
| numpy | 1.26.0 | Numerical arrays |
| pandas | 2.1.1 | DataFrame loading and EDA |
| matplotlib | 3.8.0 | Confusion matrices, PR curves |
| seaborn | 0.13.0 | Heatmaps, styled plots |
| scikit-learn | 1.3.1 | Random Forest baseline, CV, metrics |
| xgboost | 2.0.0 | Model 2 — gradient boosting |
| pytorch-tabnet | 4.1.0 | Model 3 — TabNet classifier |
| torch | 2.1.0 | Deep learning backend (CPU wheel) |
| optuna | 3.4.0 | Bayesian hyperparameter search |
| imbalanced-learn | 0.11.0 | Tomek Links in-fold resampling |
| jupyter | 1.0.0 | Notebook execution environment |
| fastapi | 0.103.2 | Reserved for Python bridge surface |
| uvicorn | 0.23.2 | ASGI server |
| pydantic | 2.4.2 | Payload validation |
| joblib | 1.3.2 | Model and encoder persistence |

### 4.2 `src/verify_env.py`

A standalone smoke test that:

1. Imports every module in `requirements.txt` and prints its installed version
2. Executes a tensor matrix multiplication to confirm PyTorch is functional
3. Trains a five-round XGBoost booster on random data to confirm the
   gradient boosting backend is functional
4. Verifies `pytorch_tabnet.TabNetClassifier` exposes its expected public
   API surface (`fit`, `predict`, `predict_proba`)

Exit code 0 on success, 1 on failure. No external state is written — the
script is pure verification.

### 4.3 `.gitignore`

Version control policy for the repository:

| Path | Policy | Rationale |
|---|---|---|
| `.venv/`, `venv/`, `ENV/` | Ignored | Regenerable from `requirements.txt` |
| `__pycache__/`, `*.py[cod]` | Ignored | Bytecode artifacts |
| `models/*.joblib`, `models/*.pt` | Ignored | Regenerable from Notebook 02 with fixed seeds |
| `data/processed/` | Ignored, with exceptions | Regenerable from Notebook 01 |
| `data/processed/feature_names.json` | Tracked | Frozen contract for the Python inference bridge |
| `data/processed/split_indices.json` | Tracked | Frozen train/test split for reproducibility |
| `outputs/**/*.{png,pdf,svg,csv,json,log,txt}` | **Tracked** | Graded deliverables — figures, tables, logs |
| `node_modules/`, `client/.next/` | Ignored | Build caches |
| `.env*` | Ignored | Secrets |

The `outputs/` folder is explicitly tracked because it holds the confusion
matrices, ROC/PR curves, SHAP plots, and metric tables that the project
paper, demo video, and grading rubric depend on. Trained models are
ignored during development and force-added in a single freeze commit
before final submission.

---

## 5. Verification

Command:

python src/verify_env.py

Output summary:
MODULE VERSION STATUS

numpy 1.26.0 OK
pandas 2.1.1 OK
sklearn 1.3.1 OK
imblearn 0.11.0 OK
xgboost 2.0.0 OK
torch 2.1.0 OK
pytorch_tabnet 4.1.0 OK
optuna 3.4.0 OK
matplotlib 3.8.0 OK
seaborn 0.13.0 OK
joblib 1.3.2 OK
fastapi 0.103.2 OK
uvicorn 0.23.2 OK
pydantic 2.4.2 OK
jupyter 1.0.0 OK

Passed: 15 Failed (critical): 0
================================================================

[torch runtime]
torch version : 2.1.0+cpu
CUDA available : False
tensor matmul : OK

[xgboost runtime]
xgboost version : 2.0.0
toy train + predict: OK

[pytorch-tabnet runtime]
tabnet version : 4.1.0
classifier class : TabNetClassifier
public API surface : OK
import : OK

RESULT: Phase 1 environment verification PASSED.


All 15 imports resolve. All three runtime checks pass. Exit code 0.

---

## 6. Issues Encountered and Resolved

### Issue 1 — Initial environment built on Python 3.13

**Symptom:** `pip install -r requirements.txt` failed during the pandas
metadata generation step. The Meson build backend invoked Cython, which
aborted with:

Error compiling Cython file:
...
DEF err = int('Build aborted: the NumPy Cython headers require Cython 3.0.0 or newer.')
ValueError: invalid literal for int() with base 10: ...


**Root cause:** pandas 2.1.1 has no prebuilt CPython 3.13 wheel on
Windows. pip fell back to building from source, which failed because the
build environment shipped with Cython 0.29 while pandas' Cython headers
require Cython 3.0 or newer.

**Resolution:** Deleted the Python 3.13 virtual environment, recreated it
with `py -3.11 -m venv .venv` (Python 3.11.9), and reinstalled. Every
pinned package had a compatible wheel available and installation completed
without source builds.

### Issue 2 — `py` launcher intercepted by Python 3.13 shim

**Symptom:** `py list` and `py install 3.11` returned
Python313\python.exe: can't open file 'C:\Users\kitdu\list': [Errno 2]

**Root cause:** In the affected terminal session, the Microsoft Store
shim for `py` (`WindowsApps\py.exe`) shadowed the real launcher
(`Programs\Python\Launcher\py.exe`) on PATH, causing `py` to resolve to
a bare Python interpreter rather than the version dispatcher.

**Resolution:** Opened a fresh terminal, confirmed with `where py` that
the real launcher was first on PATH, then used `py -3.11` explicitly
rather than relying on the default version.

### Issue 3 — `pytorch-tabnet` version check assumed nonexistent attribute

**Symptom:** The first version of `verify_env.py` attempted
`from pytorch_tabnet import __version__`, which raised
`ImportError: cannot import name '__version__'`.

**Root cause:** `pytorch-tabnet` 4.1.0 does not expose `__version__` as a
module-level attribute.

**Resolution:** Switched the version lookup to
`importlib.metadata.version("pytorch-tabnet")`, which reads the installed
distribution metadata. Additionally, the runtime check was strengthened
to assert that `TabNetClassifier` exposes the three public methods the
pipeline will depend on: `fit`, `predict`, `predict_proba`.

---

## 7. Team Handoff

Phase 1 closes with a verified environment. No handoff to another role
is required at this gate — Phase 2 begins immediately and produces the
processed feature matrices that Amber needs for the Random Forest
baseline.

Downstream consumers of Phase 1 outputs:

| Consumer | Depends On | Notes |
|---|---|---|
| All roles | `.venv` + `requirements.txt` | Reproduce locally with the same interpreter |
| Markie | `pytorch-tabnet`, `joblib` | Bridge will deserialize `.pkl` artifacts |
| Amber | `scikit-learn`, `imbalanced-learn` | RF baseline + Tomek Links |
| Kenneth | `jupyter`, `torch` | Training loop execution |
| Professor / grader | `src/verify_env.py` | Reproducibility checkpoint |

---

## 8. Phase 1 Mandate Checklist

| Item | Status |
|---|---|
| `.venv` initialized | Complete |
| All required packages installed | Complete |
| `requirements.txt` authored and pinned | Complete |
| `src/verify_env.py` authored | Complete |
| PyTorch runtime verified | Complete |
| XGBoost runtime verified | Complete |
| TabNet import verified | Complete |
| `.gitignore` policy established | Complete |
| Branch created per governance policy | Complete |
| Scaffolding pushed to team repository | Complete |

Phase 1 of `tasks/1.md` is closed.

---

## 9. Next Phase

**Phase 2 — Data Exploration & Preprocessing.**

Target files:
- `notebooks/01_EDA_and_Data_Prep.ipynb`
- `src/data_prep.py`
- `src/encoding.py`

Pending inputs to resolve before Phase 2 code begins:

1. Contents of `data/raw/training_attack_types.txt`
2. Decision on train/test split ratio (default recommendation: 80/20 stratified)
3. Encoder contract for the `service` feature — raw string vs pre-encoded integer
4. Format confirmation for `data/raw/kddcup.names.txt` — 43 lines with attack-list header, or 42 lines without

Deliverable from Phase 2: pristine, transformed feature matrices exported to
`data/processed/`, with encoders fitted strictly on training-fold data to
prevent leakage into validation splits.

