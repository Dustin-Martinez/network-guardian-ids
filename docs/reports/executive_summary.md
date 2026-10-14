# Executive Summary: Network Guardian IDS

**Owner:** Markie (Role 2, Paper Lead)
**Updated:** 2026-10-14
**Status:** Final result summary integrated; manuscript review and video recording remain pending.
**Paper placement:** Professor Section VIII; target length is one formatted page.

## 1. What problem did we set out to solve and why does it matter

We compare three learning methods for distinguishing normal network connections from four attack families. Missed rare attacks and false alarms matter as much as aggregate correctness.

## 2. What did we discover about the data that shaped our decisions

The supplied file contains 494,021 records, substantial duplication, and only 52 U2R examples. Preparation retained 145,584 records, split into 109,188 training and 36,396 test rows with 43 encoded inputs.

## 3. Which approaches did we compare and how did we judge them

Random Forest, XGBoost, and TabNet were evaluated on the same frozen test set. Macro F1 gives each class equal weight. Test scores were 0.933095, 0.945134, and 0.930622, respectively; class recall and measured prediction times describe additional tradeoffs.

## 4. What do we recommend and what evidence supports it

XGBoost is the preferred candidate for this benchmark. It had the highest test Macro F1, R2L recall of 0.992000, and the shortest recorded full-test prediction time of 0.126 seconds. All models detected the same 10 of 13 U2R cases; the sampled explanation figures describe selected model behavior but do not explain the three missed cases. Deployment readiness requires further checks.

## 5. What are the limitations of our work and what would we do next

The historical simulated benchmark, only 13 U2R test records, preprocessing outside individual validation folds, and unequal optimization budgets limit generalization. Comparable training metrics and complete runtime provenance remain pending. The SHAP summaries and TabNet attention plot use samples of 1,000 test records; the local SHAP plot shows one selected, correctly classified U2R case. Future work should explain missed cases, use newer traffic, fit preprocessing within folds, and conduct controlled ablations.

## 6. What was our biggest mistake or surprise and what did we learn from it

A duplicate notebook export replaced the corrected label format; the fixed notebook now passes verification. Later auditing distinguished cumulative fold means and trial dispersion from independent fold scores. The lesson is to verify both artifact contents and metric definitions.

## Sources and remaining checks

Test metrics and class support: `outputs/03_evaluation/test_set_evaluation.json`; timing: `docs/reports/role-5-phase-3-dwayne-evaluation-suite.md`; row-level errors: `outputs/03_evaluation/test_predictions.csv`; explanation methods and snapshot: Dwayne's PR #22, merged to main at commit `7108f414c049ca265bdd6b305e979abcd7a5c614`. The integrated bridge and dashboard are documented in the merged handoffs. The paper distinguishes trial-value dispersion from fold SD and CV-versus-test differences from training gaps. Kit's review of PR #25 and the final recording remain pending. Research limitations include unavailable comparable full-training metrics, provisional normalized-metrics schema, and incomplete receiving-device verification for every model route.
