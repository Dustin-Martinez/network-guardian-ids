# Team Discovery Log: Network Guardian IDS

**Maintainer:** Markie (Role 2); Kit reviews paper Section VII.
**Status:** Updated for final paper integration and Phase 4 documentation on 2026-10-14; remaining evidence gaps and review ownership are explicit.

## 1. Recording conventions

Record the real question, attempted approach, observation or failure, change, verification, and lesson. Attribute inherited events to their author; they were not rerun during documentation scaffolding. A source report records what its author observed, not independent reproduction. Keep expected outcomes separate from measured results.

Use `Reported resolved`, `Locally verified`, `Open`, or `Pending evidence` as status values. Every number, plot, or performance claim must identify its repository source and section or artifact field. Add event dates only when supplied by the original author.

## 2. Starter discovery records

### DL-001: Python dependency compatibility

- **Owner / phase:** Kit / Role 1 Phase 1.
- **Question:** Can the pinned dependencies install on the default interpreter?
- **Attempt and observation:** Kit reports that Python 3.13 caused pandas 2.1.1 installation to fall back to a failing source build.
- **Change:** Recreated the environment on Python 3.11.9 and installed the pinned packages.
- **Verification:** Kit's report records passing imports and runtime checks. That historical report lists dependencies that differ from the current `requirements.txt`; use the current manifest for fresh reproduction.
- **Lesson:** Check interpreter compatibility and record the dependency manifest actually used.
- **Status:** Reported resolved; not rerun in Role 2 Phase 1.
- **Source:** `docs/reports/role-1-phase-1-kit-environment-setup.md`, sections 5-6; `requirements.txt`.

### DL-002: Feature manifest parsing

- **Owner / phase:** Kit / Role 1 Phase 2.
- **Question:** Does the names file explicitly declare the target column?
- **Attempt and observation:** The parser expected 43 lines; Kit reports 42 non-empty lines: an attack header plus 41 feature definitions.
- **Change:** Validate 42 lines, skip the header, and append the implicit label column.
- **Verification:** The Phase 2 report records corrected parsing and array integrity checks.
- **Lesson:** Inspect the source schema before fixing parser assumptions.
- **Status:** Reported resolved.
- **Source:** `docs/reports/role-1-phase-2-kit-data-preparation.md`, sections 12 and 14, Issue 1.

### DL-003: Missing normal label mapping

- **Owner / phase:** Kit / Role 1 Phase 2.
- **Question:** Does the attack manifest cover every observed target?
- **Attempt and observation:** Kit reports `ValueError: Unmapped attack labels: ['normal']` because the manifest omitted normal traffic.
- **Change:** Add `normal -> normal` at runtime while preserving the raw manifest.
- **Verification:** The report records the correction and the resulting five-class order.
- **Lesson:** Validate target coverage before transformation.
- **Status:** Reported resolved.
- **Source:** `docs/reports/role-1-phase-2-kit-data-preparation.md`, sections 12.3 and 14, Issue 2.

### DL-004: Label-array serialization

- **Owner / phase:** Kit / Role 1 Phase 2.
- **Question:** Can saved labels load without enabling pickle?
- **Attempt and observation:** Object-dtype label arrays could not load with `allow_pickle=False`.
- **Change:** Export fixed-width Unicode labels using `dtype='<U6'`.
- **Verification:** Kit's report records array integrity checks after regeneration.
- **Lesson:** Treat serialized dtype as part of the downstream interface.
- **Status:** Reported resolved.
- **Source:** `docs/reports/role-1-phase-2-kit-data-preparation.md`, sections 12.1 and 14, Issue 3.

### DL-005: Unsupported claims in documentation drafts

- **Owner / phase:** Markie / Role 2 Phase 1; prepared with Codex assistance.
- **Question:** Are the existing summary and discovery claims supported by this clone?
- **Observation:** The summary named a winning dual-engine system while final comparison artifacts were absent. The discovery draft described SMOTE failures and model outcomes without traceable execution evidence.
- **Change:** Replace unsupported claims with pending results and attributed records from Kit's reports. Do not infer failures from design choices.
- **Verification:** Reviewed the tracked file inventory and Kit's Phase 3 section 10, which still contains result placeholders.
- **Lesson:** Keep measured results, reported events, and plans distinguishable.
- **Status:** Locally verified documentation correction.
- **Sources:** `docs/reports/executive_summary.md`; `docs/reports/role-1-phase-3-kit-model-architecture.md`, section 10; clone baseline `c5b40c8`.

### DL-006: Onboarding notebook overwrites label dtype

- **Event date:** 2026-10-11 (Asia/Manila).
- **Owner / phase:** Markie / Role 2 Phase 1; executed with Codex assistance.
- **Question:** Does Notebook 01 produce the shapes and dtypes required by the updated setup guide?
- **Attempt and observation:** Ran every cell in order with the Python 3.11.9 virtual environment. The final duplicate export cell (index 16) used `.to_numpy()` without a Unicode dtype, overwriting the correct `<U6` arrays from cell 15. `np.load(..., allow_pickle=False)` then failed for both labels.
- **Change:** Converted only the locally generated label arrays to `<U6`. No source notebook, frozen JSON, or model code was changed.
- **Verification:** Both labels now load without pickle; training labels have 109,188 rows and test labels 36,396 rows. Feature arrays have 43 columns and dtype float64. All four frozen hashes match the setup guide.
- **Lesson:** A later duplicate export can undo an earlier serialization fix; verify the artifacts after the last cell completes.
- **Status:** Resolved upstream and locally verified on 2026-10-12. Kit removed the duplicate cell in commit `46c3401` (merged into main). Reran the fixed notebook top to bottom; labels load with `allow_pickle=False` as `<U6`, shapes match, and all four frozen hashes are OK.
- **Source:** `notebooks/01_EDA_and_Data_Prep.ipynb`, code cell indices 15-16; `docs/SETUP.md`, Steps 7-9; `docs/reports/role-2-phase-1-markie-documentation-scaffolding.md`, section 6.

## 3. Reusable entry template

### DL-NNN: [Short discovery title]

- **Event date:** [Contributor-supplied date, or not recorded]
- **Owner / phase:** [Member and phase]
- **Question:** [What uncertainty prompted the work?]
- **Attempt and observation:** [Actual approach, error, or measurement]
- **Change:** [What changed and why?]
- **Verification:** [Command/result or artifact field; distinguish reported from rerun]
- **Lesson:** [What the team learned]
- **Status:** [Reported resolved / Locally verified / Open / Pending evidence]
- **Source:** [Exact repository path and section/field]

## 4. Review queue and outstanding evidence

| Owner | Review or evidence still needed | Paper use |
|---|---|---|
| Kit | Review and approve final manuscript PR #25; confirm remaining method and attribution details | II, III, VII, IX |
| Amber | Confirm RF source attribution and dashboard statements during manuscript review | III.1, VII, IX |
| Kenneth | Confirm XGBoost execution/runtime attribution and his reflection | III.2, VII, IX |
| Dwayne | Confirm TabNet, evaluation, and explainability interpretation and his reflection | III.3, V-VII, IX |
| Markie | Final manuscript integration and evidence audit completed; video walkthrough is prepared, recording/presentation remains to be delivered | VIII, IX, video |

## 5. Finalization checklist

- [x] Attach traceable evidence for each integrated discovery record.
- [x] Replace empirical-result placeholders with source-verified results.
- [ ] Have contributors verify attribution and conclusions; Kit's final manuscript review is pending.
- [x] Integrate records into Section VII without inventing chronology.
- [x] Cite external sources in APA and disclose AI assistance in Section X.

## 6. Evaluation integration discoveries on 2026-10-14

### DL-007: Backend implementation and live frontend connection

- **Owner / phase:** Markie, backend implementation; Amber, frontend integration.
- **Observation:** The Express route and Python bridge passed 13 functional checks and a real RF request. Merged UI work removed fabricated panel values and wired the dashboard to exported evaluation data. Only the Analyze form and threat gauge make live API requests; the charts and model comparisons are static views of frozen outputs.
- **Status:** RF request verified. The updated contract and bridge pass raw engineered inputs to TabNet, matching training; a real TabNet artifact request and receiving-device XGBoost verification remain open.
- **Sources:** `docs/reports/role-2-phase-2-markie-backend-bridge.md`; `docs/reports/role-3-phase-3-amber-frontend-backend-integration.md`; `docs/contracts/api_data_contract.md`; `docs/handoffs/ui_phase_handoff.md`; `server/predict_bridge.py`.

### DL-008: XGBoost final-refit early-stopping failure

- **Owner / phase:** Kit, XGBoost execution; documented in the 2026-10-14 handoff.
- **Problem:** The final refit failed because early stopping required a validation dataset but the refit supplied no `eval_set`.
- **Resolution:** The model builder accepts an early-stopping flag; CV retains validation-based stopping, while the final refit disables it. The optimization study was preserved.
- **Status:** Reported resolved; no training was rerun for paper integration.
- **Sources:** `docs/handoffs/xgboost.md`, section 6.1; `src/models.py`; `docs/reports/role-4-phase-2-kit-xgboost-execution.md`.

### DL-009: Fold statistics and accumulated study history

- **Owner / phase:** Markie, paper source audit on 2026-10-14.
- **Question:** Do the exported fold scores, metadata standard deviations, and configured trial budgets describe the same experiment?
- **Observation:** XGBoost and TabNet export cumulative fold means through `trial.report(mean(fold_scores), fold_idx)`. Their metadata SD is computed by `_safe_cv_std` over all non-null recorded trial values, including pruned values. RF independently reconstructs its best-trial fold scores and fold SD.
- **Verification:** Trial-log dispersion reproduces XGBoost SD 0.0259540060 and TabNet SD 0.0192504074. The saved XGBoost log has 90 records (78 complete, 12 pruned), while 30 is the per-invocation budget. RF has 20 complete records; TabNet has 15 complete and five pruned.
- **Change in paper:** Preserve selected CV objective means, distinguish trial dispersion from fold SD, and report accumulated trial counts. Do not silently rewrite owner CSVs or sidecars.
- **Status:** Definitions verified from code and logs; independent fold-report corrections remain with the model owners.
- **Sources:** `src/models.py`, `_safe_cv_std`, objectives and save functions; `outputs/02_training/*_cv_scores.csv`; `outputs/02_training/optuna_*_trials.csv`; `models/*.meta.json`.

### DL-010: Shared rare-class misses and operational interpretation

- **Owner / phase:** Dwayne, test evaluation; Markie, paper verification.
- **Observation:** All models have U2R recall 10/13 = 0.769231 and miss the same three exported rows (zero-based positions 20207, 30364, 32453). RF and TabNet label all three normal. XGBoost labels row 20207 R2L and the other two normal.
- **Verification:** All 36,396 exported prediction rows reproduce the JSON per-class F1 and Macro F1. Reconstructed attack-as-normal counts are RF 22, XGBoost 10, TabNet 16; normal-as-attack counts are RF 13, XGBoost 21, TabNet 68.
- **Lesson:** A missed attack family is not necessarily an attack classified as normal. Identical recall does not prove an intrinsic data ceiling or rule out other models improving detection.
- **Status:** Verified from exported predictions without model refitting. Sampled global and local tree explanations and a TabNet attention aggregate are now available; they do not analyze the three shared U2R misses.
- **Sources:** `outputs/03_evaluation/test_predictions.csv`; `test_set_evaluation.json`; `per_class_metrics.csv`; `docs/reports/role-5-phase-3-dwayne-evaluation-suite.md`.


### DL-011: Sampled explanation outputs added to paper drafts

- **Owner / phase:** Dwayne / Role 5 Phase 4; Markie / Role 2 Phase 3 integration.
- **Observation:** The Phase 4 report, now merged through PR #22, describes RF and XGBoost TreeExplainer summaries from 1,000 sampled frozen-test records, one selected correctly classified U2R XGBoost example, and TabNet attention averaged over decision steps and 1,000 sampled records.
- **Integration:** Added the four supplied images, method limits, and source attribution to both manuscripts. The snapshot is commit `7108f414c049ca265bdd6b305e979abcd7a5c614`; it was not merged into the main baseline at integration time.
- **Interpretive limit:** The local figure is a selected success case and does not explain the three missed U2R records. Predicted-class SHAP summaries and TabNet attention answer different questions; neither establishes causation.
- **Status:** Source report and files reviewed; upstream merge is complete, contributor review remains pending.
- **Sources:** `docs/reports/role-5-phase-4-dwayne-explainability.md` and `outputs/03_evaluation/{shap_summary_rf.png,shap_summary_xgb.png,shap_local_example.png,tabnet_attention_mask.png}` at the stated snapshot.


### DL-012: Dashboard panels now use exported evaluation data

- **Owner / phase:** Kit (project oversight), Amber (frontend), and Markie (backend integration); merged to main on 2026-10-14.
- **Observation:** PR #23 removes mock panel data and wires class distribution, confusion matrices, feature importances, and model comparisons to repository outputs. The Analyze form and threat gauge remain the live API surfaces; the charts display static evaluation data.
- **TabNet update:** The API contract and bridge now pass the raw engineered matrix used during training. The saved scaler is not used. The branch's fixture-based tests do not establish that a real TabNet artifact request succeeds.
- **Status:** Dashboard source merged; real TabNet artifact verification and receiving-device XGBoost verification remain open.
- **Sources:** `docs/handoffs/ui_phase_handoff.md`; `docs/handoffs/ui_usage_guide.md`; `docs/contracts/api_data_contract.md`; `server/predict_bridge.py`; PR #23, merged as of main snapshot `e250700`.
