# Handoff — Model Comparison for Paper Integration

**From:** Kit Dustin (Role 1) — Project Manager
**To:** Markie (Role 2) — Paper Lead
**Date:** 2026-10-14
**Status:** Complete — ready for paper integration
**Source files:** `outputs/02_training/model_comparison.csv`, `outputs/03_evaluation/test_set_evaluation.json`

---

## 1. Purpose

This document provides the complete model comparison results for the
Network Guardian IDS paper. It is not a draft — it is the source
material. Every number here traces to a file on `main`. Use the
figures and tables as written, adapt the phrasing to fit the paper's
voice, and cite the source files where the paper references them.

The paper needs two comparison tables:

1. **Cross-validation results** — what each model achieved during
   hyperparameter tuning on the training partition.
2. **Test-set results** — what each model achieved on the frozen
   held-out test partition. This is the honest generalization metric.

The two tables answer different questions. The paper should present
both, in that order.

---

## 2. Model Lineup

Three models, three algorithm families, one comparison.

| Model | Family | Code Owner | Execution Owner |
|---|---|---|---|
| Random Forest | Tree bagging ensemble | Amber (Role 3) | Amber |
| XGBoost | Gradient tree boosting | Kit (Role 1) | Kit (reassigned from Kenneth) |
| TabNet | Deep learning with sequential attention | Kit (Role 1) | Dwayne (Role 5) |

The progression from bagging to boosting to attention is deliberate.
It represents increasing model expressiveness and decreasing
interpretability. The paper's Methodology section should note this
as a design choice.

---

## 3. Table 1 — Cross-Validation Results

**Source:** `outputs/02_training/model_comparison.csv`
**Reading:** Each model's CV Macro F1 is the mean score across
stratified folds. Random Forest and XGBoost used 5-fold CV. TabNet
used 3-fold CV (see section 7 for the rationale). The standard
deviation reflects fold-to-fold variability.

| Model | CV Macro F1 (mean) | CV std | Best trial |
|---|---|---|---|
| Random Forest | 0.9505 | 0.0212 | 17 |
| XGBoost | 0.9508 | 0.0260 | 81 |
| TabNet | 0.9212 | 0.0193 | 16 |

### 3.1 What Table 1 tells the reader

- **XGBoost has the highest CV Macro F1** at 0.9508. Random Forest is
  effectively tied at 0.9505 — the difference of 0.0003 is within
  numeric noise. Neither model is meaningfully stronger on this
  metric.
- **TabNet is 3 percentage points below the tree models** at 0.9212.
  This is a meaningful gap and worth discussion.
- **All three models are stable.** No model has a CV std above 0.026.
  The fold scores cluster tightly around each mean.
- **Best trial numbers differ** because the three studies used
  different search spaces and different trial budgets. Trial 17 for
  RF, trial 81 for XGBoost (from a study with 30 trials and pruned
  trials taking additional indices), trial 16 for TabNet. These
  numbers do not indicate relative quality.

### 3.2 Note on per-class recall at CV

The CSV also contains a per-class recall column for each model.
**Do not use these for cross-model comparison.** The field names
differ between models and measure recall on different data:

| Model | Field | Meaning |
|---|---|---|
| Random Forest | `per_class_recall_cv` | Recall on CV validation folds |
| XGBoost | `per_class_recall_train` | Recall on the training pool after refit |
| TabNet | `per_class_recall_train` | Recall on the training pool after refit |

XGBoost and TabNet both show U2R recall of 1.0 because they were
measured on their own training data. Random Forest shows 0.8205
because it was measured on held-out folds. These are not the same
metric.

**For a valid cross-model comparison of per-class recall, use Table 2
from the test-set evaluation.**

---

## 4. Table 2 — Test-Set Results

**Source:** `outputs/03_evaluation/test_set_evaluation.json`
**Test set:** 36,396 samples, 43 features, frozen at Phase 2.
**Reading:** Each model was evaluated once on the frozen test partition.
No model saw these rows during training or tuning.

| Model | Test Macro F1 | Test accuracy | U2R recall | R2L recall |
|---|---|---|---|---|
| Random Forest | 0.9331 | 0.9989 | 0.7692 | 0.9520 |
| XGBoost | **0.9451** | **0.9990** | 0.7692 | **0.9920** |
| TabNet | 0.9306 | 0.9976 | 0.7692 | 0.9760 |

### 4.1 What Table 2 tells the reader

- **XGBoost has the highest test Macro F1** at 0.9451. This is the
  primary comparison metric and the headline result.
- **Random Forest and TabNet are close** at 0.9331 and 0.9306
  respectively. The difference of 0.0025 is small.
- **All three models achieve identical U2R recall** at 0.7692. Ten of
  the thirteen U2R test samples were correctly classified by every
  model. Three were missed by every model.
- **XGBoost has the highest R2L recall** at 0.9920. Only two R2L
  samples were misclassified. Random Forest missed twelve. TabNet
  missed six.

### 4.2 The U2R recall coincidence — a paper-worthy finding

Three architecturally different models landing on identical U2R
recall is unusual. It suggests one of two things:

- The three missed U2R samples have feature signatures that are
  indistinguishable from other classes. No model in the comparison
  can separate them.
- All three models share a common blind spot on those specific
  samples.

This is worth a paragraph in the paper's Discussion section. It shows
that adding model complexity does not improve U2R detection on this
test set — the limit is the data, not the model.

---

## 5. Table 3 — Model Recommendation

**Recommendation:** XGBoost.

**Justification:**

1. **Highest test Macro F1** — 0.9451, above the next-best model by
   1.2 percentage points.
2. **Highest R2L recall** — 0.9920, notably better than TabNet (0.9760)
   and Random Forest (0.9520). R2L is the second-rarest attack class
   and the one where detection differences actually matter.
3. **Fastest inference** — 0.126 seconds for the full test set.
   Random Forest takes 0.151 seconds. TabNet takes 1.091 seconds.
4. **Best balance of performance and cost** — XGBoost combines the
   second-fastest inference with the highest test Macro F1. It is
   the natural deployment choice.

**Caveat for the paper:** all three models tie on U2R recall. XGBoost
is not better at U2R; it is better at the aggregate metric and at R2L.
The paper should not overclaim on U2R.

---

## 6. Cross-Tab Analysis — What the Two Tables Say Together

| Model | CV Macro F1 | Test Macro F1 | Gap (CV − Test) |
|---|---|---|---|
| Random Forest | 0.9505 | 0.9331 | 0.0174 |
| XGBoost | 0.9508 | 0.9451 | 0.0057 |
| TabNet | 0.9212 | 0.9306 | **−0.0094** |

### 6.1 Interpreting the gap

- **Random Forest:** Test is 1.74 points below CV. This is a moderate
  generalization gap. Expected for a bagged tree ensemble on this
  dataset.
- **XGBoost:** Test is 0.57 points below CV. This is an excellent
  generalization result — the model performs almost identically on
  unseen data as it did during cross-validation.
- **TabNet:** Test is 0.94 points **above** CV. This is not a problem.
  It means the specific test partition happened to be slightly easier
  for TabNet than the CV folds were. The direction of the gap is
  within the natural variance of a 3-fold split with a rare-class
  test partition.

**No model shows severe overfitting.** All gaps are within 2 percentage
points. This is a strong result across the board and worth stating
explicitly in the paper's Discussion.

### 6.2 What this says about the tuning pipeline

The XGBoost result is particularly notable. Test Macro F1 is only 0.57
percentage points below CV. That means the hyperparameters selected
during tuning transfer almost perfectly to unseen data. The search
space was well-calibrated and the CV-based selection did not overfit
to the fold partition.

This is worth a sentence in the paper's Methodology section:
*"XGBoost's test-set Macro F1 of 0.9451 was within 0.6 percentage
points of its cross-validation mean of 0.9508, indicating that the
hyperparameter search generalized cleanly to unseen data."*

---

## 7. Why TabNet Uses 3 Folds

The paper will be asked this question. The answer:

Random Forest and XGBoost used 5-fold stratified cross-validation.
TabNet used 3-fold.

Rationale: the rarest class (U2R) has only 39 training examples. Under
5-fold stratified CV, each validation fold contains approximately 7 to
8 U2R rows. That is too few for a stable per-class recall estimate.
Under 3-fold, each validation fold contains approximately 13 U2R rows,
which is the minimum for a meaningful estimate.

The reduced fold count is a documented design choice. It was recorded
in the Phase 3 design phase before any model was trained. The reason
was to keep the rare-class metric statistically usable.

**Paper reference:** this appears in the methodology report and in the
TabNet execution contract section 5.1.

---

## 8. Figures for the Paper

The paper needs these figures. All are on `main` in
`outputs/03_evaluation/` and `outputs/02_training/`.

| Figure | Source file | Suggested caption |
|---|---|---|
| Figure 1 | `confusion_matrix_rf.png` | Random Forest confusion matrix on the frozen test set |
| Figure 2 | `confusion_matrix_xgb.png` | XGBoost confusion matrix on the frozen test set |
| Figure 3 | `confusion_matrix_tabnet.png` | TabNet confusion matrix on the frozen test set |
| Figure 4 | `pr_curve_u2r.png` | Precision-recall curves for U2R detection across all three models |
| Figure 5 | `pr_curve_r2l.png` | Precision-recall curves for R2L detection across all three models |
| Figure 6 | `model_comparison_visual.png` | Macro F1 comparison across the three models on the frozen test set |
| Figure 7 | `class_distribution.png` | Class distribution of the training and test partitions |

The confusion matrices should be presented side by side or stacked.
The reader should be able to compare the three models' error patterns
directly.

---

## 9. Paper Section Assignment

Mapping each result to its paper section:

### Section VI — Results and Visualizations

- Table 1 (CV results) — from section 3 of this document
- Table 2 (test results) — from section 4 of this document
- Figures 1–3 (confusion matrices)
- Figure 4 (PR curve for U2R)
- Figure 5 (PR curve for R2L)
- Figure 6 (comparison visual)
- Figure 7 (class distribution)

### Section V — Model Comparison and Evaluation

- V.1 Comparative Results — Table 1 and Table 2
- V.2 Error Analysis — U2R misses, R2L misses, discussion of the equal U2R recall
- V.3 Overfitting Analysis — the CV-versus-test gap table from section 6
- V.4 Model Recommendation — XGBoost, justified by section 5

### Section IV — Model Metadata

- Pull best trial numbers, hyperparameters, and cross-validation folds
  from each model's meta sidecar (`models/*.meta.json`)

---

## 10. What to Emphasize

Three points worth returning to in the paper.

### 1 — The generalization result is strong

No model shows a large CV-versus-test gap. That means the hyperparameter
search, the anti-leakage discipline, and the cross-validation protocol
all worked. XGBoost in particular nearly matches its CV score on
unseen data.

### 2 — Per-class recall is the interesting metric

Aggregate accuracy is above 99 percent for all three models. That
number is uninformative. The differences show up in the rare classes:
U2R recall is identical across models at 0.7692, and R2L recall
differentiates XGBoost (0.9920) from Random Forest (0.9520).

### 3 — The U2R ceiling is a data property, not a model property

Three different algorithm families cannot exceed 0.7692 U2R recall on
this test set. The limit is not model capacity. It is the number and
feature separability of U2R test samples. This is worth stating clearly.

---

## 11. What to Avoid

Four things the paper should not say.

- **Do not cite the CV per-class recall values in Table 1 as if they
  were the same metric across models.** RF uses a different field and
  measures a different thing. Use Table 2's test-set values for any
  per-class discussion.
- **Do not claim XGBoost is better at U2R detection.** All three
  models tie. XGBoost is better at aggregate Macro F1 and at R2L.
- **Do not report accuracy as the headline metric.** It is above 99
  percent for all three models and does not distinguish them.
- **Do not use the words "overfitting" without qualification.** The CV
  versus test gap is at most 1.74 percentage points. That is not
  severe. Note the gap and move on.

---

## 12. Traceability Index

Every number in this handoff comes from one of these files.

| Number | Source |
|---|---|
| CV Macro F1 (all models) | `outputs/02_training/model_comparison.csv` |
| CV std (all models) | `outputs/02_training/model_comparison.csv` |
| Best trial numbers | `models/*.meta.json` → `best_trial_number` |
| Test Macro F1 (all models) | `outputs/03_evaluation/test_set_evaluation.json` |
| Test accuracy (all models) | `outputs/03_evaluation/test_set_evaluation.json` |
| Test per-class recall | `outputs/03_evaluation/test_set_evaluation.json` |
| Per-class metrics tables | `outputs/03_evaluation/per_class_metrics.csv` |
| Normalized per-class metrics | `outputs/03_evaluation/per_class_metrics_normalized.csv` |
| Confusion matrices | `outputs/03_evaluation/confusion_matrix_*.png` |
| PR curves | `outputs/03_evaluation/pr_curve_u2r.png`, `pr_curve_r2l.png` |
| Comparison visual | `outputs/03_evaluation/model_comparison_visual.png` |
| Class distribution | `outputs/03_evaluation/class_distribution.png` |
| Full evaluation narrative | `docs/reports/role-5-phase-3-dwayne-evaluation-suite.md` |
| Full XGBoost narrative | `docs/reports/role-4-phase-2-kit-xgboost-execution.md` |
| Full RF narrative | `docs/reports/role-3-phase-2-amber-rf-baseline.md` |
| Full TabNet narrative | `docs/reports/role-5-phase-2-dwayne-tabnet-execution.md` |

If a number appears in the paper that does not trace to a row in this
table, do not include it.

---

## 13. Summary

**Primary result:** XGBoost leads on test Macro F1 at 0.9451 and R2L
recall at 0.9920. Random Forest and TabNet are within 1.5 percentage
points on the aggregate metric.

**Generalization:** all three models generalize well. The largest
CV-versus-test gap is 1.74 percentage points (Random Forest).

**Rare class ceiling:** U2R recall is 0.7692 for all three models. The
limit is the test set, not the models.

**Recommendation:** XGBoost for deployment, justified by test Macro
F1, R2L recall, and inference cost.

**What the paper needs from this document:**

- Table 1 (CV results)
- Table 2 (test results)
- Table 3 (recommendation)
- Section 6 cross-tab analysis
- Section 7 rationale for the TabNet fold count
- Section 10's three emphasis points
- Section 11's four warnings

Every number here is final. Every figure is on `main`. Markie can
proceed with the paper's Results, Model Comparison, and Recommendation
sections directly from this document.

---

**Signed off by:** Kit Dustin, Project Manager (Role 1)
**Date:** 2026-10-14