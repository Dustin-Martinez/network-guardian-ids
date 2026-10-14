# UI Usage Guide — Network Guardian Dashboard

**Audience:** Team members, professor, graders, and any reviewer.
**Purpose:** Tell the reader how to run the dashboard and use every
screen without asking.
**Related:** `docs/SETUP.md`, `docs/contracts/api_data_contract.md`,
`docs/handoffs/ui_content.md`.

---

## 1. What the Dashboard Is

The Network Guardian Dashboard is a Next.js web application that
demonstrates the intrusion detection pipeline. It has two roles:

1. **Live inference.** The user submits a single network packet and
   receives a prediction from one of the three trained models
   (Random Forest, XGBoost, or TabNet). The prediction comes from the
   Express bridge in real time.

2. **Evaluation review.** The dashboard also displays the frozen test-set
   evaluation results for all three models. These numbers match the
   paper. They are loaded from static JSON assets, not recomputed.

The dashboard does not retrain models and does not touch the frozen
test set. It serves the trained models and displays the evaluation
outputs.

---

## 2. Prerequisites

Before starting the dashboard, confirm the following.

- Python 3.11.9 inside `.venv`
- All packages from `requirements.txt` installed
- All three trained model files present:
  - `models/rf_baseline.joblib`
  - `models/xgb_optuna.joblib`
  - `models/tabnet_best.zip`
- All three meta sidecars present:
  - `models/rf_baseline.meta.json`
  - `models/xgb_optuna.meta.json`
  - `models/tabnet_best.meta.json`
- Node.js 18 or later
- The `client/node_modules/` folder installed (`npm install` run at
  least once)
- The four static data files present in `client/public/data/`

To verify the model files and static data exist:

```powershell
Test-Path models\rf_baseline.joblib
Test-Path models\xgb_optuna.joblib
Test-Path models\tabnet_best.zip
Test-Path client\public\data\class_distribution.json
Test-Path client\public\data\confusion_matrices.json
Test-Path client\public\data\features.json
Test-Path client\public\data\evaluation.json
```

All seven must return `True`.

If the four JSON files in `client/public/data/` are missing or stale,
regenerate them:

```powershell
python scripts\export_ui_data.py
```

---

## 3. Running the Dashboard

The dashboard needs two servers running at the same time.

### Terminal 1 — Express backend

```powershell
cd server
node server.js
```

Expected output:

```
Node.js Server running on port 5000
```

Leave this terminal running.

### Terminal 2 — Next.js frontend

```powershell
cd client
npm run dev
```

Expected output:

```
- ready started server on 0.0.0.0:3000, url: http://localhost:3000
```

Leave this terminal running.

### Browser

Open `http://localhost:3000`.

---

## 4. Logging In

The dashboard uses a demo login. The credentials are stored in
`client/src/lib/data.ts` under `DEMO_USERS`. They are readable in the
browser, so they are not real security.

| Username | Password | Role |
|---|---|---|
| `analyst` | `guardian123` | SOC analyst |
| `admin` | `admin123` | Administrator |

Enter either set of credentials and click Log In.

---

## 5. Navigating the Dashboard

The sidebar has five entries.

| Entry | What it shows |
|---|---|
| Dashboard | Form + panels: class distribution, threat gauge, confusion matrix, feature importances |
| Analyze | Full-width form + threat gauge |
| History | Table of every analysis run in this session |
| Models | Test-set comparison table for all three models |
| Explainability | Feature importances for the currently selected model and the last analysis |
| Settings | Account info and clear-history button |

The selected model persists across views within a session. Switching
the model in the Analyze form updates the confusion matrix and feature
importances panels on the Dashboard and Explainability views.

---

## 6. Running an Analysis

The Analyze form is at the top of the Dashboard and Analyze views.

### Step 1 — Pick a model

Use the Model dropdown. Three options:

- XGBoost (default, highest test Macro F1)
- Random Forest
- TabNet

The dashboard panels update to reflect the selected model.

### Step 2 — Load a preset (optional)

Three preset buttons:

- **Normal SMTP session** — a normal traffic record from the contract
- **DoS flood** — a synthetic DoS record
- **Port probe** — a synthetic probe record

Clicking a preset fills the form with the corresponding values.

### Step 3 — Edit fields (optional)

The form has three collapsible groups:

- **Connection** — protocol, service, flag, duration, bytes
- **Content** — binary flags, failed logins, file operations
- **Traffic statistics** — counts and rate fields

Rate fields must be between 0 and 1. Byte counts and duration must be
non-negative. Binary fields are 0 or 1.

### Step 4 — Click Analyze traffic

The form sends the packet to the Express backend. The backend spawns
`predict_bridge.py`, which loads the selected model, applies the frozen
encoders, and returns a prediction.

The threat gauge updates with the result.

---

## 7. Reading the Threat Gauge

The gauge has four parts.

- **Arc** — a curved indicator scaled to the confidence percentage
- **Prediction** — the class name (Normal, DoS, Probe, R2L, or U2R)
- **Confidence** — the model's probability in percent
- **Model** — the model that produced the prediction

Color coding:

- **Cyan** — the prediction is `normal`, no threat
- **Pink** — the prediction is any attack class

Below the gauge, an alert strip confirms the result: "No threat
detected" or "Threat detected: <class>".

Below that, the last five predictions in this session are listed as
small chips.

---

## 8. Reading the Confusion Matrix

The Confusion Matrix panel shows the test-set confusion matrix for the
currently selected model.

- **Rows** — the true label
- **Columns** — the predicted label
- **Cell values** — counts of test samples
- **Diagonal** — highlighted in cyan (correct predictions)
- **Off-diagonal** — highlighted in pink (errors), with intensity
  proportional to the row share

Switching the model in the Analyze form updates this panel. The title
shows which model is displayed.

Source: `outputs/03_evaluation/test_predictions.csv`, exported to
`client/public/data/confusion_matrices.json`.

---

## 9. Reading the Feature Importances

The Feature Importances panel shows the top eight features for the
currently selected model.

- **XGBoost** — global feature importance from the gradient-boosted
  trees
- **Random Forest** — global feature importance from the bagged trees
- **TabNet** — attention-mask importance from the network's explain
  output

The values are normalized so the largest feature fills the bar.

Switching the model updates this panel.

Source: trained models in `models/`, exported to
`client/public/data/features.json`.

---

## 10. Reading the Class Distribution

The Class Distribution panel shows the train/test split for all five
classes.

- **Cyan bars** — training partition counts
- **Pink bars** — test partition counts
- **Logarithmic scale note** — the class imbalance is large; U2R has
  39 training samples against 65,874 for Normal

Source: `data/processed/split_indices.json`, exported to
`client/public/data/class_distribution.json`.

---

## 11. Reading the Models View

The Models view shows the frozen test-set comparison table.

| Column | Meaning |
|---|---|
| Model | The model name |
| Type | Algorithm family: bagging, boosting, or deep learning |
| Accuracy | Test-set accuracy |
| Macro F1 | Test-set Macro F1 (the primary metric) |
| U2R recall | Recall on the rarest attack class |
| R2L recall | Recall on the second-rarest attack class |

Below the table, a bar chart shows Macro F1 for all three models.

All numbers trace to `outputs/03_evaluation/test_set_evaluation.json`.

---

## 12. Reading the Explainability View

The Explainability view has three panels.

- **Feature importances** — same as the Dashboard panel for the
  currently selected model
- **Last analysis** — the inputs and prediction of the most recent
  Analyze submission
- **What each feature means** — a glossary of the top features

---

## 13. History and Session

Every analysis run in the current browser session is stored in the
History view. History is cleared when the tab is closed. It is not
persisted to disk.

The Clear button on the History view and in Settings empties the
session history.

---

## 14. What the Dashboard Does Not Do

- It does not retrain models.
- It does not create a new train/test split.
- It does not modify the frozen test set.
- It does not store user data.
- It does not persist history beyond the current browser session.
- It does not run in production. It is a demonstration.

---

## 15. Stopping the Servers

In each terminal, press `Ctrl+C` to stop the server.

Do not close a terminal without pressing `Ctrl+C` first. On Windows,
closing without interrupting can leave the port bound for up to 30
seconds.

If a port is stuck, release it:

```powershell
Get-NetTCPConnection -LocalPort 5000
Get-NetTCPConnection -LocalPort 3000
Stop-Process -Id <PID>
```

---

## 16. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| "Service unavailable. Check that the server is running on port 5000." | Express backend is not running | Start Terminal 1 |
| Confusion matrix panel is empty | `confusion_matrices.json` is missing or empty | Run `python scripts\export_ui_data.py` |
| Feature importances panel is empty | `features.json` is missing | Run `python scripts\export_ui_data.py` |
| Models view shows only one row | `evaluation.json` uses short keys | Update `scripts/export_ui_data.py` and re-run |
| CORS error in browser console | Next.js is not on port 3000 | Confirm the dev server port; if different, update `server/server.js` CORS whitelist |
| Login fails | Wrong credentials | Use `analyst` / `guardian123` |
| TabNet prediction errors | The scaling check was not removed | Confirm the TabNet branch in `server/predict_bridge.py` matches the raw-features version |
| Static data does not update | Next.js cached the `public/` folder | Restart `npm run dev` |

---

## 17. Where to Look for Further Detail

| Document | Contents |
|---|---|
| `docs/handoffs/ui_content.md` | Full panel-by-panel data provenance |
| `docs/handoffs/model_comparison.md` | The underlying numbers for the paper |
| `docs/contracts/api_data_contract.md` | Payload schemas and validation rules |
| `docs/SETUP.md` | Environment setup from a clean clone |
| `docs/reports/role-5-phase-3-dwayne-evaluation-suite.md` | Full evaluation narrative |

---

**Signed off by:** Kit Dustin, Project Manager (Role 1)
**Date:** 2026-10-14