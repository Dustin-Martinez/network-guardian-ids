# Team Discovery Log: Network Guardian IDS

**Maintainer:** Markie (Role 2); Kit reviews paper Section VII.
**Status:** Phase 1 scaffold with source-backed starter records.

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

## 4. Pending contributions

| Contributor | Needed evidence | Paper use |
|---|---|---|
| Kit | Confirm dataset identity, frozen counts, preprocessing decisions | II, VII |
| Amber | RF execution report, tuning outcomes, frontend integration issues | III.1, VII |
| Kenneth | XGBoost runtime, hardware limits, execution failures and recovery | III.2, VII |
| Dwayne | TabNet execution, evaluation and explainability findings | III.3, V-VII |
| Markie | Backend bridge issues after Phase 2; final synthesis after Phase 3 | VII, VIII |

## 5. Finalization checklist

- [ ] Attach traceable evidence for each new record.
- [ ] Replace placeholders only after the owning member supplies evidence.
- [ ] Have contributors verify attribution and conclusions.
- [ ] Integrate records into Section VII without inventing chronology.
- [ ] Cite external sources in APA and disclose AI assistance in Section X.
