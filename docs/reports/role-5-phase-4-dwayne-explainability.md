# Role 5 — Phase 4 Explainability Outputs

## 1. Objective

Generate explainability visualizations for the saved Random Forest, XGBoost, and TabNet models to support the Network Guardian intrusion detection research project.

## 2. Environment and Data

- Python environment: Python 3.11.9 virtual environment
- Test dataset: `data/processed/X_test.npy`
- Test samples: 36,396
- Input features: 43
- Classification classes: normal, dos, probe, r2l, and u2r
- Random Forest checkpoint: `models/rf_baseline.joblib`
- XGBoost checkpoint: `models/xgb_optuna.joblib`
- TabNet checkpoint: `models/tabnet_best.zip`

The existing checkpoints and frozen test set were used. No model retraining was performed.

## 3. Explainability Methods

### 3.1 Global SHAP Summaries

`shap.TreeExplainer` was used to calculate SHAP values for the saved Random Forest and XGBoost models. A reproducible sample of 1,000 test records was used for each global summary plot, with random seed 42.

The summary plots visualize feature contributions to the models' predicted classes. These results provide a global overview of features influencing predictions; they do not establish causation.

**Figure 1.** Random Forest global SHAP summary. Source: `outputs/03_evaluation/shap_summary_rf.png`; model: `models/rf_baseline.joblib`.

**Figure 2.** XGBoost global SHAP summary. Source: `outputs/03_evaluation/shap_summary_xgb.png`; model: `models/xgb_optuna.joblib`.

### 3.2 Local SHAP Explanation

A correctly predicted U2R test example was selected using the existing Phase 3 prediction and confidence outputs. The selected test row was index 29,522. The XGBoost SHAP waterfall plot illustrates how feature contributions combine relative to the explainer's baseline for the selected class.

**Figure 3.** Local SHAP waterfall for the selected U2R example. Source: `outputs/03_evaluation/shap_local_example.png`; model: `models/xgb_optuna.joblib`; test row index: 29,522.

### 3.3 TabNet Attention Visualization

The saved TabNet checkpoint was loaded from `models/tabnet_best.zip`. Attention masks were extracted using the model's explanation interface. Mean attention values were aggregated across decision steps and a reproducible sample of 1,000 test records.

The resulting plot presents the 20 features with the highest aggregated attention values. Attention indicates how the model allocates feature selection across its decision process and should not be interpreted as equivalent to SHAP values.

**Figure 4.** TabNet feature attention aggregated across decision steps. Source: `outputs/03_evaluation/tabnet_attention_mask.png`; model: `models/tabnet_best.zip`.

## 4. Generated Deliverables

The following files were generated under `outputs/03_evaluation/`:

- `shap_summary_rf.png`
- `shap_summary_xgb.png`
- `shap_local_example.png`
- `tabnet_attention_mask.png`

The script completed successfully and confirmed that all four output files exist.

## 5. Limitations

The global SHAP figures use a 1,000-record subset rather than the complete test set. The TabNet attention visualization also uses a 1,000-record subset. These choices reduce computational cost and make the process reproducible.

The local explanation represents one selected U2R test example and should not be generalized to all U2R traffic. SHAP feature contributions and TabNet attention masks describe different aspects of the models and should not be treated as directly interchangeable measurements.

## 6. Conclusion

Phase 4 explainability figure generation completed successfully using the existing model checkpoints and frozen test data. The four required visualizations are available for inspection and potential inclusion in the research paper, subject to reviewing plot readability and aligning captions with `docs/reports/paper_structure.md`.
