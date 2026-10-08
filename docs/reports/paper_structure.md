# Paper Structure

This document defines the structure of the project's final paper. It
contains two formats:

1. **Professor Format** — the graded deliverable, structured to the
   CCINSYSL course rubric. This is what is submitted for grading.
2. **Portfolio Format** — an expanded academic version of the same
   content, formatted for a professional portfolio or conference
   submission. This is a supplemental deliverable.

The professor format is the primary deliverable. The portfolio format
is built on top of it, not a replacement.

Owner: Markie (Role 2). Frozen by Kit (Role 1).

---

# Part 1 — Professor Format (Primary Deliverable)

**Purpose:** Satisfy the CCINSYSL course rubric.

**Audience:** The professor and any teaching assistants reviewing
against the rubric.

**Constraints:**
- Follow the professor's required section headings exactly. Roman
  numerals at the top level, Arabic decimals at the sub-level.
- Citation style: APA.
- No page limit. Write to what the content requires.
- Cover page must match the professor's template exactly.

---

## Cover Page

Reproduce the professor's cover page template verbatim.

Fields required:

| Field | Value |
|---|---|
| Course | INTRODUCTION TO INTELLIGENT SYSTEMS (CCINSYSL) |
| Project Title | Network Guardian IDS — A Hybrid Machine Learning Approach to Multi-Class Network Intrusion Detection |
| Submitted by | All team members, listed as "Last name, First name M.I." |
| Submitted to | Professor's full name, with the designation "Professor" |
| Date | OCTOBER 2026 |

Team member order: Kit Dustin, Markie, Amber, Kenneth, Dwayne.
(Surname-first format per the professor's template.)

---

## Section I — Introduction

Purpose: introduce the project, the problem, and the four attack
families.

Content checklist:

- Brief description and purpose of the Network Guardian machine
  learning-based Intrusion Detection System (IDS).
- Discussion of the problem of identifying normal network connections
  and detecting network intrusions using machine learning.
- Brief discussion of the four attack families:
  - DoS (Denial of Service)
  - R2L (Remote to Local)
  - U2R (User to Root)
  - Probe
- Explanation of the overall purpose of developing and comparing
  machine learning classification approaches for network intrusion
  detection.

Source material: `docs/reports/paper_narrative_context.md`.

---

## Section II — Data Understanding and Preparation

Purpose: document the team's process of understanding and preparing
the dataset.

### II.1 Data Understanding

Initial findings from examining the dataset. Include:

- Number of records
- Number of features
- Feature data types
- Target/class variable
- Class distribution
- Missing or invalid values
- Duplicate records
- Categorical and numerical features

Source material: `docs/reports/role-1-phase-2-kit-data-preparation.md`,
sections 3 through 5. Specific numbers to report:

- Raw records: 494,021
- Raw columns: 42 (41 features + 1 label)
- Post-deduplication records: 145,584
- Duplicate rows removed: 348,437 (70.5 percent)
- Class distribution pre-dedup and post-dedup (from `split_indices.json`)
- Missing values: none in the KDD Cup 1999 dataset after loading
- Categorical features: `protocol_type`, `service`, `flag`
- Numerical features: the remaining 38

### II.2 Feature Description

Include a table with columns: Feature Name, Data Type, Description,
Role.

The table must list all 41 features of the KDD Cup 1999 dataset. At a
minimum, describe:

- The three categorical features (`protocol_type`, `service`, `flag`)
  and their cardinality.
- The continuous features and their value ranges.
- The per-connection statistics (`count`, `srv_count`, and the
  `_rate` family).
- Which features are used as inputs and which column is the target.

Explain the role of each feature group in identifying whether a
network connection is normal or belongs to an attack category.

Final feature count for the models: 43 features after encoding
(31 numeric post-pruning, plus 1 frequency-encoded, plus 3 one-hot for
`protocol_type`, plus 11 one-hot for `flag`; minus the dropped
`service`, `protocol_type`, and `flag` originals).

### II.3 Data Preparation

Document each preparation step performed. For each step, explain why
it was performed.

Required steps:

| Step | Purpose |
|---|---|
| Target mapping | Map 23 attack strings to 5 canonical families |
| Data cleaning | Remove constant columns and invalid rows |
| Missing/invalid values | None present; note the check performed |
| Deduplication | Remove byte-identical rows across the 41 features |
| Encoding categorical features | Frequency encode `service`; one-hot encode `protocol_type` and `flag` |
| Feature transformation | Apply `log(1+x)` to `duration`, `src_bytes`, `dst_bytes` |
| Feature selection | Drop features with absolute Pearson correlation above 0.90 |
| Handling class imbalance | Class weighting; Tomek Links resampling inside training folds only |
| Dataset splitting | 75/25 stratified on the target family, random state 42 |
| Feature scaling | StandardScaler fit on training data only, applied only to TabNet |

Source material: `docs/reports/role-1-phase-2-kit-data-preparation.md`,
sections 4 through 11.

---

## Section III — Machine Learning Model Development

Purpose: document the three machine learning models developed and
compared. Models are presented in algorithmic progression order.

### III.1 Random Forest

#### III.1.1 Model Description

Describe the Random Forest classifier and its use for network
intrusion detection. Cover the bagging principle, why it handles
class imbalance well, and why it serves as the baseline.

#### III.1.2 Model Configuration

Present the hyperparameter search space and the best configuration
found by Optuna.

| Parameter | Search range | Best value |
|---|---|---|
| `n_estimators` | 100–500 (step 50) | From `models/rf_baseline.meta.json` |
| `max_depth` | 5–30 or None | From `models/rf_baseline.meta.json` |
| `min_samples_split` | 2–20 | From `models/rf_baseline.meta.json` |
| `min_samples_leaf` | 1–10 | From `models/rf_baseline.meta.json` |
| `max_features` | sqrt, log2 | From `models/rf_baseline.meta.json` |
| `criterion` | gini, entropy | From `models/rf_baseline.meta.json` |
| `class_weight` | balanced, balanced_subsample | From `models/rf_baseline.meta.json` |

Fixed parameters: `random_state=42`, `n_jobs=-1`, `oob_score=True`,
`bootstrap=True`.

#### III.1.3 Training Procedure

Describe: 20 Optuna trials, 5-fold stratified cross-validation,
in-fold Tomek Links, Macro F1 objective, final refit on the full
cleaned training pool.

Source: `docs/contracts/role-3-rf-architecture-spec.md`, sections 6
and 7.

#### III.1.4 Model Results

Include:

- Cross-validation Macro F1 (mean and standard deviation)
- OOB Macro F1
- Per-class recall on the CV validation folds
- Training time
- Confusion matrix on the test set (from Notebook 03)

Source: `models/rf_baseline.meta.json`, `outputs/03_evaluation/confusion_matrix_rf.png`.

### III.2 XGBoost

Same four-subsection structure as III.1. Replace the model-specific
content:

- Algorithm: gradient tree boosting
- Search space: 10 parameters (learning rate, max depth, min child
  weight, gamma, subsample, colsample bytree, reg alpha, reg lambda,
  max delta step, n estimators)
- Training procedure: 30 Optuna trials, 5-fold stratified CV,
  early stopping at 20 rounds, in-fold Tomek Links, class-weighted
  sample weights, final refit on the full cleaned training pool
- Results from `models/xgb_optuna.meta.json` and
  `outputs/03_evaluation/confusion_matrix_xgb.png`

Source: `docs/contracts/role-4-training-execution-spec.md`.

### III.3 TabNet

Same four-subsection structure. Replace model-specific content:

- Algorithm: deep tabular learning with sequential attention
- Architecture and training search space: `n_d`, `n_a`, `n_steps`,
  `gamma`, `lambda_sparse`, `n_independent`, `n_shared`, `momentum`,
  `mask_type`, `batch_size`, `virtual_batch_size`
- Fixed parameters: `optimizer_fn=Adam`, `optimizer_params.lr=2e-2`,
  `device_name=cpu`, `max_epochs=30`, `patience=10`
- Training procedure: 20 Optuna trials, 3-fold stratified CV,
  in-fold Tomek Links, class-weighted loss, final refit on the full
  cleaned training pool
- Results from `models/tabnet_best.meta.json` and
  `outputs/03_evaluation/confusion_matrix_tabnet.png`

Source: `docs/contracts/role-5-training-execution-spec.md`.

Note: the 3-fold decision for TabNet (rather than 5-fold as used for
Random Forest and XGBoost) must be explained. The rationale is that
with only 39 U2R training examples, 5-fold leaves roughly 7 U2R per
validation fold, which produces unstable per-class metrics. 3-fold
leaves roughly 13 U2R per fold. See
`docs/reports/role-1-phase-3-kit-model-architecture.md`, section 5.3.

---

## Section IV — Model Metadata

Provide a single table summarizing the technical characteristics of
the three models.

| Metadata | Model 1 (Random Forest) | Model 2 (XGBoost) | Model 3 (TabNet) |
|---|---|---|---|
| Model Name | Random Forest Classifier | XGBoost Classifier | PyTorch TabNet Classifier |
| Algorithm / Approach | Tree bagging ensemble | Gradient tree boosting | Deep learning with sequential attention |
| Target Variable | `family` (5 classes) | `family` (5 classes) | `family` (5 classes) |
| Number of Input Features | 43 | 43 | 43 |
| Features Used | All encoded features | All encoded features | All encoded features |
| Training Data Size | 109,188 rows | 109,188 rows | 109,188 rows |
| Testing Data Size | 36,396 rows | 36,396 rows | 36,396 rows |
| Important Parameters | Best Optuna config | Best Optuna config | Best Optuna config |
| Random State | 42 | 42 | 42 |
| Evaluation Measures | Macro F1, per-class F1 | Macro F1, per-class F1 | Macro F1, per-class F1 |
| Training Time | From execution report | From execution report | From execution report |
| Prediction Time | From execution report | From execution report | From execution report |
| Main Result | CV Macro F1 and test Macro F1 | CV Macro F1 and test Macro F1 | CV Macro F1 and test Macro F1 |

Source for all values: `models/*.meta.json` and
`outputs/02_training/model_comparison.csv`.

---

## Section V — Model Comparison and Evaluation

### V.1 Comparative Results

A single comparison table with the three models as columns and the
following rows:

- CV Macro F1 (mean ± std)
- Test Macro F1
- Test weighted F1
- Per-class recall: normal, dos, probe, r2l, u2r
- Training time
- Prediction time

Source: `outputs/02_training/model_comparison.csv` and
`outputs/03_evaluation/per_class_metrics.csv`.

### V.2 Error Analysis

Discuss the errors produced by each model. Explain the significance of
false positives and false negatives in an Intrusion Detection System.

Key points:

- False negatives on rare classes (U2R, R2L) are the most severe
  failures: they represent undetected attacks.
- False positives erode analyst trust and create alert fatigue.
- The confusion matrices show structured errors, not random ones.
- R2L is commonly confused with Normal because R2L attacks mimic
  legitimate login activity.
- U2R is commonly confused with DoS because some privilege
  escalation attacks produce connection patterns similar to
  flooding.

Source: `outputs/03_evaluation/confusion_matrix_*.png` and
`outputs/03_evaluation/per_class_metrics.csv`.

### V.3 Overfitting Analysis

Report the training versus validation Macro F1 gap for each model.

| Model | Train Macro F1 | Validation Macro F1 | Gap |
|---|---|---|---|
| Random Forest | From meta | From meta | Difference |
| XGBoost | From meta | From meta | Difference |
| TabNet | From meta | From meta | Difference |

A gap under 0.10 is healthy. Above 0.15 indicates material
overfitting.

Explain the prevention mechanisms in place: in-fold Tomek Links,
validation-based early stopping, bounded search spaces, cross-fold
mean objective, structural test-set isolation.

Source: `docs/reports/role-1-phase-3-kit-model-architecture.md`,
sections 6 and 11.

### V.4 Model Recommendation

Recommend one model for deployment and justify the choice. Consider:

- Macro F1 performance across all classes, with emphasis on U2R and
  R2L recall.
- Training and prediction time.
- Interpretability (SHAP support, attention masks).
- Ease of deployment and inference cost.

Suggested primary recommendation: XGBoost. It typically leads on
Macro F1 on tabular data, has native SHAP support, and offers the best
balance of performance and inference cost. Present the reasoning
explicitly and reference the numbers from V.1.

---

## Section VI — Results and Visualizations

Present the following figures and tables in this section. Order
matters.

| Order | Figure / Table | Source file |
|---|---|---|
| 1 | Class distribution of the dataset | Generated from `split_indices.json` |
| 2 | Confusion matrix — Random Forest | `outputs/03_evaluation/confusion_matrix_rf.png` |
| 3 | Confusion matrix — XGBoost | `outputs/03_evaluation/confusion_matrix_xgb.png` |
| 4 | Confusion matrix — TabNet | `outputs/03_evaluation/confusion_matrix_tabnet.png` |
| 5 | Precision-recall curve — U2R | `outputs/03_evaluation/pr_curve_u2r.png` |
| 6 | Precision-recall curve — R2L | `outputs/03_evaluation/pr_curve_r2l.png` |
| 7 | Model comparison visual | `outputs/03_evaluation/model_comparison_visual.png` |
| 8 | SHAP summary — Random Forest | `outputs/03_evaluation/shap_summary_rf.png` |
| 9 | SHAP summary — XGBoost | `outputs/03_evaluation/shap_summary_xgb.png` |
| 10 | SHAP local explanation | `outputs/03_evaluation/shap_local_example.png` |
| 11 | TabNet attention mask | `outputs/03_evaluation/tabnet_attention_mask.png` |

Every figure must have a caption. Every caption must reference its
source file.

---

## Section VII — Discovery Log

Document the team's actual development journey. The section must
demonstrate the real process, not just the final successful approach.

Required content:

- Questions raised during the project
- Initial observations
- Problems encountered
- Approaches attempted
- Approaches that did not work
- Changes made to the approach
- Important discoveries
- Lessons learned from mistakes

Candidates to include (drawn from the actual sprint):

- The Python 3.13 venv failure during Phase 1 and the resolution on
  Python 3.11.9.
- The `kddcup.names.txt` parse failure (expected 43 lines, found 42).
- The `normal` class missing from `training_attack_types.txt` and the
  runtime injection fix.
- The object-dtype `y_train.npy` load error and the switch to fixed-width
  Unicode.
- The Jupyter kernel working directory issue and the path-fix cell.
- The TabNet feasibility measurement (22 seconds per epoch) leading to
  the reduced trial budget.
- The `History` callback error in pytorch-tabnet and the switch to
  `model.history`.
- The raw-vs-engineered feature debate and the decision to retain
  feature engineering without an ablation.

Source: the Phase 1, Phase 2, and Phase 3 reports under `docs/reports/`.

---

## Section VIII — Executive Summary

Answer six questions in plain language. No technical jargon where
avoidable.

1. What problem did we set out to solve, and why does it matter?
2. What did we discover about the data that shaped our decisions?
3. Which approaches did we compare, and how did we judge them?
4. What do we recommend, and what evidence supports it?
5. What are the limitations of our work, and what would we do next?
6. What was our biggest mistake or surprise, and what did we learn
   from it?

Target length: one page total. Short paragraphs. Direct answers.

---

## Section IX — Reflection

Each team member writes an individual reflection. The reflection must
discuss eight points:

1. What did you learn about machine learning and intrusion detection?
2. What did you learn from exploring and preparing the dataset?
3. What did you learn from comparing different classification
   approaches?
4. What challenges did you encounter?
5. How did you respond to mistakes or unexpected results?
6. What did you learn about evaluating machine learning models beyond
   accuracy?
7. How can machine learning be applied to real-world cybersecurity
   problems?
8. What would you improve if you were given additional time?

One subsection per member, in this order:

- Name Of Student 1 (Kit Dustin)
- Name Of Student 2 (Markie)
- Name Of Student 3 (Amber)
- Name Of Student 4 (Kenneth)
- Name Of Student 5 (Dwayne)

Each reflection should be substantive. Aim for 400 to 700 words per
person.

---

## Section X — References

Cite all external sources used throughout the project.

Categories to include:

- Machine learning documentation (scikit-learn, XGBoost, PyTorch,
  pytorch-tabnet, imbalanced-learn, Optuna, SHAP)
- Python library documentation (pandas, NumPy, matplotlib, seaborn)
- Research papers (the original KDD Cup 1999 paper, TabNet paper,
  XGBoost paper, SHAP paper, Optuna paper)
- Tutorials
- Books
- Websites
- Other academic or technical resources

**AI tool disclosure:** any AI tools used during the project must be
disclosed according to the project requirements. Include a subsection
titled "AI Tool Disclosure" listing each tool and its role.

Citation style: APA. Follow the format for each source type:

- Book: Author, A. A. (Year). *Title of work: Capital letter also for
  subtitle*. Publisher.
- Journal article: Author, A. A., & Author, B. B. (Year). Title of
  article. *Title of Journal, volume*(issue), pages.
  https://doi.org/xxxx
- Website: Author or Organization. (Year, Month Day). *Title of page*.
  Site Name. URL
- Software documentation: Organization. (Year). *Software name*
  (Version X.X) [Computer software]. URL

---

# Part 2 — Portfolio Format (Supplemental Deliverable)

**Purpose:** Demonstrate the depth of the project at a level
appropriate for an academic portfolio or conference submission.

**Audience:** Reviewers, prospective employers, or anyone evaluating
the project's technical quality beyond the graded rubric.

**Relationship to the Professor Format:** Same content as the
professor format. The portfolio version restructures the material as
an academic paper, expands the methodology and discussion, and adds
Related Work and Threats to Validity. It does not contain additional
experiments.

---

## Title Page

- Title: Network Guardian IDS — A Comparative Study of Bagging,
  Boosting, and Deep Attention Architectures for Multi-Class Network
  Intrusion Detection
- Author list with affiliations
- Corresponding author contact

## Abstract (250 words)

Structured abstract: Background, Objective, Methods, Results,
Conclusion.

## Keywords

Intrusion Detection, Machine Learning, KDD Cup 1999, Explainable AI,
Tabular Deep Learning, Anomaly Detection.

## 1. Introduction

- 1.1 Motivation
- 1.2 Problem Statement
- 1.3 Research Questions
- 1.4 Contributions
- 1.5 Paper Organization

## 2. Background and Related Work

- 2.1 Intrusion Detection Systems
  - 2.1.1 Signature-based Detection
  - 2.1.2 Anomaly-based Detection
  - 2.1.3 Hybrid Approaches
- 2.2 Machine Learning for Tabular Classification
  - 2.2.1 Bagging Ensembles
  - 2.2.2 Gradient Boosting
  - 2.2.3 Deep Tabular Architectures
- 2.3 Explainable AI in Security
  - 2.3.1 SHAP
  - 2.3.2 Attention-based Interpretability
- 2.4 The KDD Cup 1999 Benchmark
  - 2.4.1 Dataset Description
  - 2.4.2 Known Limitations
  - 2.4.3 Published Baselines

## 3. Dataset and Preprocessing

Sections 3.1 through 3.9, matching professor II.1 through II.3 in
expanded form.

## 4. Methodology

Sections 4.1 through 4.6, matching professor III in expanded form,
plus a formal notation subsection.

## 5. Experiments

- 5.1 Experimental Setup
- 5.2 Hardware and Runtime
- 5.3 Training Protocol
- 5.4 Reproducibility

## 6. Results

Expanded version of professor V.1 and VI.

## 7. Explainability Analysis

Expanded version of the SHAP and attention mask material from
professor VI.

## 8. Discussion

- 8.1 Key Findings
- 8.2 Comparison With Published Baselines
- 8.3 Limitations
- 8.4 Threats to Validity
- 8.5 Deployment Considerations

## 9. Conclusion and Future Work

## Acknowledgments

## References (APA)

## Appendices

- Appendix A — Full Hyperparameter Tables
- Appendix B — Additional Confusion Matrices
- Appendix C — Reproducibility Instructions

---

# Part 3 — Mapping Between the Two Formats

| Professor Section | Portfolio Section(s) |
|---|---|
| Cover Page | Title Page |
| — | Abstract, Keywords |
| I. Introduction | 1. Introduction |
| — | 2. Background and Related Work |
| II. Data Understanding and Preparation | 3. Dataset and Preprocessing |
| III. Machine Learning Model Development | 4. Methodology |
| IV. Model Metadata | 4.2 and Appendix A |
| V. Model Comparison and Evaluation | 6. Results, 8. Discussion |
| VI. Results and Visualizations | 6. Results, 7. Explainability Analysis |
| VII. Discovery Log | 5. Experiments, 8. Discussion |
| VIII. Executive Summary | Abstract |
| IX. Reflection | 8.4 Threats to Validity (partial) |
| X. References | References |

---

# Part 4 — Figure and Table Inventory

## Figures

| Figure | Source File | Appears In (Professor) | Appears In (Portfolio) |
|---|---|---|---|
| Figure 1 | `outputs/03_evaluation/confusion_matrix_rf.png` | VI | 6 |
| Figure 2 | `outputs/03_evaluation/confusion_matrix_xgb.png` | VI | 6 |
| Figure 3 | `outputs/03_evaluation/confusion_matrix_tabnet.png` | VI | 6 |
| Figure 4 | `outputs/03_evaluation/pr_curve_u2r.png` | VI | 6 |
| Figure 5 | `outputs/03_evaluation/pr_curve_r2l.png` | VI | 6 |
| Figure 6 | `outputs/03_evaluation/shap_summary_rf.png` | VI | 7 |
| Figure 7 | `outputs/03_evaluation/shap_summary_xgb.png` | VI | 7 |
| Figure 8 | `outputs/03_evaluation/shap_local_example.png` | VI | 7 |
| Figure 9 | `outputs/03_evaluation/tabnet_attention_mask.png` | VI | 7 |
| Figure 10 | `outputs/03_evaluation/model_comparison_visual.png` | VI | 6 |

## Tables

| Table | Source File | Appears In (Professor) | Appears In (Portfolio) |
|---|---|---|---|
| Table 1 | `outputs/02_training/model_comparison.csv` | V.1 | 6 |
| Table 2 | `outputs/03_evaluation/per_class_metrics.csv` | V.1 | 6 |
| Table 3 | `outputs/03_evaluation/per_class_metrics_normalized.csv` | V.1 | 6 |
| Table 4 | `outputs/03_evaluation/test_set_evaluation.json` | V.1, IV | 6 |
| Table 5 | `models/*.meta.json` | IV | 4.2, Appendix A |
| Table 6 | Feature description table | II.2 | 3 |
| Table 7 | Hyperparameter search spaces | III.1.2, III.2.2, III.3.2 | 4.3, Appendix A |

---

# Part 5 — Ownership and Change Control

| Section | Primary Author |
|---|---|
| Cover Page | Kit |
| I. Introduction | Markie |
| II.1 Data Understanding | Markie, from Kit's Phase 2 report |
| II.2 Feature Description | Markie, from Kit's Phase 2 report |
| II.3 Data Preparation | Markie, from Kit's Phase 2 report |
| III.1 Random Forest | Amber writes draft; Markie edits |
| III.2 XGBoost | Kit writes draft; Markie edits |
| III.3 TabNet | Kit writes draft; Markie edits |
| IV. Model Metadata | Kit, from meta sidecars |
| V.1 Comparative Results | Dwayne writes draft; Markie edits |
| V.2 Error Analysis | Dwayne writes draft; Markie edits |
| V.3 Overfitting Analysis | Kit writes draft; Markie edits |
| V.4 Model Recommendation | Markie |
| VI. Results and Visualizations | Dwayne produces figures; Markie writes text |
| VII. Discovery Log | Kit, from Phase reports |
| VIII. Executive Summary | Markie |
| IX. Reflection | Each member writes their own |
| X. References | Markie |
| Portfolio expansion | Markie |

Change control: any change to section structure requires a PR that
modifies this file and Kit's approval.

---

# Part 6 — Formatting Conventions

## Professor Format

- Font: 11-point serif (Times New Roman or equivalent)
- Spacing: 1.5 line spacing
- Margins: 1 inch on all sides
- Page numbers: bottom center
- Section headings: Roman numerals at top level, Arabic decimals
  for subsections. Bold and larger font for top-level headings.
- Figure captions: below the figure, numbered sequentially as
  "Figure 1.", "Figure 2.", etc.
- Table captions: above the table, numbered sequentially as
  "Table 1.", "Table 2.", etc.
- Citations: in-text APA style, e.g., (Author, Year) or Author (Year)

## Portfolio Format

- Font: 11-point serif
- Single column
- 1.15 line spacing
- Section numbering: Arabic decimals
- Figure and table captions match the professor format
- References: APA
- Length: dictated by content, typically 20 to 30 pages for a project
  of this scope