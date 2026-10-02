# Rubric Compliance & Verification Matrix

This matrix maps project implementation artifacts directly against the CCINSYSL course evaluation rubrics[cite: 1, 2].

| Rubric Component | Targeted Criteria for "Exceptional" (4 Points) | Implementation Location | Compliance Strategy |
| :--- | :--- | :--- | :--- |
| **Data Understanding & Preparation**[cite: 1, 2] | Thorough data exploration, identification of data flaws, and explicit justification for every preparation decision[cite: 1]. | `notebooks/01_EDA_and_Data_Prep.ipynb`<br>`docs/project_overview.md` | Documents duplicate removal, log transformations, hybrid encoding, correlation pruning, and target mapping[cite: 1, 2, 3, 4]. |
| **Model Building & Comparison**[cite: 1, 2] | Builds several well-chosen models from different algorithmic approaches, comparing them under identical conditions[cite: 1]. | `notebooks/02_Model_Training.ipynb`<br>`src/models.py` | Trains Random Forest (Bagging), XGBoost (Boosting), and PyTorch TabNet (Deep Learning) using a shared K-Fold split[cite: 1]. |
| **Evaluation & Interpretation**[cite: 1, 2] | Uses problem-appropriate metrics, evaluates real error costs, and checks for overfitting[cite: 1, 2]. | `notebooks/03_Evaluation_and_XAI.ipynb`<br>`src/evaluate.py` | Evaluates Macro F1-Score, analyzes false positives/negatives in confusion matrices, and uses SHAP for explainability[cite: 1, 2]. |
| **Discovery Process & Documentation**[cite: 1, 2] | Clean, reproducible notebook execution; complete Discovery Log and Executive Summary[cite: 1, 2]. | `notebooks/`<br>Final PDF Documentation | Enforces seed locking, exports model artifacts, and records development lessons[cite: 1, 2]. |