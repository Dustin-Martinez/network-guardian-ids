# AI Prompt: Evaluation, Metrics & Explainability Phase

*Use this vendor-agnostic prompt when scripting the evaluation metrics, confusion matrix visualizations, threshold tuning, and SHAP explainability engine (`src/evaluate.py` or Notebook 03).*

---

### Prompt Text:
> "Act as a digital forensics and machine learning lead. I need to evaluate our trained IDS models (Random Forest, XGBoost, TabNet) and explain their predictions for a security operations team.
> 
> Please provide Python code using `scikit-learn`, `matplotlib`, `seaborn`, and `shap` that implements:
> 1. **Comprehensive Metrics:** A function that computes Macro F1-Score, weighted Precision, Recall, and generates multi-class confusion matrix plots.
> 2. **Threshold Calibration:** Code that evaluates Precision-Recall curves to manually adjust classification decision thresholds for high-risk, low-frequency attack classes (`u2r`, `r2l`).
> 3. **Explainable AI (XAI):** Implementation of `shap.TreeExplainer` to generate local and global feature importance summary plots for the XGBoost and Random Forest models, alongside guidance on extracting TabNet attention masks.
> 
> Format the output clearly with clean, production-grade functions."