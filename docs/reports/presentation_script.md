# Video Presentation Script and Structure

**Status:** Results integrated into the rehearsal draft; live demo and recording pending.
**Outline maintainer:** Markie (Role 2).
**Production and editing owner:** Kenneth (Role 4).
**Target runtime:** 7 minutes, within the required 5-8 minutes.
**Recording rule:** Every member must be visible on camera and speak.

## 1. Timing and ownership

| Time | Speaker | Segment | Evidence / visual |
|---|---|---|---|
| 0:00-1:15 | Kit Dustin | Problem, data, preparation | Title; `outputs/01_eda/family_distribution.png`; `outputs/01_eda/correlation_heatmap.png` |
| 1:15-2:30 | Amber | Random Forest and SOC dashboard | RF test metrics and confusion matrix; prepared dashboard demonstration |
| 2:30-3:40 | Kenneth | XGBoost execution and runtime tradeoffs | XGBoost execution report and metadata |
| 3:40-5:10 | Dwayne | TabNet, evaluation, explainability | Confusion matrices, per-class metrics, sampled SHAP and attention figures |
| 5:10-6:40 | Markie | Paper walkthrough and backend | Paper section map; final summary; API contract; verified backend demonstration |
| 6:40-7:00 | Kit Dustin | Conclusion and handoff | Verified recommendation and limitations slide |

Each window includes transitions. Rehearse the actual spoken script with screen changes; the timing table is a budget, not a measured recording duration. Shorten repeated model definitions before cutting rare-class error analysis.

## 2. Rehearsal script

### Kit Dustin: problem and data preparation

“Network Guardian IDS compares three machine learning approaches for classifying network connections. Our five categories are normal traffic, denial of service, probing, remote-to-local access, and user-to-root escalation. We focus on missed attacks and false alarms because overall accuracy can hide poor detection of rare classes.

Our data-preparation report documents duplicated connections, skewed byte and duration values, and limited rare-class examples. The preparation pipeline removes duplicates and redundant features, transforms skewed values, and encodes categorical inputs. Encoders and scalers use the training partition; validation folds are kept separate from resampling. The paper reports 494,021 supplied rows, 145,584 retained records, and a frozen split of 109,188 training and 36,396 test rows. This historical benchmark supports an academic comparison but does not establish performance on modern production networks. Amber will introduce our baseline and dashboard.”

**Before recording:** Reconcile dataset counts with frozen manifests; identify exactly which distribution each EDA figure displays. Sources: Kit's Phase 2 report, sections 5-10; `docs/reports/paper_narrative_context.md`.

### Amber: Random Forest and dashboard

“Random Forest is our bagging baseline. It combines decision trees trained with randomness in their data and feature selection. We compare it with boosting and attention-based learning under the project's fixed training protocol.

RF test Macro F1 was 0.933095. Its U2R recall was 0.769231 and R2L recall was 0.952000. Show the confusion matrix and point out that RF produced fewer normal-as-attack errors than the other models. The dashboard accepts connection statistics and categorical fields such as protocol, service, and flag. During the demonstration I will submit one prepared example and show the predicted family and confidence. Confidence should not be interpreted as proof that a connection is safe. We will explain an incorrect prediction as well as a correct one if the evaluation provides suitable examples. Kenneth will describe the boosting run.”

**Before recording:** Use `docs/contracts/role-3-rf-architecture-spec.md`, RF metadata, and `outputs/03_evaluation/confusion_matrix_rf.png`. Run the dashboard demonstration only after frontend-backend integration; keep an approved recording available if needed.

### Kenneth: XGBoost execution

“XGBoost builds a sequence of trees that improves the model's predictions. Its tuning process searches the bounded parameter space in our execution contract and uses cross-validation Macro F1 as the objective. Early stopping during validation and resampling only within training folds help control overfitting and leakage.

The saved search contains 90 records, 78 complete and 12 pruned, while 30 was the configured budget per invocation. Trial 81 had validation Macro F1 of 0.950842. Reported training time was about 1 hour 55 minutes; use the execution report for hardware details. These are measured results from our execution report, not estimated training budgets. We preserve the selected configuration and metadata so the run can be traced. Any execution failure and recovery is recorded in the Discovery Log. Dwayne will explain TabNet and evaluate all three models.”

**Before recording:** Source values from `docs/reports/role-4-phase-2-kenneth-xgboost-execution.md` and `models/xgb_optuna.meta.json`; distinguish training time from prediction time.

### Dwayne: TabNet, evaluation, and explainability

“TabNet adds an attention-based neural network to the comparison. It selects features at successive decision steps. We use three validation folds for TabNet and five for the tree models, and disclose that difference rather than treating the validation estimates as identical experiments.

[Show the verified comparison and state Macro F1 for each model.] We also examine precision, recall, and F1 for each class. A false negative is an attack classified incorrectly as safe; a false positive is normal traffic flagged as an attack. The U2R and R2L results matter even when overall accuracy looks strong.

XGBoost correctly classified 248 of 250 R2L cases; Random Forest classified 238 and TabNet 244. All three identified 10 of 13 U2R cases and missed the same three records. Show the confusion matrix, then the selected XGBoost U2R waterfall and TabNet attention plot. The waterfall is one high-confidence correct example, so it does not explain the shared misses. SHAP and attention describe model behavior; neither establishes the cause of an intrusion. Held-out results remain separate from tuning. Markie will connect this evidence to the paper and backend.”

**Before recording:** Use `outputs/03_evaluation/per_class_metrics.csv`, `test_set_evaluation.json`, `confusion_matrix_*.png`, `shap_local_example.png`, and `tabnet_attention_mask.png`. State actual plotted classes and values. Evaluation and figure production belong to Dwayne.

### Markie: paper walkthrough and backend

“Our Professor paper follows the required sections I–X, and the Portfolio version expands the same experiments into an academic manuscript. We now have test results for all three models. XGBoost had the highest Macro F1 at 0.945134 and correctly identified 248 of 250 R2L cases. All three models correctly identified 10 of 13 U2R cases and missed the same three. We recommend XGBoost as the preferred candidate for this benchmark, while retaining the limits of rare-class support and historical data.

The backend and dashboard integration are complete in the project handoff. The Express route validates 31 raw connection fields, and the Python bridge reconstructs the frozen 43-feature vector. The recorded verification includes 13 functional checks and a real Random Forest API request. The dashboard displays exported evaluation data, and its Analyze form uses the live endpoint. The paper reports remaining model-specific inference checks separately from the completed backend integration.

Our paper separates validation objectives, test results, and available training metrics. Sampled SHAP summaries, one local success case, and a TabNet attention plot are integrated. The figures do not explain the shared U2R misses, and each member still supplies their own reflection.”

**Before recording:** Rehearse a validated RF request using `server/examples/normal-smtp.json`, the running backend, and its actual response. Cite the test metrics and prediction exports; the sampled SHAP and attention figures are available in `outputs/03_evaluation/`; attribute them to Dwayne’s PR #22 source, now merged to main, and explain their sampling limits. Treat recorded batch prediction timings separately from HTTP latency. Do not imply that an offline metric verifies every model's live route.

### Kit Dustin: conclusion

“[State the selected model and the measured tradeoff supporting it.] The main lesson is to compare class-level detection, runtime, and explanations using traceable evidence. Future work should validate on newer traffic and test inference cost before deployment. Thank you.”

**Before recording:** The conclusion must agree with paper Section V.4 and the Executive Summary. Avoid suggesting that explanation figures resolve the missed U2R cases.

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

Codex assisted with the script draft. The team must check the final wording, measurements, and demonstration before recording and disclose AI assistance in paper Section X.
