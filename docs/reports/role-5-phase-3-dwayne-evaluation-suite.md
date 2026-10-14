# Role 5 — Phase 3: Evaluation Suite Report

**Project:** Network Guardian: Detecting Network Intrusions with Machine Learning  
**Role:** Role 5 — Evaluation Engineer and Explainability Contributor  
**Prepared by:** Dwyane  
**Date:** October 14, 2026  
**Status:** Evaluation executed; required outputs verified; reporting follow-ups remain.

---

## 1. Executive Summary

Phase 3 evaluated the saved Random Forest, XGBoost, and TabNet models against the project's frozen held-out test set. The evaluation used 36,396 samples and 43 features, with the class order `normal`, `dos`, `probe`, `r2l`, and `u2r`.

XGBoost achieved the highest test Macro F1 score at **0.945134**, followed by Random Forest at 0.933095 and TabNet at 0.930622. XGBoost also had the highest weighted F1 score, at 0.998961.

Performance on the minority attack classes remains important. All three models missed three U2R samples. XGBoost missed two R2L samples, compared with six for TabNet and twelve for Random Forest. These results indicate that aggregate performance alone does not adequately describe the models' behavior on rare attacks.

The evaluation script completed successfully, and all nine required Phase 3 files were verified. The class-distribution figure was also generated separately from the class counts recorded in `data/processed/split_indices.json`.

The training-versus-cross-validation gap for every model and the precise intended schema of `per_class_metrics_normalized.csv` still require final validation.

## 2. Evaluation Environment and Method

The evaluation was conducted in the project's Python virtual environment, `.venv`, using the existing saved model artifacts.

The evaluated artifacts were:

- `models/rf_baseline.joblib`
- `models/xgb_optuna.joblib`
- `models/tabnet_best.zip`

The evaluation used:

- `data/processed/X_test.npy`
- `data/processed/y_test.npy`
- `data/processed/class_order.json`
- `data/processed/feature_names.json`

The frozen test set contains 36,396 samples and 43 features. The canonical class order is Normal, DoS, Probe, R2L, and U2R.

No new train/test split was created, and the evaluation workflow did not retrain or tune the saved models. Test results are reported as held-out evaluation results and must not be used to select new hyperparameters.

Macro F1 is treated as the primary comparison metric because it gives equal weight to each class. Weighted F1 is included as a supplementary measure; it can be dominated by the more frequent classes in an imbalanced dataset.

## 3. Comparative Test Results

| Metric | Random Forest | XGBoost | TabNet |
|---|---:|---:|---:|
| Test Macro F1 | 0.933095 | **0.945134** | 0.930622 |
| Test weighted F1 | 0.998905 | **0.998961** | 0.997602 |
| U2R recall | 0.769231 | 0.769231 | 0.769231 |
| U2R false negatives | 3 | 3 | 3 |
| R2L recall | 0.952000 | **0.992000** | 0.976000 |
| R2L false negatives | 12 | **2** | 6 |
| Prediction time (seconds) | 0.151 | **0.126** | 1.091 |

XGBoost achieved the highest Macro F1 score among the three evaluated models. Its R2L recall was 0.992000, corresponding to two missed R2L samples. Random Forest had the lowest R2L recall of the three models, at 0.952000, and missed twelve R2L samples. TabNet achieved an R2L recall of 0.976000 and missed six.

All three models achieved a U2R recall of 0.769231 and missed three U2R samples. Since U2R is represented by only 13 test samples, each missed sample has a substantial effect on its recall. This small support also means that the observed recall should be interpreted cautiously.

The high weighted F1 scores should not be interpreted as evidence of equally strong performance on every class. Macro F1 and the per-class metrics provide a more balanced view of performance under the observed class imbalance.

Prediction times were measured during this evaluation run. They are environment-specific observations, not a comprehensive benchmark of deployment latency.

## 4. Error Analysis and Operational Implications

The evaluation identified missed detections in both rare attack classes.

### U2R

Each model missed three of the 13 U2R test samples. The resulting recall was 0.769231 for all three models. In an intrusion-detection setting, these false negatives represent U2R examples that were not correctly detected as U2R.

Because the test support is small, additional independent data would be useful to assess whether this result generalizes to unseen U2R traffic.

### R2L

XGBoost produced the fewest R2L false negatives, with two. TabNet missed six, and Random Forest missed twelve. Based on these test results, XGBoost showed the strongest R2L detection performance among the evaluated models.

False positives also matter operationally because they can create unnecessary alerts and increase analyst workload. The per-class metrics and confusion matrices should be reviewed together to assess both missed detections and incorrect positive predictions. No specific operational cost or alert threshold was measured in this evaluation.

The results support further investigation of XGBoost as a candidate model, but they do not by themselves establish the final deployment choice. That decision should also consider false-positive behavior, model explainability, and the project's validation requirements.

## 5. Generated Outputs

The following required files were verified in `outputs/03_evaluation/`:

- `confusion_matrix_rf.png`
- `confusion_matrix_xgb.png`
- `confusion_matrix_tabnet.png`
- `per_class_metrics.csv`
- `per_class_metrics_normalized.csv`
- `pr_curve_u2r.png`
- `pr_curve_r2l.png`
- `model_comparison_visual.png`
- `test_set_evaluation.json`

The additional class-distribution figure was generated at:

- `outputs/03_evaluation/class_distribution.png`

Its source was `data/processed/split_indices.json`, which contains the train and test class counts. The figure uses a logarithmic vertical axis to make the large differences in class frequency visible.

The evaluation outputs provide the basis for the paper's comparative-results and error-analysis sections. Figures should be opened and inspected before final inclusion in the paper.

## 6. Training-versus-Cross-Validation Gap

The evaluation script did not calculate a training-versus-cross-validation Macro F1 gap for models whose metadata lacked a `train_macro_f1` field. The held-out test score is not a substitute for the training score and must not be used to calculate that gap.

A separate TabNet verification report records a training Macro F1 of 0.962640 and a cross-validation mean of 0.921225, producing a difference of 0.041415. This is an in-sample versus cross-validation comparison and should be cited as coming from that separate report, not represented as a new result calculated by the Phase 3 test evaluation.

The training-versus-cross-validation comparison for Random Forest and XGBoost remains to be confirmed from their recorded training metrics or a controlled training-set prediction analysis. The discrepancy between the expected and recorded per-class recall metadata fields should also be documented rather than silently corrected.

The current evidence is insufficient to conclude that all three models have the same degree of overfitting. Any interpretation should distinguish in-sample performance, cross-validation performance, and held-out test performance.

## 7. Metric Schema and Limitations

The project requires both `per_class_metrics.csv` and `per_class_metrics_normalized.csv`, but the available Phase 3 instructions do not clearly define how the normalized file must differ from the standard file.

The current evaluation implementation keeps precision, recall, and F1 on their natural 0–1 scale and adds `support_fraction`, calculated as each class's support divided by total test support. This is an explicit provisional interpretation, not a confirmed project-wide definition. The schema should be confirmed with the project lead before the normalized CSV is treated as final.

Additional limitations include the small number of U2R and R2L test samples, the absence of an independent external test dataset in this evaluation, and the fact that prediction timings are specific to the current machine and runtime.

## 8. Conclusion and Handoff

Phase 3 successfully evaluated the three saved models and generated the required evaluation artifacts. XGBoost achieved the highest test Macro F1 and the fewest R2L false negatives. However, all three models missed three U2R samples, and the small U2R test support warrants caution when interpreting its recall.

Before the phase is marked fully complete, the normalized-metrics schema and the remaining training-versus-cross-validation comparisons must be confirmed. The generated figures and metrics can then be handed to Markie for paper integration.

Phase 4 will address explainability through SHAP summaries for Random Forest and XGBoost, local SHAP explanations for selected rare-attack predictions, and a TabNet attention-mask visualization. These analyses must use the approved saved models and preserve the frozen test set's role as an evaluation dataset.

**Primary result source:** `outputs/03_evaluation/test_set_evaluation.json`  
**Per-class metrics:** `outputs/03_evaluation/per_class_metrics.csv`  
**Normalized metrics (schema pending confirmation):** `outputs/03_evaluation/per_class_metrics_normalized.csv`