# Project Execution Roadmap: Network Guardian IDS

This roadmap outlines the phased, professional workflow for building, optimizing, and evaluating the Network Guardian Intrusion Detection System. It uses a sprint-based approach focused on milestone completion rather than strict calendar weeks.

---

## Phase 1: Environment & Architecture Initialization
*Objective: Lock down reproducible dependencies, folder architecture, and system scaffolding.*
* **Milestone 1.1:** Initialize the Python virtual environment (`.venv`) and containerize package versions via `requirements.txt`.
* **Milestone 1.2:** Establish the modular repository layout (`src/`, `notebooks/`, `docs/`, `contracts/`).
* **Milestone 1.3:** Configure `.gitignore` to secure binary datasets and serialized models.

## Phase 2: Data Exploration & Preprocessing Pipeline
*Objective: Transform raw, highly skewed network packet telemetry into clean, leakage-free matrices.*
* **Milestone 2.1:** Execute exploratory data analysis in `01_EDA_and_Data_Prep.ipynb` to inspect class distributions and missing values.
* **Milestone 2.2:** Programmatically map raw attack labels into the five core classification targets (`normal`, `dos`, `probe`, `r2l`, `u2r`).
* **Milestone 2.3:** Implement data cleaning: drop duplicate records and prune features with >90% linear correlation.
* **Milestone 2.4:** Apply logarithmic transformation ($log(1+x)$) to continuous byte and duration fields.
* **Milestone 2.5:** Execute hybrid encoding (Frequency encoding for `service`; One-Hot encoding for `protocol_type` and `flag`).

## Phase 3: Multi-Model Architecture & Optimization
*Objective: Train diverse machine learning paradigms under unified cross-validation conditions.*
* **Milestone 3.1:** Implement Stratified 5-Fold cross-validation wrapper combined with Tomek Links boundary clearing strictly inside training folds.
* **Milestone 3.2:** Train baseline **Random Forest** (Bagging) to establish non-linear performance metrics.
* **Milestone 3.3:** Train **XGBoost** (Gradient Boosting) integrated with Optuna hyperparameter tuning and validation-based early stopping.
* **Milestone 3.4:** Train **PyTorch TabNet** (Deep Learning with Attention) utilizing continuous feature scaling and synchronized early stopping.

## Phase 4: Evaluation, Explainability & Threshold Calibration
*Objective: Rigorously evaluate error costs, combat class imbalance, and interpret model decisions.*
* **Milestone 4.1:** Compute aggregate Out-of-Fold metrics prioritizing **Macro F1-Score** over bulk accuracy.
* **Milestone 4.2:** Generate and analyze multi-class confusion matrices to quantify false positives and false negatives for high-severity attacks (`u2r`, `r2l`).
* **Milestone 4.3:** Perform decision threshold calibration to optimize sensitivity for rare intrusion vectors.
* **Milestone 4.4:** Integrate **SHAP** values for tree models and extract **Attention Masks** for TabNet to provide forensic feature attribution.

## Phase 5: Artifact Export & Documentation
*Objective: Package models for deployment and finalize academic deliverables.*
* **Milestone 5.1:** Serialize trained transformers, scalers, and model weights into the `models/` directory using `joblib` and `torch`.
* **Milestone 5.2:** Finalize Jupyter notebooks with comprehensive Markdown text cell justifications for every technical decision.
* **Milestone 5.3:** Complete the Executive Summary, Discovery Log, and Individual Reflections for the project documentation.