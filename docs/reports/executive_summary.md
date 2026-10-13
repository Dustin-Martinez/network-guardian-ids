# Executive Summary: Network Guardian IDS

**Owner:** Markie (Role 2, Paper Lead)
**Status:** Phase 1 draft; final model results pending.
**Paper placement:** Section VIII; target length is one formatted page.

## 1. What problem did we set out to solve, and why does it matter?

Network Guardian IDS studies whether machine learning can distinguish normal network connections from four attack families: denial of service (DoS), probing, remote-to-local access (R2L), and user-to-root escalation (U2R). The aim is to compare detection approaches and explain their errors, especially missed rare attacks and false alarms. This is a research prototype; effectiveness on current production traffic has not been established.

## 2. What did we discover about the data that shaped our decisions?

Kit's data-preparation report records substantial duplication, skewed byte and duration values, and very few U2R examples. These findings motivated duplicate removal, removal of redundant features, logarithmic transformations, and a combination of categorical encodings. Local onboarding now verifies 145,584 prepared connections split into 109,188 training and 36,396 test rows, with 43 encoded features. The frozen split contains only 39 U2R training examples and 13 test examples, so rare-class recall must be interpreted carefully. (Source: `data/processed/split_indices.json`; all frozen hashes verified during onboarding.) (Source: `docs/reports/role-1-phase-2-kit-data-preparation.md`, sections 5-9.)

## 3. Which approaches did we compare, and how did we judge them?

The planned comparison covers Random Forest, XGBoost, and TabNet: independently trained trees, sequentially improved trees, and an attention-based neural network. The main measure is Macro F1, which gives each class equal weight. Per-class recall, false alarms, missed attacks, training time, and prediction time will explain tradeoffs. Cross-validation uses five folds for Random Forest and XGBoost and three for TabNet; this difference must remain explicit. (Sources: the RF, XGBoost, and TabNet execution contracts under `docs/contracts/`; Kit's Phase 3 report.)

## 4. What do we recommend, and what evidence supports it?

**Pending evaluation.** No winning model or deployment recommendation is established in this draft. The final recommendation will combine cross-validation results, held-out test metrics, rare-class recall, runtime, and explanation quality. Insert the selected model and measured tradeoffs from `outputs/02_training/model_comparison.csv`, `outputs/03_evaluation/test_set_evaluation.json`, and `outputs/03_evaluation/per_class_metrics.csv` after Dwayne delivers evaluation outputs. Keep validation-based selection distinct from held-out test reporting.

## 5. What are the limitations of our work, and what would we do next?

The historical benchmark does not establish performance on today's networks. Few rare-class examples limit the stability of recall estimates. Different validation fold counts and CPU training budgets also limit comparison. Future work should validate on newer traffic, measure inference cost, and test the value of preparation steps through controlled experiments. Live packet capture and production deployment remain future work.

## 6. What was our biggest mistake or surprise, and what did we learn from it?

One documented early mistake was setting up pinned dependencies with Python 3.13. Kit reports that pandas installation failed and that recreating the environment on Python 3.11.9 resolved it. This shows why dependency compatibility should be verified before model work. The team will select its final biggest lesson after reviewing all execution reports. (Source: `docs/reports/role-1-phase-1-kit-environment-setup.md`, section 6.)

## Editorial completion checklist

- [ ] Replace pending results with values checked against delivered artifacts.
- [x] Verify prepared counts and class shares against the frozen split manifest.
- [ ] Reconcile benchmark provenance before final submission; the narrative context mixes KDD Cup 1999 and KDDTrain+ terminology.
- [ ] Convert working source pointers into APA citations and include full references in paper Section X.
- [ ] Reconcile the recommendation with evaluation and runtime evidence.
- [ ] Fit the six answers within one formatted page; omit this checklist from the submitted summary.
- [ ] Disclose AI assistance in the paper's AI Tool Disclosure subsection.
