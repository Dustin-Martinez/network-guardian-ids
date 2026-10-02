# Operational Mandate: Role 4 - Kenneth
**Title:** Execution Lead, Technical Tester & Video Producer

## Phase 1: Environment & Test Automation Setup
* **Dependencies:** Wait for Kit Dustin to push `requirements.txt`.
* **Target Files:** `src/verify_env.py`, `src/main.py`.
* **Instructions:** Clone the repository and execute the verification script. Ensure your local machine (or Google Colab environment) can allocate sufficient memory and processing power to handle the heavy execution loads[cite: 1].

## Phase 2: Master Execution & Model Tuning
* **Dependencies:** **BLOCKER** - Wait for Kit Dustin and Amber to finalize `src/models.py` and `src/data_prep.py`.
* **Target Files:** `notebooks/02_Model_Training.ipynb`.
* **Instructions:** 
  1. Execute the master Stratified K-Fold cross-validation loops for all three models (Random Forest, XGBoost, TabNet).
  2. Run the Optuna hyperparameter optimization trials[cite: 1]. 
  3. Monitor validation loss carefully to ensure early stopping triggers correctly, recording this process for the Overfitting Analysis requirement[cite: 2].
  4. Serialize and save the final trained models to the `models/` directory using `joblib` and `torch`.
* **Handoff:** Notify Markie that trained artifacts are ready for evaluation.

## Phase 3: Documentation Co-Authoring & Verification
* **Dependencies:** Wait for Markie to draft the initial reports.
* **Target Files:** `reports/discovery_log.md`, `reports/executive_summary.md`.
* **Instructions:** Review the documentation to ensure the empirical results (training times, hardware limits, optimization barriers) you experienced during Phase 2 are accurately recorded in the Discovery Log[cite: 2]. Verify that the notebooks execute top-to-bottom without error on a fresh environment[cite: 1, 2].

## Phase 4: Video Production & Editing
* **Dependencies:** Finalization of all code and presentation scripts.
* **Target Files:** Final `.mp4` video file (5–8 minutes)[cite: 1].
* **Instructions:** Coordinate the recording sessions. Ensure every member is visible on-camera and speaks[cite: 1]. Splice the technical screen-shares (UI demonstration, confusion matrices) with the speaker feeds. Edit for clarity, flow, and strict adherence to the 5–8 minute time limit[cite: 1].