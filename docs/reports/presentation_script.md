# Video Presentation Script and Structure

**Status:** Phase 1 outline and rehearsal draft; results and live demo pending.
**Outline maintainer:** Markie (Role 2).
**Production and editing owner:** Kenneth (Role 4).
**Target runtime:** 7 minutes, within the required 5-8 minutes.
**Recording rule:** Every member must be visible on camera and speak.

## 1. Timing and ownership

| Time | Speaker | Segment | Evidence / visual |
|---|---|---|---|
| 0:00-1:15 | Kit Dustin | Problem, data, preparation | Title; `outputs/01_eda/family_distribution.png`; `outputs/01_eda/correlation_heatmap.png` |
| 1:15-2:30 | Amber | Random Forest and SOC dashboard | RF contract; pending RF metrics; prepared dashboard demonstration |
| 2:30-3:40 | Kenneth | XGBoost execution and runtime tradeoffs | XGBoost execution report and metadata, pending |
| 3:40-5:10 | Dwayne | TabNet, evaluation, explainability | Confusion matrices, per-class metrics, SHAP and attention masks, pending |
| 5:10-6:40 | Markie | Paper walkthrough and backend | Paper section map; summary; API contract; backend demo after Phase 2 |
| 6:40-7:00 | Kit Dustin | Conclusion and handoff | Verified recommendation and limitations slide, pending |

Each window includes transitions. Rehearse the actual spoken script with screen changes; the timing table is a budget, not a measured recording duration. Shorten repeated model definitions before cutting rare-class error analysis.

## 2. Rehearsal script

### Kit Dustin: problem and data preparation

“Network Guardian IDS compares three machine learning approaches for classifying network connections. Our five categories are normal traffic, denial of service, probing, remote-to-local access, and user-to-root escalation. We focus on missed attacks and false alarms because overall accuracy can hide poor detection of rare classes.

Our data-preparation report documents duplicated connections, skewed byte and duration values, and limited rare-class examples. The preparation pipeline removes duplicates and redundant features, transforms skewed values, and encodes categorical inputs. Encoders and scalers use the training partition; validation folds are kept separate from resampling. The paper will state the exact verified counts and split configuration. This historical benchmark supports an academic comparison, but it does not establish performance on modern production networks. Amber will introduce our baseline and dashboard.”

**Before recording:** Reconcile dataset counts with frozen manifests; identify exactly which distribution each EDA figure displays. Sources: Kit's Phase 2 report, sections 5-10; `docs/reports/paper_narrative_context.md`.

### Amber: Random Forest and dashboard

“Random Forest is our bagging baseline. It combines decision trees trained with randomness in their data and feature selection. We compare it with boosting and attention-based learning under the project's fixed training protocol.

[Insert verified RF cross-validation Macro F1 and a rare-class tradeoff, with the source artifact visible.] The dashboard accepts connection statistics and categorical fields such as protocol, service, and flag. During the demonstration I will submit one prepared example and show the predicted family and confidence. Confidence should not be interpreted as proof that a connection is safe. We will explain an incorrect prediction as well as a correct one if the evaluation provides suitable examples. Kenneth will describe the boosting run.”

**Before recording:** Use `docs/contracts/role-3-rf-architecture-spec.md`, RF metadata, and `outputs/03_evaluation/confusion_matrix_rf.png`. Run the dashboard demonstration only after frontend-backend integration; keep an approved recording available if needed.

### Kenneth: XGBoost execution

“XGBoost builds a sequence of trees that improves the model's predictions. Its tuning process searches the bounded parameter space in our execution contract and uses cross-validation Macro F1 as the objective. Early stopping during validation and resampling only within training folds help control overfitting and leakage.

[Insert completed trial count, measured elapsed time, hardware, and cross-validation result.] These are measured results from our execution report, not estimated training budgets. We preserve the selected configuration and metadata so the run can be traced. Any execution failure and recovery is recorded in the Discovery Log. Dwayne will explain TabNet and evaluate all three models.”

**Before recording:** Source values from `docs/reports/role-4-phase-2-kenneth-xgboost-execution.md` and `models/xgb_optuna.meta.json`; distinguish training time from prediction time.

### Dwayne: TabNet, evaluation, and explainability

“TabNet adds an attention-based neural network to the comparison. It selects features at successive decision steps. We use three validation folds for TabNet and five for the tree models, and disclose that difference rather than treating the validation estimates as identical experiments.

[Show the verified comparison and state Macro F1 for each model.] We also examine precision, recall, and F1 for each class. A false negative is an attack classified incorrectly as safe; a false positive is normal traffic flagged as an attack. The U2R and R2L results matter even when overall accuracy looks strong.

[Use a confusion matrix to explain one observed error and give its count.] [Show one sourced SHAP example and one TabNet attention mask.] These plots describe how models use features; they do not prove the cause of an intrusion. Our held-out test results are reported separately from tuning. Markie will connect this evidence to the paper and backend.”

**Before recording:** Use `outputs/03_evaluation/per_class_metrics.csv`, `test_set_evaluation.json`, `confusion_matrix_*.png`, `shap_local_example.png`, and `tabnet_attention_mask.png`. State actual plotted classes and values. Evaluation and figure production belong to Dwayne.

### Markie: paper walkthrough and backend

“Our paper follows the professor's required structure. It begins with the problem and data preparation, then explains the three models and their metadata. The comparison, error analysis, and visualizations connect the results to the security question. The Discovery Log records actual mistakes and corrections, while the Executive Summary answers six questions in plain language. Each member provides an individual reflection, and the references disclose external sources and AI assistance.

The backend interface connects the dashboard to Python inference. The planned route receives telemetry, validates it against our API contract, and passes it to a Python bridge. The bridge must reconstruct the model's feature order using the frozen preprocessing artifacts before returning a prediction.

[After Phase 2, demonstrate one validated request and its actual response.] [Insert the evidence-backed recommendation and its limitation.] At this stage, the documentation scaffold is complete; backend implementation and final results are separate deliverables.”

**Before recording:** Replace the final status sentence with the actual completion state. Use `docs/contracts/api_data_contract.md`, `docs/reports/paper.md` after integration, and the completed Role 2 Phase 2 report. Do not describe the planned bridge as implemented before it is verified.

### Kit Dustin: conclusion

“[State the selected model and the measured tradeoff supporting it.] The main lesson is to compare class-level detection, runtime, and explanations using traceable evidence. Future work should validate on newer traffic and test inference cost before deployment. Thank you.”

**Before recording:** The conclusion must agree with paper Section V.4 and the Executive Summary.

## 3. Asset readiness checklist

- [ ] All speakers reviewed their facts and practiced transitions.
- [ ] Final paper and Executive Summary agree on the recommendation.
- [ ] Every metric matches a delivered evaluation or metadata artifact.
- [ ] Every displayed figure has a readable label and source caption.
- [ ] Dashboard, server, and inference artifacts support the recorded demo.
- [ ] No pending bracketed script instructions remain in the final recording.
- [ ] All five members are visible on camera and speak.
- [ ] Final exported video duration is measured and lies within 5-8 minutes.
- [ ] Kenneth checks audio, readable visuals, captions, and final edit.

## 4. Sources and disclosure

Working sources: `docs/tasks/role_2.md`, `docs/tasks/role_3.md`, `docs/tasks/role_4.md`, `docs/tasks/role_5.md`, `docs/reports/paper_structure.md`, and `docs/reports/paper_narrative_context.md`. The user-supplied Team Coordination briefing assigns the video segments consistently with the role mandates. Instructions about channel posts in that briefing are coordination context; this outline does not send messages.

Codex assisted with this Phase 1 outline. The team must check the final wording, measurements, and demonstration before recording and disclose AI assistance in paper Section X.
