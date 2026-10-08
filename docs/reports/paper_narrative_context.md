# Paper Narrative Context

**Purpose:** Provide Markie (Role 2) with the narrative framing, key
facts, and source pointers needed to write the paper's Introduction,
Problem Statement, and Methodology sections.

**Audience:** Markie. This is source material, not a draft. Use the
content directly, adapt the phrasing, and pull the concrete numbers
from the locations listed under each section.

**Owner:** Kit (Role 1). Frozen for the sprint.

**Related documents:**
- `docs/reports/paper_structure.md` — the paper's section outline
- `docs/reports/role-1-phase-2-kit-data-preparation.md` — full data
  preparation details
- `docs/reports/role-1-phase-3-kit-model-architecture.md` — full
  model development details
- `docs/contracts/api_data_contract.md` — feature ordering and
  payload schemas
- `data/processed/*.json` — frozen artifact contracts

---

## 1. The Problem

**Use in:** paper section I (Introduction).

Security Operations Centers (SOCs) are the teams inside organizations
responsible for monitoring network traffic and detecting attacks.
Modern SOCs process millions of connection logs per day. Traditional
rule-based firewalls work for known attack signatures but miss novel
attacks and generate overwhelming numbers of false alarms. Analysts
burn out. Real threats slip through the noise.

Machine learning offers an alternative: instead of hand-written rules,
train models to learn patterns from historical traffic and generalize
to attacks not explicitly described in advance. This project builds
and evaluates such a system on the standard academic benchmark for
network intrusion detection.

**Where to find more:**
- Problem motivation and attack family definitions:
  `docs/reports/role-1-phase-2-kit-data-preparation.md` section 4.
- Master project framing: the project overview document.

---

## 2. The Research Question

**Use in:** paper section I (Introduction), subsection on objectives.

The project answers one primary question and one sub-question.

**Primary question:**

Does a hybrid pipeline that combines deduplication, correlation
pruning, log transformation of skewed features, and hybrid categorical
encoding produce materially different detection performance across
three algorithmic families (bagging, gradient boosting, and deep
attention) on the severely imbalanced KDD Cup 1999 multi-class
problem?

**Sub-question:**

Which class-level metrics reveal the differences that aggregate
accuracy hides?

The comparison is a scientific study, not a hyperparameter search. The
goal is to characterize how each algorithm family behaves on the same
frozen data, with the same preprocessing, under the same evaluation
protocol.

**Where to find more:**
- Evaluation metrics chosen and rationale:
  `docs/reports/role-1-phase-3-kit-model-architecture.md` section 7.
- Class imbalance mechanics:
  `docs/reports/role-1-phase-2-kit-data-preparation.md` section 5.

---

## 3. The Five Classes

**Use in:** paper section I (Introduction), attack family discussion.

The system classifies each network connection into one of five
categories.

| Class | Description | Share of raw data | Examples |
|---|---|---|---|
| normal | Baseline, non-malicious traffic | approximately 53 percent | user sessions, server responses |
| dos | Denial of Service | approximately 47 percent of attacks | smurf, neptune, back, teardrop |
| probe | Surveillance and port scanning | approximately 4 percent | satan, ipsweep, nmap, portsweep |
| r2l | Remote to Local unauthorized access | under 1 percent | guess_passwd, ftp_write, warezmaster |
| u2r | User to Root privilege escalation | under 0.1 percent | buffer_overflow, rootkit, loadmodule |

DoS is loud and detectable from byte counts and connection rates.
Probe is quieter but leaves scanning signatures. R2L and U2R are the
hard cases. R2L attacks resemble legitimate login activity. U2R
attacks are rare enough that a model trained on raw counts will
effectively ignore them.

The dataset contains 23 distinct attack strings grouped into these
four attack families. The grouping follows the standard
`training_attack_types.txt` convention shipped with the KDD Cup 1999
distribution.

**Where to find more:**
- Full label mapping table:
  `docs/reports/role-1-phase-2-kit-data-preparation.md` section 4.
- Class distribution before and after deduplication:
  `docs/reports/role-1-phase-2-kit-data-preparation.md` section 5 and
  section 9.5.
- Frozen class order: `data/processed/class_order.json`.

---

## 4. The Dataset

**Use in:** paper section II.1 (Data Understanding).

The project uses the KDD Cup 1999 dataset, the standard academic
benchmark for network intrusion detection research.

**Provenance:**

- Origin: derived from the 1998 DARPA Intrusion Detection Evaluation
  Program, hosted at MIT Lincoln Laboratory.
- Distribution: UCI Machine Learning Repository.
- Version: 10 percent training subset (`KDDTrain+`), 494,021 records.
- Reference: the original KDD Cup 1999 paper by Stolfo et al.

**Structure:**

- 41 features per record.
- 1 label column: the attack string.
- All features are numeric or categorical strings. No timestamps, no
  raw bytes.
- The 41 features were already engineered by the dataset authors.
  They are per-connection statistics, not raw packet captures.

**Known limitations (to be stated explicitly in the paper):**

- Traffic reflects a 1998 simulated network environment.
- Attack patterns do not generalize to modern production networks
  without retraining.
- The dataset is dominated by DoS attacks. U2R is nearly absent.
- Duplicate records make up roughly 70 percent of the raw file.

These limitations are documented, not hidden. Stating them
demonstrates awareness of the benchmark's scope.

**Where to find more:**
- Full data understanding writeup:
  `docs/reports/role-1-phase-2-kit-data-preparation.md` section 3.
- Deduplication counts:
  `docs/reports/role-1-phase-2-kit-data-preparation.md` section 5.
- Split contract with exact train/test distributions:
  `data/processed/split_indices.json`.

---

## 5. Why Macro F1

**Use in:** paper section II.3 (Data Preparation) or section III
(Methodology), subsection on evaluation metrics.

Accuracy is the wrong metric for this dataset.

Normal and DoS together account for approximately 97 percent of the
data. A model that predicts `normal` for every row achieves roughly
53 percent accuracy and detects zero attacks. A model that learns to
separate normal from DoS but ignores the three rare classes achieves
above 95 percent accuracy while missing every U2R and R2L attack.

Macro F1 weights each class equally. A perfect U2R prediction
contributes the same as a perfect Normal prediction. This forces the
pipeline to give the rare, high-severity classes a fair chance.

**Where to find more:**
- Metric rationale:
  `docs/reports/role-1-phase-3-kit-model-architecture.md` section 7.
- Class imbalance weights actually applied:
  `docs/reports/role-1-phase-3-kit-model-architecture.md` section 7.
- Per-class metrics final values:
  `outputs/03_evaluation/per_class_metrics.csv`.

---

## 6. The Three-Model Comparison

**Use in:** paper section III (Machine Learning Model Development).

Three algorithm families, one model per family.

### Random Forest — bagging ensemble

A collection of decision trees trained on bootstrap samples of the
training data. Each tree sees a random subset of features at each
split. Predictions are aggregated by majority vote or averaged
probability. Random Forest is robust to noisy features, provides
out-of-bag error estimates for free, and serves as a strong, stable
baseline. It is the natural starting point.

**Owner:** Amber (Role 3). Code in `src/models.py` RF section,
contract at `docs/contracts/role-3-rf-architecture-spec.md`.

### XGBoost — gradient tree boosting

A sequential ensemble where each new tree is fit to the residuals of
the previous ensemble. Regularized by design, handling missing values
natively, and optimizing a differentiable loss. XGBoost is the
standard high-performance model on tabular data and typically leads
on balanced classification benchmarks.

**Owner:** Kit (Role 1) for code, Kenneth (Role 4) for execution.
Contract at `docs/contracts/role-4-training-execution-spec.md`.

### TabNet — deep tabular attention

A neural network architecture designed specifically for tabular data.
Uses sequential attention to select a sparse subset of features at
each decision step. Produces interpretable attention masks that
identify which features contributed to each prediction. Adds a deep
learning arm to the comparison and provides an alternative form of
explainability to SHAP.

**Owner:** Kit (Role 1) for code, Dwayne (Role 5) for execution.
Contract at `docs/contracts/role-5-training-execution-spec.md`.

The progression from bagging to boosting to attention is deliberate.
It represents increasing model expressiveness and decreasing
interpretability, and it produces a defensible narrative for the
paper's model selection section.

**Where to find more:**
- Full model configuration details:
  `docs/reports/role-1-phase-3-kit-model-architecture.md` section 5.
- Search spaces:
  `docs/reports/role-1-phase-3-kit-model-architecture.md` sections
  5.1 and 5.2.
- Final hyperparameters:
  `models/*.meta.json`, field `best_params`.

---

## 7. Data Preparation Summary

**Use in:** paper section II (Data Understanding and Preparation).

Seven steps, applied in order.

| Step | Operation | Reason |
|---|---|---|
| 1. Target mapping | 23 attack strings to 5 families | Creates the classification problem |
| 2. Deduplication | Drop rows identical across the 41 features | Removes artificial inflation and train/test leakage risk |
| 3. Constant-column removal | Drop columns with a single value | Zero predictive signal |
| 4. Correlation pruning | Drop features with absolute Pearson correlation above 0.90 | Removes redundant information |
| 5. Log transformation | Apply `log(1+x)` to `duration`, `src_bytes`, `dst_bytes` | Compresses extreme skew |
| 6. Hybrid categorical encoding | Frequency encode `service`; one-hot encode `protocol_type` and `flag` | Preserves information without exploding dimensionality |
| 7. Train/test split | 75/25, stratified on the target family, random state 42, frozen | Enables evaluation without leakage |

Two mandatory considerations:

- Encoders and scalers are fit on the training partition only. The
  test partition is transformed using frozen artifacts.
- Tomek Links resampling is applied only inside each cross-validation
  fold's training partition. Validation partitions are never
  resampled.

**Where to find more:**
- Full data preparation writeup:
  `docs/reports/role-1-phase-2-kit-data-preparation.md` sections 4
  through 10.
- Split configuration and class distribution:
  `data/processed/split_indices.json`.
- Feature ordering after encoding:
  `data/processed/feature_names.json`.
- Encoder artifacts:
  `data/processed/encoder_service.pkl`,
  `data/processed/encoder_onehot_protocol_flag.pkl`.

---

## 8. Training and Evaluation Protocol

**Use in:** paper section III (Methodology), subsection on training
procedure.

**Cross-validation:**

- 5-fold stratified for Random Forest and XGBoost.
- 3-fold stratified for TabNet.
- Random state 42 for all folds.
- Stratification on the target family.

The TabNet reduction from 5 to 3 folds is deliberate. With 39 U2R
examples in the training partition, 5-fold leaves approximately 7 U2R
per validation fold, which produces unstable per-class metrics. 3-fold
leaves approximately 13 U2R per fold, which is the minimum for a
statistically meaningful estimate of per-class recall.

**Hyperparameter optimization:**

- Optuna with TPE sampler, seed 42.
- MedianPruner with warmup.
- Objective: mean Macro F1 across folds.
- Trial budgets: 20 for Random Forest, 30 for XGBoost, 20 for TabNet.
- Search spaces bounded to prevent overfitting-prone configurations
  (for example, XGBoost `max_depth` capped at 10).

**Overfitting prevention:**

- In-fold Tomek Links.
- Validation-based early stopping for XGBoost and TabNet.
- Bounded search spaces.
- Cross-fold mean objective.
- Structural test-set isolation: no training function accepts the test
  partition as input.

**Final refit:**

- After the study, the best configuration is refit on the full cleaned
  training pool (post Tomek Links).
- No early stopping during the final refit. The number of boosting
  rounds or epochs is taken from the best trial.
- Class weights for the refit are computed from the post-Tomek-Links
  training pool, not the raw pool.

**Test-set usage:**

- The test set is evaluated exactly once, in Notebook 03, by Dwayne.
- No tuning or model selection consults the test set at any point.

**Where to find more:**
- Full methodology:
  `docs/reports/role-1-phase-3-kit-model-architecture.md` sections 5,
  6, and 7.
- Search spaces and trial budgets:
  `docs/reports/role-1-phase-3-kit-model-architecture.md` section 5.
- Overfitting prevention design:
  `docs/reports/role-1-phase-3-kit-model-architecture.md` section 6.
- XGBoost execution contract:
  `docs/contracts/role-4-training-execution-spec.md`.
- TabNet execution contract:
  `docs/contracts/role-5-training-execution-spec.md`.

---

## 9. Explainability Approach

**Use in:** paper section V or VI (Model Comparison and Evaluation),
subsection on interpretability.

Two complementary explainability techniques.

**SHAP for tree models (Random Forest and XGBoost):**

- Global feature importance shows which features drive predictions
  across the dataset.
- Local explanations show why a specific packet was classified a
  particular way. These are the artifacts a security analyst would
  actually use.
- SHAP values are theoretically grounded in cooperative game theory,
  which makes them defensible in academic work.

**Attention masks for TabNet:**

- TabNet's sequential attention mechanism produces a mask per input
  indicating which features were selected at each decision step.
- The masks provide an alternative, architecturally native form of
  interpretability.
- Comparing SHAP rankings with attention rankings is a legitimate
  contribution to the paper's analysis.

**Where to find more:**
- Explainability approach:
  `docs/reports/role-1-phase-3-kit-model-architecture.md` section 5
  and the master project specification.
- Output figures:
  `outputs/03_evaluation/shap_summary_rf.png`,
  `outputs/03_evaluation/shap_summary_xgb.png`,
  `outputs/03_evaluation/shap_local_example.png`,
  `outputs/03_evaluation/tabnet_attention_mask.png`.
- Dwayne's mandate for figure production:
  `docs/tasks/5.md` phases 4 and 5.

---

## 10. Expected Results

**Use in:** paper section V (Model Comparison and Evaluation), and to
calibrate the paper's claims.

Based on published KDD Cup 1999 baselines and the model lineup, the
realistic ranges are:

| Model | CV Macro F1 range | U2R recall range | R2L recall range |
|---|---|---|---|
| Random Forest | 0.84 to 0.90 | 0.40 to 0.60 | 0.65 to 0.80 |
| XGBoost | 0.88 to 0.93 | 0.50 to 0.70 | 0.70 to 0.85 |
| TabNet | 0.85 to 0.91 | 0.45 to 0.65 | 0.65 to 0.80 |

These are ranges, not targets. Any value within range is a strong
result for this dataset. Values below range trigger investigation.
Values above range are worth highlighting.

Do not overclaim. If the final numbers sit at the median of these
ranges, the paper reports them honestly. The interesting scientific
result is the comparison across families, not a headline number.

**Where to find more:**
- Final cross-validation results:
  `outputs/02_training/model_comparison.csv`.
- Final test-set results:
  `outputs/03_evaluation/test_set_evaluation.json`.
- Per-class metrics:
  `outputs/03_evaluation/per_class_metrics.csv`.
- Confusion matrices:
  `outputs/03_evaluation/confusion_matrix_*.png`.

---

## 11. What to Emphasize in the Paper

**Use in:** paper section VIII (Executive Summary) and section V.4
(Model Recommendation).

Three points worth returning to throughout the paper.

**First: the rare classes drive the interesting result.** Aggregate
accuracy is nearly meaningless on this dataset. The comparison
between models is interesting because of how they handle U2R and R2L,
not because of their overall score.

**Second: structural anti-leakage discipline.** The pipeline prevents
test-set leakage by function signature, not by discipline. This is
unusual in student projects and worth stating clearly.

**Third: interpretability is not decoration.** SHAP and attention
masks are what turn a classifier into a usable security tool. The
paper should argue this, not just present the plots.

---

## 12. What to Avoid in the Paper

**Use in:** all sections.

Four things to avoid.

**Do not claim production readiness.** The system is a research
prototype trained on a 1998 benchmark. State this limitation
explicitly.

**Do not compare against modern IDS systems.** The KDD Cup 1999
benchmark is not comparable to CIC-IDS-2017 or modern production
traffic. Comparisons should be against published KDD Cup 1999
baselines only.

**Do not hide the fold-count difference for TabNet.** The 3-fold
decision is a deliberate response to class imbalance, not a
shortcut. State it and justify it.

**Do not present accuracy as a headline metric.** Macro F1 is the
correct metric. If accuracy appears at all, it appears with a caveat
about imbalance.

---

## 13. Source Pointer Index

A consolidated reference table. Every concrete number, table, or
figure in the paper traces to one of these locations.

| Paper content | Source |
|---|---|
| Raw record count, column count, feature types | `docs/reports/role-1-phase-2-kit-data-preparation.md` section 3 |
| Class distribution before and after dedup | `docs/reports/role-1-phase-2-kit-data-preparation.md` section 5 |
| Deduplication count | `docs/reports/role-1-phase-2-kit-data-preparation.md` section 5 |
| Constant columns dropped | `docs/reports/role-1-phase-2-kit-data-preparation.md` section 6.1 |
| Correlated features dropped | `docs/reports/role-1-phase-2-kit-data-preparation.md` section 6.2 |
| Log-transformed columns | `docs/reports/role-1-phase-2-kit-data-preparation.md` section 7 |
| Encoded feature list (43 features) | `docs/reports/role-1-phase-2-kit-data-preparation.md` section 8.3 and `data/processed/feature_names.json` |
| Train/test split configuration | `docs/reports/role-1-phase-2-kit-data-preparation.md` section 9 and `data/processed/split_indices.json` |
| Class distribution in train and test | `data/processed/split_indices.json` |
| Model search spaces | `docs/reports/role-1-phase-3-kit-model-architecture.md` section 5 |
| Trial budgets and fold counts | `docs/reports/role-1-phase-3-kit-model-architecture.md` section 5 |
| Overfitting prevention mechanisms | `docs/reports/role-1-phase-3-kit-model-architecture.md` section 6 |
| Class imbalance handling details | `docs/reports/role-1-phase-3-kit-model-architecture.md` section 7 |
| Serialization formats | `docs/reports/role-1-phase-3-kit-model-architecture.md` section 8 |
| Final hyperparameters per model | `models/rf_baseline.meta.json`, `models/xgb_optuna.meta.json`, `models/tabnet_best.meta.json` |
| Cross-validation metrics per model | `outputs/02_training/*_cv_scores.csv` and the `cv_mean_macro_f1` field in each meta sidecar |
| Model comparison table | `outputs/02_training/model_comparison.csv` |
| Per-class metrics | `outputs/03_evaluation/per_class_metrics.csv` and `per_class_metrics_normalized.csv` |
| Confusion matrices | `outputs/03_evaluation/confusion_matrix_*.png` |
| Precision-recall curves | `outputs/03_evaluation/pr_curve_u2r.png` and `pr_curve_r2l.png` |
| SHAP outputs | `outputs/03_evaluation/shap_summary_rf.png`, `shap_summary_xgb.png`, `shap_local_example.png` |
| TabNet attention mask | `outputs/03_evaluation/tabnet_attention_mask.png` |
| Model comparison visual | `outputs/03_evaluation/model_comparison_visual.png` |
| Test-set evaluation | `outputs/03_evaluation/test_set_evaluation.json` |
| Discovery log candidates | Phase 1, 2, and 3 reports in `docs/reports/` |
| Feature order and payload schema for the dashboard | `docs/contracts/api_data_contract.md` |

If a number in the paper does not trace to a row in this table, it
does not go in the paper. This is the traceability rule.

---

## 14. Where the Sprint Reports Map to Paper Sections

A cross-reference for Markie when he pulls source material.

| Paper section | Primary report to pull from |
|---|---|
| I. Introduction | `docs/reports/paper_narrative_context.md` (this file) sections 1, 2, 3 |
| II.1 Data Understanding | `docs/reports/role-1-phase-2-kit-data-preparation.md` sections 3, 4, 5 |
| II.2 Feature Description | `docs/reports/role-1-phase-2-kit-data-preparation.md` sections 3, 8.3, and `data/processed/feature_names.json` |
| II.3 Data Preparation | `docs/reports/role-1-phase-2-kit-data-preparation.md` sections 5 through 11 |
| III.1 Random Forest | `docs/contracts/role-3-rf-architecture-spec.md` and `models/rf_baseline.meta.json` |
| III.2 XGBoost | `docs/contracts/role-4-training-execution-spec.md`, `models/xgb_optuna.meta.json`, `docs/reports/role-1-phase-3-kit-model-architecture.md` section 5.1 |
| III.3 TabNet | `docs/contracts/role-5-training-execution-spec.md`, `models/tabnet_best.meta.json`, `docs/reports/role-1-phase-3-kit-model-architecture.md` section 5.2 |
| IV. Model Metadata | All three meta sidecars in `models/`, plus `outputs/02_training/model_comparison.csv` |
| V.1 Comparative Results | `outputs/02_training/model_comparison.csv` and `outputs/03_evaluation/per_class_metrics.csv` |
| V.2 Error Analysis | `outputs/03_evaluation/confusion_matrix_*.png` |
| V.3 Overfitting Analysis | `docs/reports/role-1-phase-3-kit-model-architecture.md` sections 6 and 11 |
| V.4 Model Recommendation | `docs/reports/role-1-phase-3-kit-model-architecture.md` section 10 |
| VI. Results and Visualizations | `outputs/03_evaluation/*` |
| VII. Discovery Log | `docs/reports/role-1-phase-1-kit-environment-setup.md` section 6 (Phase 1 issues), `role-1-phase-2-kit-data-preparation.md` section 14 (Phase 2 issues), `role-1-phase-3-kit-model-architecture.md` section 14 (Phase 3 issues) |
| VIII. Executive Summary | `docs/reports/paper_narrative_context.md` (this file) sections 1 through 10 |
| IX. Reflection | Individual members write their own; use the phase reports to recall specific issues they encountered |
| X. References | Cite the sources used in the reports: scikit-learn, XGBoost, PyTorch, pytorch-tabnet, imbalanced-learn, Optuna, SHAP, pandas, NumPy, matplotlib, seaborn, KDD Cup 1999, TabNet paper, XGBoost paper, SHAP paper, Optuna paper |