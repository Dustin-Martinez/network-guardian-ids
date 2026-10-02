# Video Presentation Script & Structure (5–8 Minutes)

*This guide outlines the structure, visual cues, and spoken script to ensure every team member speaks on-camera and fulfills all rubric requirements within the time limit[cite: 1, 2].*

## Part 1: The Problem & Significance (Speaker 1)
* **Visual:** Title slide, dashboard screenshot, and statistics on SOC analyst burnout.
* **Script:** "Welcome. Modern Security Operations Centers process millions of connections daily, leading to missed threats and high false-positive rates[cite: 1]. Network Guardian is our machine learning prototype designed to automate intrusion detection and accurately categorize threats into DoS, Probe, R2L, and U2R families[cite: 1, 4]."

## Part 2: Data Findings & Preparation (Speaker 2)
* **Visual:** EDA distribution plots, correlation heatmaps, and deduplication logs[cite: 2, 3].
* **Script:** "When exploring our dataset, we discovered significant class imbalance, skewed packet bytes, and redundant records[cite: 2, 3]. To prevent data leakage, we applied deduplication, correlation pruning, logarithmic transforms, and hybrid encoding before running our cross-validation splits[cite: 2, 3]."

## Part 3: Model Architecture & Comparison (Speaker 3)
* **Visual:** Architecture diagram showing Random Forest, XGBoost, and TabNet under Stratified K-Fold[cite: 1].
* **Script:** "To satisfy our requirement for diverse approaches, we compared three distinct paradigms: Random Forest for baseline bagging, XGBoost with Optuna hyperparameter tuning, and PyTorch TabNet for deep learning with sequential attention[cite: 1]."

## Part 4: Evaluation, Results & Recommendation (Speaker 4)
* **Visual:** Confusion matrices, Macro F1-Score comparison tables, and SHAP / Attention explanation plots[cite: 1, 2].
* **Script:** "Instead of relying on misleading accuracy scores, we optimized for Macro F1-Score[cite: 1]. XGBoost achieved the best balance of speed and detection rate, while TabNet provided critical forensic interpretability[cite: 1]. We recommend deploying XGBoost for real-time filtering backed by TabNet for deep forensic audits[cite: 1]."

## Part 5: Limitations & Individual Reflections (Speaker 5)
* **Visual:** Team on-camera closing slide, summary of lessons learned, and future improvements[cite: 1, 2].
* **Script:** "While our prototype excels on benchmark data[cite: 3], real-world deployment requires streaming telemetry pipelines. As a team, this project taught us that rigorous data preparation and evaluating beyond simple accuracy are the true foundation of professional machine learning[cite: 1, 2]. Thank you."