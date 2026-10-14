# Handoff — UI Wiring to Real Evaluation Data

**From:** Kit Dustin (Role 1) — Project Manager
**To:** Markie (Role 2) — Paper Lead; Dwayne (Role 5) — Evaluation Engineer;
Kenneth (Role 4) — Video Producer
**Date:** 2026-10-14
**Status:** Complete — merged to main
**Related:** `docs/handoffs/ui_usage_guide.md`,
`docs/handoffs/ui_content.md`, `docs/handoffs/model_comparison.md`.

---

## 1. Purpose

This document records the completion of the dashboard wiring to real
evaluation data. Before this work, the dashboard panels other than the
threat gauge displayed fabricated placeholder values from Phase 1. After
this work, every panel displays numbers that trace to a file produced by
the training or evaluation pipeline.

The paper, the video, and any external reviewer can now rely on the
dashboard as an evidence surface. The numbers shown in the UI match the
numbers in the paper.

---

## 2. What Changed

### New files

| File | Purpose |
|---|---|
| `scripts/export_ui_data.py` | Generates four JSON assets from trained models and evaluation outputs |
| `client/public/data/class_distribution.json` | Train/test class counts |
| `client/public/data/confusion_matrices.json` | Test-set confusion matrices for all three models |
| `client/public/data/features.json` | Top-8 feature importances for all three models |
| `client/public/data/evaluation.json` | Full test-set evaluation payload |
| `docs/handoffs/ui_usage_guide.md` | How to run and use the dashboard |
| `docs/handoffs/ui_content.md` | Panel-by-panel data provenance |

### Modified files

| File | Change |
|---|---|
| `client/src/lib/data.ts` | Removed all mock constants; added typed loaders for the four JSON assets |
| `client/src/components/Charts.tsx` | TrafficChart replaced with class distribution; ConfusionMatrix and FeatureImportances read real data and accept a model prop |
| `client/src/components/Views.tsx` | ModelsView reads real test-set metrics |
| `client/src/components/AnalyzeForm.tsx` | Added `onModelChange` callback so parent can track the selected model |
| `client/src/app/page.tsx` | Model state lifted from AnalyzeForm to Dashboard; passed to panels as a prop |

### Removed

- `TRAFFIC_NORMAL`, `TRAFFIC_DOS`, `MATRIX`, `FEATURES`, `MODELS` constants from `client/src/lib/data.ts`. All were fabricated.

---

## 3. What Each Panel Now Displays

| Panel | Live or Static | Data Source |
|---|---|---|
| Class distribution | Static | `split_indices.json` via `class_distribution.json` |
| Confusion matrix | Static | `test_predictions.csv` via `confusion_matrices.json` |
| Feature importances | Static | Trained models via `features.json` |
| Models view | Static | `test_set_evaluation.json` via `evaluation.json` |
| Threat gauge | **Live** | Express bridge at `POST /api/analyze` |
| Analyze form | N/A | Contract-defined fields |

Only the threat gauge and the analyze form are live. Everything else is
a static representation of the frozen evaluation.

---

## 4. Data Flow

```
Notebook 03
    ↓ produces
outputs/03_evaluation/test_predictions.csv
outputs/03_evaluation/test_set_evaluation.json
    ↓ read by
scripts/export_ui_data.py
    ↓ writes
client/public/data/*.json
    ↓ served by
Next.js static assets
    ↓ read by
Dashboard panels
```

The full chain is idempotent. Running `scripts/export_ui_data.py` again
produces the same JSON files from the same sources.

---

## 5. Key Findings Surfaced by the UI

Three findings that the dashboard makes visible for the first time.

### Finding 1 — XGBoost leads on Macro F1

The Models view shows XGBoost at 94.51% test Macro F1, above Random
Forest at 93.31% and TabNet at 93.06%. The spread is 1.45 percentage
points. XGBoost is the recommended model for deployment.

### Finding 2 — U2R recall is identical across all three models

All three models classify 10 of the 13 U2R test samples correctly. The
recall is 76.92% for every model. Adding model complexity does not
improve U2R detection on this test set. This is a data-limit finding.

### Finding 3 — XGBoost and Random Forest learn different top features

The Feature Importances panel shows:

- Random Forest: top feature is `service_freq`
- XGBoost: top feature is `flag_S0`
- TabNet: top feature is `service_freq`

TabNet agrees with Random Forest. XGBoost diverges. The divergence is
real and worth discussing in the paper's Discussion section. XGBoost
leans on the one-hot encoded `flag` column, while the other two models
lean on the frequency encoding of `service`.

---

## 6. Handoff Actions

### To Markie (Role 2)

The Models view table in the dashboard matches the paper's Table 2. The
following numbers are the source for the paper's Results section and can
be cited directly:

- XGBoost test Macro F1: 0.9451
- Random Forest test Macro F1: 0.9331
- TabNet test Macro F1: 0.9306
- U2R recall for all three: 0.7692
- R2L recall: XGBoost 0.9920, Random Forest 0.9520, TabNet 0.9760

Figure sources for the paper:

- Test-set confusion matrices: `client/public/data/confusion_matrices.json`
  (raw counts) and `outputs/03_evaluation/confusion_matrix_*.png`
  (rendered plots)
- Feature importances: `client/public/data/features.json`
- Class distribution: `client/public/data/class_distribution.json`

The paper's Discussion section should include Finding 3 — the divergence
between XGBoost's top feature and the other two models' top feature.

### To Dwayne (Role 5)

The feature importance extraction uses TabNet's `explain()` method on a
512-row sample of the test set. The masks are averaged over the rows to
produce one importance value per feature. The extraction is documented
in `scripts/export_ui_data.py` under `export_feature_importances`.

No further TabNet extraction work is needed for the UI. The SHAP work
for the paper is separate and continues as planned.

### To Kenneth (Role 4)

The dashboard is now stable and paper-consistent. It is ready for the
video demo. When recording the screen, the following panels are safe to
show:

- Class distribution — shows the real dataset imbalance
- Confusion matrix — shows the real test-set results
- Feature importances — shows the real model feature usage
- Models view — shows the real comparison table
- Threat gauge — shows the live prediction when a packet is submitted

The video should use the **XGBoost** model selector when showing the
threat gauge, since XGBoost is the recommended model.

---

## 7. What Remains

### For the paper

- Markie integrates the comparison numbers into the Results section.
- Markie integrates Dwayne's SHAP plots into the Explainability section.
- Markie drafts the Discussion section including the feature-importance
  divergence.

### For the video

- Kenneth records the dashboard segments.
- Kit reviews the recording before final edit.

### For submission

- Kit writes `SUBMISSION.md` at repo root on Day 9.
- Kit updates `README.md` at repo root on Day 9.
- Kit runs the final review pass on Day 9.

---

## 8. How to Verify the Handoff

Any team member can verify the dashboard is wired to real data.

1. Open `http://localhost:3000` after starting both servers.
2. Navigate to **Models** in the sidebar.
3. Confirm the table shows three rows with the values in section 6.
4. Return to **Dashboard**.
5. Change the model selector between XGBoost, Random Forest, and TabNet.
6. Confirm the confusion matrix title and cell values change per model.
7. Confirm the feature importances panel changes per model.
8. Click **Normal SMTP session**, then **Analyze traffic**.
9. Confirm the threat gauge updates with a prediction.

If all nine steps pass, the wiring is correct.

---

## 9. Traceability

Every dashboard number traces to a file. The table below lists the
sources.

| Dashboard element | Source file |
|---|---|
| Class distribution counts | `data/processed/split_indices.json` |
| Confusion matrix cells | `outputs/03_evaluation/test_predictions.csv` |
| Feature importance values | `models/rf_baseline.joblib`, `models/xgb_optuna.joblib`, `models/tabnet_best.zip` |
| Models view table | `outputs/03_evaluation/test_set_evaluation.json` |
| Threat gauge | Live bridge at `server/predict_bridge.py` |

The four static JSON files in `client/public/data/` are derived copies.
They are regenerated from the sources above by
`scripts/export_ui_data.py`.

---

## 10. Commit References

The dashboard wiring was completed in a single commit on branch
`feature/role-1-ui-real-data`.

Commit message:

```
feat(ui): wire dashboard panels to real evaluation data

- scripts/export_ui_data.py generates four JSON assets from trained
  models and evaluation outputs
- class_distribution.json from split_indices.json
- confusion_matrices.json from test_predictions.csv; keys use long names
- features.json from RF and XGBoost feature_importances_ plus TabNet
  explain() output
- evaluation.json with model keys remapped to long names
- Charts.tsx: TrafficChart replaced with class distribution;
  ConfusionMatrix and FeatureImportances accept a model prop
- Views.tsx: ModelsView reads real test-set metrics
- AnalyzeForm.tsx: onModelChange callback lifts model selection to
  parent
- page.tsx: model state lifted to Dashboard, passed to panels
- Removes all mock constants from lib/data.ts
```

---

**Signed off by:** Kit Dustin, Project Manager (Role 1)
**Date:** 2026-10-14