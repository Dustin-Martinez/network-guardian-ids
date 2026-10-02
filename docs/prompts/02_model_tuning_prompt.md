# AI Prompt: Model Training & Optuna Optimization Phase

*Use this vendor-agnostic prompt when generating the training loops, Optuna objective functions, and early stopping configurations for XGBoost and TabNet (`src/models.py` or Notebook 02).*

---

### Prompt Text:
> "Act as an expert MLOps engineer. I am training three distinct classification models—**Random Forest**, **XGBoost**, and **PyTorch TabNet**—on tabular network intrusion data with severe class imbalance.
> 
> Please provide Python code utilizing `optuna`, `xgboost`, `pytorch-tabnet`, and `scikit-learn` that satisfies the following requirements:
> 1. **Stratified Cross-Validation:** Set up a Stratified 5-Fold training loop where Tomek Links resampling is applied *exclusively* inside the training fold to prevent validation leakage.
> 2. **Optuna Hyperparameter Optimization:** Write an objective function targeting **Macro F1-Score** to dynamically tune hyperparameters for XGBoost (e.g., learning rate, max depth, subsample) and TabNet.
> 3. **Early Stopping:** Configure validation monitoring for XGBoost and TabNet with a patience window to automatically halt training and prevent overfitting.
> 
> Include code snippets showing how to serialize the trained models using `joblib` and PyTorch state dictionaries."