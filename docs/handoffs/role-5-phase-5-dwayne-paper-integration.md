# Handoff — Phase 5 Results and Explainability for Paper Integration

**From:** Dwayne (Role 5) — Evaluation Engineer, Explainability Contributor & TabNet Executor

**To:** Markie (Role 2) — Paper Lead

**Date:** 2026-10-14

**Status:** Draft prepared — pending final figure and metric verification

**Source files:** `outputs/03_evaluation/test_set_evaluation.json`, `outputs/03_evaluation/per_class_metrics.csv`, `outputs/03_evaluation/per_class_metrics_normalized.csv`, `outputs/03_evaluation/shap_summary_rf.png`, `outputs/03_evaluation/shap_summary_xgb.png`, `outputs/03_evaluation/shap_local_example.png`, `outputs/03_evaluation/tabnet_attention_mask.png`

---

## 1. Purpose

This handoff provides the Results and Explainability draft material prepared by Role 5 for integration into the Network Guardian IDS research paper.

The material builds on the completed Phase 3 evaluation and Phase 4 explainability outputs. It provides the main findings, suggested interpretation, figure references, and reporting limitations for the paper lead.

The intended recipient is Markie (Role 2), who will review and integrate the material into the main manuscript.

**This handoff is not a substitute for the source artifacts.** Numerical claims must be traceable to the committed evaluation files, and feature-level explainability claims must be verified against the actual figures before publication.

## 2. Paper Sections Covered

This handoff supports the following paper sections:

| Paper section | Content |
|---|---|
| Results and Evaluation | Comparison of Random Forest, XGBoost, and TabNet |
| Error Analysis | Per-class performance and rare-attack limitations |
| Explainability Analysis | Global SHAP, local SHAP, and TabNet attention |
| Discussion | Interpretation, limitations, and implications |

The Results section should prioritize Macro F1 and class-level detection behavior rather than using accuracy as the primary basis for model selection.

---

## 3. Table 1 — Test-Set Model Comparison

**Source:** `outputs/03_evaluation/test_set_evaluation.json`

**Test set:** 36,396 samples and 43 features, with five classes.

| Model | Test Macro F1 | Test accuracy |
|---|---:|---:|
| Random Forest | 0.9331 | 0.9989 |
| XGBoost | 0.9451 | 0.9990 |
| TabNet | 0.9306 | 0.9976 |

### 3.1 Interpretation

- **XGBoost achieved the highest test Macro F1**, at 0.9451.
- Random Forest scored 0.9331, while TabNet scored 0.9306.
- The difference between Random Forest and TabNet was approximately 0.0025 in Macro F1.
- Macro F1 is the more informative headline metric because the test set is imbalanced and contains substantially fewer examples of R2L and U2R than normal and DoS traffic.

The test results support identifying XGBoost as the leading model by aggregate Macro F1. The per-class results must also be considered before making claims about which model is most suitable for detecting a specific attack class.

**Suggested paper table caption:** Test-set performance comparison of Random Forest, XGBoost, and TabNet on the frozen held-out dataset.

## 4. Rare-Class Detection

**Sources:**
- `outputs/03_evaluation/per_class_metrics.csv`
- `outputs/03_evaluation/per_class_metrics_normalized.csv`
- `outputs/03_evaluation/pr_curve_u2r.png`
- `outputs/03_evaluation/pr_curve_r2l.png`

The test set contains the following class counts:

| Class | Test samples |
|---|---:|
| Normal | 21,958 |
| DoS | 13,643 |
| Probe | 532 |
| R2L | 250 |
| U2R | 13 |

The class distribution makes rare-class evaluation especially important.

### 4.1 U2R

All three models recorded U2R recall of 0.7692, equivalent to 10 correctly detected instances out of 13.

This is an important limitation to discuss. The result does not establish that the models missed the same individual records; that would require a comparison of their row-level predictions.

The small U2R support also means that each individual test example has a substantial effect on the measured recall. The paper should avoid treating this estimate as a precise prediction of performance on future U2R traffic.

### 4.2 R2L

| Model | R2L recall |
|---|---:|
| Random Forest | 0.9520 |
| XGBoost | 0.9920 |
| TabNet | 0.9760 |

XGBoost recorded the highest R2L recall among the three models. This provides a useful complement to the Macro F1 comparison and highlights a difference in class-level performance that overall accuracy alone would not communicate clearly.

**Suggested discussion:** Compare the R2L recall values with the confusion matrices and precision–recall curves. Avoid drawing conclusions about false-positive burden from recall alone; precision and the relevant confusion-matrix entries should also be reviewed.

---

## 5. Explainability Outputs

Phase 4 generated four required figures from the existing saved models and frozen test data. The explainability script completed successfully without retraining the models.

### 5.1 Global SHAP — Random Forest

**Source:** `outputs/03_evaluation/shap_summary_rf.png`

The global SHAP summary visualizes feature contributions across a reproducible sample of 1,000 test records.

Use this figure to discuss the features with the largest displayed absolute SHAP contributions and the variation in their contributions across records. The actual leading feature names and contribution directions must be confirmed by inspecting the figure.

### 5.2 Global SHAP — XGBoost

**Source:** `outputs/03_evaluation/shap_summary_xgb.png`

The XGBoost global SHAP summary provides a corresponding view of feature contributions for the second tree-based model.

Compare the feature-attribution patterns between Random Forest and XGBoost. Discuss shared or differing rankings only after inspecting the actual plots.

The figures summarize model behavior within the selected explanation sample; they do not demonstrate that any feature causes an attack.

### 5.3 Local SHAP — U2R Example

**Source:** `outputs/03_evaluation/shap_local_example.png`

The local waterfall plot was generated for test-set row index 29,522, selected as a correctly predicted U2R example using the existing Phase 3 prediction and confidence outputs.

Use the waterfall to explain how individual feature contributions move the explained model output relative to its baseline. The displayed feature names, contribution directions, and magnitudes must be checked directly against the figure before describing specific features in the paper.

This is one illustrative example, not evidence that the model consistently detects all U2R traffic.

### 5.4 TabNet Attention

**Source:** `outputs/03_evaluation/tabnet_attention_mask.png`

The TabNet attention visualization aggregates attention-mask values across six decision steps and a reproducible sample of 1,000 test records. It displays the 20 features with the highest aggregated attention values.

Use this figure to describe the features receiving comparatively high average attention under the implemented aggregation method.

**Important distinction:** SHAP values estimate feature contributions to model outputs. TabNet attention masks describe the model's internal feature-selection behavior. They are complementary explanations and must not be treated as equivalent importance measurements.

---

## 6. Figure Inventory

The following Phase 3 and Phase 4 figures are available for integration.

| Figure | Source file | Suggested caption |
|---|---|---|
| 1 | `outputs/03_evaluation/confusion_matrix_rf.png` | Random Forest confusion matrix on the frozen test set |
| 2 | `outputs/03_evaluation/confusion_matrix_xgb.png` | XGBoost confusion matrix on the frozen test set |
| 3 | `outputs/03_evaluation/confusion_matrix_tabnet.png` | TabNet confusion matrix on the frozen test set |
| 4 | `outputs/03_evaluation/pr_curve_u2r.png` | Precision–recall curves for U2R detection across the evaluated models |
| 5 | `outputs/03_evaluation/pr_curve_r2l.png` | Precision–recall curves for R2L detection across the evaluated models |
| 6 | `outputs/03_evaluation/model_comparison_visual.png` | Test-set Macro F1 comparison across the three models |
| 7 | `outputs/03_evaluation/shap_summary_rf.png` | Global SHAP summary for Random Forest |
| 8 | `outputs/03_evaluation/shap_summary_xgb.png` | Global SHAP summary for XGBoost |
| 9 | `outputs/03_evaluation/shap_local_example.png` | Local SHAP waterfall for the selected U2R example |
| 10 | `outputs/03_evaluation/tabnet_attention_mask.png` | TabNet attention aggregated across decision steps |

These are suggested figure numbers for this handoff only. Renumber them to match the final manuscript and the inventory in `docs/reports/paper_structure.md`.

---

## 7. Reporting Rules and Limitations

Before final integration, observe the following:

1. **Use Macro F1 as the primary aggregate comparison metric.** Accuracy is above 99% for all three models and does not adequately distinguish their class-level behavior.
2. **Do not claim XGBoost has superior U2R recall.** All three models recorded 0.7692 on the test set.
3. **Do not claim the models missed the same U2R records** based solely on their equal recall values. Verify row-level predictions before making that claim.
4. **Do not invent feature rankings or SHAP contribution directions.** Inspect the saved plots first.
5. **Do not interpret attention as a direct measure of feature contribution.** TabNet attention and SHAP measure different aspects of model behavior.
6. **State the sample sizes used for the explanation figures.** The global SHAP and TabNet attention plots use 1,000 test records each.
7. **Avoid unsupported deployment claims.** Performance on the held-out dataset does not establish performance on live network traffic.
8. **Verify exact per-class metrics against the committed CSV and evaluation JSON** before final publication.

---

## 8. Traceability Index

| Claim or artifact | Source |
|---|---|
| Test-set size and feature count | `outputs/03_evaluation/test_set_evaluation.json` |
| Test Macro F1 and accuracy | `outputs/03_evaluation/test_set_evaluation.json` |
| Per-class precision, recall, F1, and support | `outputs/03_evaluation/per_class_metrics.csv` |
| Normalized per-class metrics | `outputs/03_evaluation/per_class_metrics_normalized.csv` |
| Confusion matrices | `outputs/03_evaluation/confusion_matrix_*.png` |
| U2R precision–recall curve | `outputs/03_evaluation/pr_curve_u2r.png` |
| R2L precision–recall curve | `outputs/03_evaluation/pr_curve_r2l.png` |
| Macro F1 comparison | `outputs/03_evaluation/model_comparison_visual.png` |
| Random Forest global SHAP | `outputs/03_evaluation/shap_summary_rf.png` |
| XGBoost global SHAP | `outputs/03_evaluation/shap_summary_xgb.png` |
| Local U2R SHAP explanation | `outputs/03_evaluation/shap_local_example.png` |
| TabNet attention visualization | `outputs/03_evaluation/tabnet_attention_mask.png` |
| Explainability implementation | `src/explainability.py` |
| Paper structure and figure inventory | `docs/reports/paper_structure.md` |
| Research narrative guidance | `docs/reports/paper_narrative_context.md` |

Any additional numerical or feature-level claim should be verified against the relevant source before inclusion in the manuscript.

---

## 9. Handoff to Markie

The Phase 5 draft material provides a starting point for the paper's Results, Error Analysis, and Explainability sections.

The paper lead should:

- Integrate the comparative findings into the manuscript's existing structure.
- Review the actual SHAP and TabNet figures and add verified feature-level observations.
- Confirm per-class metrics and figure captions against the source artifacts.
- Remove duplicated explanations and align terminology with the Methodology section.
- Ensure the final claims reflect the limits of the held-out test set and the rare-class sample counts.

**Final status:** Draft material prepared. Final feature-level interpretation and source verification remain necessary before publication.

**Prepared by:** Dwayne — Role 5

**Date:** 2026-10-14