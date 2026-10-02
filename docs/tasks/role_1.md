# Operational Mandate: Role 1 - Kit Dustin
**Title:** Project Manager, Data Preparation Engineer & Core Model Developer

## Phase 1: Environment & Project Scaffolding
* **Dependencies:** None. (You initiate the project).
* **Target Files:** `src/verify_env.py`, `requirements.txt`, Git repository setup.
* **Instructions:** Initialize the `.venv` and install all required packages. Verify PyTorch and XGBoost are compiling correctly using the environment verification script. Push the base scaffolding to the team repository.

## Phase 2: Data Exploration & Preprocessing
* **Dependencies:** Raw data available in `data/raw/`.
* **Target Files:** `notebooks/01_EDA_and_Data_Prep.ipynb`, `src/data_prep.py`, `src/encoding.py`.
* **Instructions:** 
  1. Write parsing logic to map the specific attack strings (e.g., `smurf`, `buffer_overflow`) to the 5 target families (normal, dos, probe, r2l, u2r)[cite: 4].
  2. Implement strict deduplication to remove redundant rows[cite: 2, 3].
  3. Execute feature correlation analysis; drop columns exhibiting >90% collinearity[cite: 3].
  4. Apply logarithmic transformations ($log(1+x)$) to continuous byte/duration fields and implement hybrid categorical encoding (Frequency for `service`, One-Hot for `flag`/`protocol_type`)[cite: 3].
  5. Export the pristine, transformed matrices to `data/processed/`.
* **Handoff:** Notify Amber that processed data is ready for Random Forest baseline testing.

## Phase 3: Advanced Model Architecture (XGBoost & TabNet)
* **Dependencies:** Completion of Phase 2.
* **Target Files:** `src/models.py`.
* **Instructions:** Write the Python classes and Optuna objective functions for XGBoost and PyTorch TabNet. Ensure validation-based early stopping is configured to prevent overfitting[cite: 2]. Integrate Tomek Links boundary clearing explicitly inside the training folds of the Stratified K-Fold cross-validation loop to prevent data leakage.
* **Handoff:** Notify Kenneth that `src/models.py` is complete and ready for heavy execution.

## Phase 4: Project Management Oversight
* **Instructions:** Continuously monitor `contracts/rubric_compliance.md` to ensure all team deliverables align with the CCINSYSL course project specifications[cite: 1, 2]. Ensure every member is prepared for their specific video presentation segment[cite: 1].