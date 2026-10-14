# Role 2 Paper Integration Report: Final Manuscripts and Evidence

**Owner:** Markie
**Updated:** 2026-10-14
**Status:** Final Professor and Portfolio manuscripts prepared; awaiting Kit review before submission.
**Branch:** `feature/role-2-paper-results`
**Paper baseline:** main commit `e250700` (includes merged Phase 4 and UI integration).
**Explainability source:** Dwayne's PR #22, merged to main; source commit `7108f414c049ca265bdd6b305e979abcd7a5c614`.

## Deliverables

| Format | Manuscript text | Editable Word manuscript | Pages |
|---|---|---|---:|
| Professor, primary graded deliverable | `docs/reports/paper.md` | `docs/reports/paper-final.docx` | 39 |
| Portfolio, supplemental academic deliverable | `docs/reports/paper-portfolio.md` | `docs/reports/paper-portfolio-final.docx` | 33 |

The papers use Times New Roman 11 pt, one-inch margins, page numbers, and paragraph indents. The Professor version uses 1.5 line spacing; Portfolio is one column with 1.15 spacing. The Professor Executive Summary is a one-page, six-question section. The Portfolio abstract is exactly 250 words. The editable Word and Markdown versions were synchronized from the same manuscript content.

## Integrated evidence

Both manuscripts distinguish validation objectives from the frozen test results, report precision and recall with class support, discuss the error counts, compare CV and test Macro F1, report measured batch prediction time, and qualify the benchmark recommendation. They include seven evaluation figures and four Phase 4 explanation figures: RF and XGBoost SHAP summaries, one selected local XGBoost U2R case, and TabNet attention averaged across decision steps and 1,000 sampled test rows.

The explainability artifacts and report are merged to main through PR #22. Both papers cite source commit `7108f414c049ca265bdd6b305e979abcd7a5c614`. The open PR #24 adds Role 5 Phase 5 draft material and a handoff to the paper lead; its cautions about verifying feature claims and row-level U2R misses were followed. The handoff itself does not replace the saved source artifacts. The local success example is not evidence about the three missed U2R cases. No causal claims or new model runs are made.

Held-out test Macro F1 is RF 0.933095, XGBoost 0.945134, and TabNet 0.930622. XGBoost is the preferred candidate for this benchmark based on Macro F1, R2L recall 0.992000, and the shortest recorded full-test batch time of 0.126 seconds. RF has fewer normal false alarms. All models correctly identify 10 of 13 U2R cases and miss the same three. The papers do not claim statistical superiority or production readiness.

## Reporting qualifications

1. RF independently records fold SD 0.021178. Its acceptance threshold changed from 0.02 to 0.025 after the run; the papers disclose the post-run adjustment.
2. XGBoost and TabNet metadata SD values 0.025954 and 0.019250 are `_safe_cv_std` dispersion across non-null recorded trial values, including pruned trials. They are not best-trial fold SDs.
3. XGBoost and TabNet fold CSVs export cumulative fold means, not independent fold scores. Their cumulative values must not be used to estimate fold variability.
4. The XGBoost log has 90 records (78 complete, 12 pruned); 30 is its configured per-invocation budget. RF has 20 complete records; TabNet has 15 complete and five pruned.
5. CV-minus-test gaps are labeled explicitly. They are not training-minus-test or training-minus-validation gaps. The separate TabNet in-sample score is attributed to its verification report; comparable RF/XGBoost full-training Macro F1 remains unavailable.
6. Equal U2R recall does not prove an intrinsic ceiling. The models miss the same three rows, but XGBoost labels one R2L and the other two normal, while RF and TabNet label all three normal. Attack-family misses and attacks labeled normal are reported separately.
7. The normalized-metrics CSV schema remains provisional; the papers use standard per-class metrics. Backend readiness is separate from offline evaluation: merged PR #23 aligns the TabNet bridge and contract to its raw training inputs; a real TabNet artifact request and receiving-device XGBoost verification remain open. The merged dashboard panels now use exported evaluation data, while the analyze form and threat gauge remain live API surfaces.

## Verification

All 36,396 exported prediction rows reproduce the JSON per-class F1, Macro F1, and accuracy. The weighted F1 values match the report. Trial-log calculations reproduce the XGBoost and TabNet metadata SD fields. Reconstructed attack-as-normal counts are RF 22, XGBoost 10, TabNet 16; normal-as-attack counts are RF 13, XGBoost 21, TabNet 68. These are audits of supplied outputs, not fresh model evaluations.

The two Word files passed checks for 11-point Times New Roman body text, one-inch margins, bottom-center page numbers, paragraph indents, heading structure, the 41-feature dictionary, required tables, abstract length, and 11 figures each. The Professor paper contains five 400–700-word reflections based on role records, with the XGBoost reassignment attributed accurately; the AI disclosure identifies these as AI-assisted drafts for author validation. Microsoft Word PDF export produced 39 Professor pages and 33 Portfolio pages; every rendered page was visually reviewed. Relative figure links in Markdown point to files in `outputs/03_evaluation/`.

## Remaining work

Kit’s final review is required before submission. AI-assisted individual reflections are evidence-based drafts and should be checked by each named author for personal accuracy. Reported study limitations remain: comparable full-training metrics, independent fold reporting for XGBoost and TabNet, complete runtime provenance, normalized-metrics schema confirmation, and receiving-device inference verification for XGBoost and TabNet. Dwayne’s open PR #24 still labels its handoff material as pending final figure and metric verification; this manuscript independently verifies the published test metrics and row-level U2R misses against the committed artifacts.

## Sources

`outputs/03_evaluation/test_set_evaluation.json`, `per_class_metrics.csv`, `test_predictions.csv`, supplied evaluation PNGs and four Phase 4 PNGs; `models/*.meta.json`; `outputs/02_training/optuna_*_trials.csv`; `src/models.py`; `docs/reports/role-5-phase-3-dwayne-evaluation-suite.md`; `docs/reports/role-4-phase-2-kit-xgboost-execution.md`; `docs/reports/role-5-phase-4-dwayne-explainability.md` from snapshot `7108f414c049ca265bdd6b305e979abcd7a5c614`; `docs/handoffs/model_comparison.md`; `docs/handoffs/xgboost.md`; the RF acceptance decision record, the updated `docs/contracts/api_data_contract.md`, merged `docs/handoffs/ui_phase_handoff.md`, and Dwayne's open PR #24 Phase 5 handoff.
