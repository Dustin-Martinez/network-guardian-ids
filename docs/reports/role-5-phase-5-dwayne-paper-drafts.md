# Role 5 — Phase 5 Paper Drafts and Handoff

## 1. Objective

Prepare draft material for the Network Guardian intrusion detection research paper, using the completed evaluation and explainability artifacts from Phases 3 and 4. The intended handoff is to Markie for review, editing, and integration into the main paper.

## 2. Deliverables Prepared

### 2.1 Comparative Results and Error Analysis

**Draft:** `docs/reports/role-5-phase-5-dwayne-results-draft.md`

The draft covers the three-model comparison, test-set Macro F1, class imbalance, confusion-matrix interpretation, per-class metrics, precision–recall analysis for U2R and R2L, and limitations of the held-out evaluation.

Recorded Macro F1 values included in the draft:

- XGBoost: 0.9451
- Random Forest: 0.9331
- TabNet: 0.9306

The draft prioritizes Macro F1 rather than accuracy and emphasizes the need to assess rare-class performance separately from aggregate results.

### 2.2 Explainability Analysis

**Draft:** `docs/reports/role-5-phase-5-dwayne-explainability-draft.md`

The draft describes global SHAP summaries for Random Forest and XGBoost, the local SHAP waterfall for the selected U2R example, and the TabNet attention-mask visualization. It explains the distinction between SHAP feature contributions and TabNet's internal attention mechanism.

The selected local example is test-set row 29,522, identified as a correctly predicted U2R example using the existing Phase 3 prediction and confidence outputs.

### 2.3 Sprint Report

**File:** `docs/reports/role-5-phase-5-dwayne-paper-drafts.md`

This report records the scope of the drafting work, source artifacts, limitations, and handoff requirements.

## 3. Source Artifacts

The drafts reference the following project artifacts:

- `outputs/03_evaluation/test_set_evaluation.json`
- `outputs/03_evaluation/per_class_metrics.csv`
- `outputs/03_evaluation/per_class_metrics_normalized.csv`
- `outputs/03_evaluation/confusion_matrix_rf.png`
- `outputs/03_evaluation/confusion_matrix_xgb.png`
- `outputs/03_evaluation/confusion_matrix_tabnet.png`
- `outputs/03_evaluation/pr_curve_u2r.png`
- `outputs/03_evaluation/pr_curve_r2l.png`
- `outputs/03_evaluation/model_comparison_visual.png`
- `outputs/03_evaluation/shap_summary_rf.png`
- `outputs/03_evaluation/shap_summary_xgb.png`
- `outputs/03_evaluation/shap_local_example.png`
- `outputs/03_evaluation/tabnet_attention_mask.png`

The paper's organization and figure inventory are governed by `docs/reports/paper_structure.md`, while the interpretation and evidence requirements are guided by `docs/reports/paper_narrative_context.md`.

## 4. Interpretation and Reporting Standards

The drafts use Macro F1 as the primary aggregate comparison metric because the dataset is imbalanced. They distinguish overall model performance from per-class performance and highlight the small number of U2R test examples as a limitation.

The explainability draft treats SHAP contributions and TabNet attention as complementary but distinct forms of model interpretation. It does not claim that feature attribution establishes causation or guarantees generalization.

Every proposed figure caption references the corresponding source file, consistent with the paper structure requirements.

## 5. Remaining Validation Before Final Handoff

Before these drafts are merged into the main paper:

1. Verify the recorded Macro F1 values against the committed evaluation JSON and comparison figure.
2. Confirm the exact per-class precision, recall, and F1 values against the committed CSV.
3. Inspect the SHAP and TabNet figures and add the actual leading feature names and contribution directions where relevant.
4. Ensure figure numbering matches the final paper, since the numbering in the project inventory and draft captions may differ.
5. Have Markie review the drafts for consistency with the rest of the manuscript and remove duplicated discussion.

## 6. Handoff

The intended handoff is to Markie for review and integration into the paper's Results and Explainability Analysis sections. The drafts provide the structure and evidence references needed for integration; final publication-ready claims should be confirmed against the saved source artifacts.

## 7. Status

The initial paper drafts and sprint report have been prepared. Final validation of feature-level explainability findings and exact per-class results remains necessary before the material should be treated as publication-ready.