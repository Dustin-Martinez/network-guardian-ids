# Team Task Delegation Matrix: Network Guardian IDS
ctrl+shift+V for much cleaner look  and use the same to revert

This document formalizes the division of labor across the project lifecycle. Each member has a dedicated operational mandate detailing their exact phases, dependencies, and file responsibilities.

## Team Roster & Task Board References

| Member | Primary Role | Secondary Role | Operational Mandate |
| :--- | :--- | :--- | :--- |
| **Kit Dustin** (User) | Project Manager | Data Preparation & Advanced Model Developer | See `tasks/role_1.md` |
| **Markie** | Paper Lead | Evaluation, Explainability (XAI) & Backend | See `tasks/role_2.md` |
| **Amber** | Model Developer (Random Forest) | UI / UX Designer | See `tasks/role_3r.md` |
| **Kenneth** | Video Producer & Technical Tester | Execution & Verification Lead | See `tasks/role.md` |

## Workflow & Presentation Hand-Off Protocol

1. **Phase 1 (Data Prep & Modeling Code):** Kit Dustin builds the data preparation pipeline and writes the core logic for XGBoost and TabNet. Amber writes the Random Forest logic.
2. **Phase 2 (Execution & Tuning):** Kenneth takes over the finalized scripts to run heavy training loops, Optuna tuning, and verification across all models under Stratified K-Fold splits.
3. **Phase 3 (Evaluation & UI):** Markie executes the evaluation and SHAP explainability analyses using the trained models. Markie and Amber concurrently build and link the FastAPI backend and TSX frontend.
4. **Phase 4 (Documentation & Video Delivery):** Markie and Kenneth finalize the written documentation[cite: 1, 2]. Kenneth produces the final video presentation (`.mp4`), ensuring all members appear on-camera to present their respective components[cite: 1].