```markdown
# Documentation Hierarchy — Network Guardian IDS

This document defines the precedence order of every `.md` file under
`docs/`. When two documents disagree, when a topic is not covered, or
when a teammate needs to decide something without asking, this is the
authoritative reference.

Read this file before acting on any other `docs/` file.

---

## 1. Directory Map

```
docs/
├── README.md                 <- this file (highest precedence for
│                                 navigation and conflict resolution)
├── contracts/                <- authoritative technical agreements
├── tasks/                    <- role mandates (scope and sequence)
├── reports/                  <- execution records and deliverables
└── specs/                    <- reserved for future design documents(non exisiting)
```

Files outside `docs/` that carry contractual weight:

```
data/processed/feature_names.json       <- frozen feature ordering
data/processed/split_indices.json       <- frozen train/test split
data/processed/class_order.json         <- frozen class ordering
src/verify_env.py                       <- environment contract
requirements.txt                        <- pinned dependency contract
```

---

## 2. Precedence Order

When two documents conflict, the one higher in this list wins:

1. **`docs/contracts/*.md`** — authoritative technical agreements.
   Interface definitions, schemas, function signatures, artifact paths.
2. **`docs/tasks/*.md`** — role mandates. Scope, sequence, deliverables
   per role. A task mandate defines *what* is produced, not *how*.
3. **`docs/reports/*.md`** — execution records. Document what was done,
   with what metrics. A report never overrides a contract or mandate.
4. **Everything else** — READMEs, inline comments, commit messages.
   Informational only. Never authoritative.

If a report disagrees with a contract, the contract wins.
If a task mandate disagrees with a contract, the contract wins.
If a contract is silent, the task mandate fills the gap.
If both are silent, the owning role decides (see section 5).

---

## 3. Folder Purposes

### 3.1 `docs/contracts/`

Contains authoritative technical agreements between roles. A contract:

- Defines exact interfaces (function signatures, payload schemas, file
  formats, artifact paths)
- Freezes parameters (search spaces, trial budgets, hyperparameters,
  class orderings, feature orderings)
- Enumerates anti-patterns that would invalidate a result
- Specifies acceptance criteria
- Establishes change control

Current contracts:

| File | Owner | Governs |
|---|---|---|
| `api_data_contract.md` | Kit | Client/Express/bridge payloads, feature ordering, HTTP status codes, validation rules |
| `role-3-rf-architecture-spec.md` | Kit | Random Forest functions, search space, training protocol, meta schema |
| `role-4-training-execution-spec.md` | Kit | How XGBoost and TabNet runs are executed, monitored, reported |
| `branch_protection_policy.md` | Kit | Branch naming, PR rules, admin bypass |

### 3.2 `docs/tasks/`

Contains role mandates — what each role produces, in what order, at what
quality bar. A task mandate:

- Lists deliverables per phase
- Specifies handoffs between roles
- References the contracts that govern the deliverables

A task mandate does not define interfaces. It defers to contracts for
any technical detail.

### 3.3 `docs/reports/`

Contains execution records. A report:

- States what was done
- Reports metrics (CV Macro F1, test-set results, training time)
- Documents issues encountered and their resolutions
- Records the exact artifacts produced

A report never overrides a contract. If a report's metric disagrees with
what a contract specifies as the target, the contract's target stands and
the report explains the deviation.

### 3.4 `docs/specs/`

Reserved for future design documents that are not contracts. Not used in
this sprint.

---

## 4. Conflict Resolution

### 4.1 Contract vs. contract

Two contracts cannot disagree because each owns a distinct scope. If two
contracts touch the same topic and disagree, that is a bug in the
contracts. Report it to the project manager.

Example of a bug: `api_data_contract.md` says `service` is a string, and
`role-3-rf-architecture-spec.md` says `service` is an integer. The project
manager resolves by updating the contract whose scope is wrong.

### 4.2 Contract vs. code

If the code disagrees with a contract, the contract is authoritative until
either is changed. The team fixes whichever is wrong after a PR that
updates both in lockstep.

Example: `api_data_contract.md` says the response includes `confidence`
as a percentage. The Express server currently returns a probability in
`[0, 1]`. The code is wrong. Fix the code, do not silently relax the
contract.

### 4.3 Task mandate vs. contract

The contract wins. Task mandates defer to contracts for technical detail.

Example: `tasks/1.md` says "Train XGBoost with validation-based early
stopping." The contract `role-4-training-execution-spec.md` specifies the
exact patience value and the exact evaluation metric. The contract's
values are authoritative.

### 4.4 Report vs. contract

The contract wins. Reports document execution. They never redefine the
rules.

Example: a Phase 3 report says "RF ran with 30 trials." The contract
`role-3-rf-architecture-spec.md` says 20 trials. If the RF actually ran
with 30, either the report is wrong or the RF implementation deviated
from the contract. Investigate and correct.

### 4.5 Task mandate vs. task mandate

Task mandates are role-scoped and never overlap. If two mandates disagree,
report to the project manager.

---

## 5. When No Document Covers a Topic

If a decision is required and no contract, mandate, or report addresses it:

1. **Identify the owning role for the topic.** Use the table below.
2. **The owning role decides.** No cross-role approval required for
   decisions within that role's scope.
3. **Document the decision.** Add a note to the relevant role's report in
   `docs/reports/`. If the decision affects another role, add a short
   note to the relevant contract.
4. **If two roles disagree on ownership,** escalate to the project manager.

### 5.1 Topic-to-Owner Map

| Topic | Owner |
|---|---|
| Data preparation pipeline | Kit |
| Feature encoding scheme | Kit |
| Train/test split and stratification | Kit |
| XGBoost model and hyperparameters | Kit |
| TabNet model and hyperparameters | Kit |
| Random Forest model and hyperparameters | Amber |
| Client UI, forms, dashboards | Amber |
| Express server routes and validation | Markie |
| Python inference bridge | Markie |
| Model evaluation metrics and figures | Markie |
| SHAP explainability outputs | Markie |
| Paper draft and executive summary | Markie |
| Training execution and monitoring | Kenneth |
| Video production and presentation script | Kenneth |
| Branch naming and PR workflow | Kit |
| Documentation hierarchy (this file) | Kit |

---

## 6. Fallback Rules

When a teammate encounters a situation the documentation does not cover,
apply these fallback rules in order.

### 6.1 Stay within your scope

Do not modify files owned by another role. If a change is needed in
another role's file, request it from that role.

### 6.2 Prefer the more specific rule

When two documents could both apply, follow the one that is more specific
to the situation. `role-3-rf-architecture-spec.md` section 5 is more
specific about Tomek Links in RF folds than `tasks/3.md` is. Follow the
specific one.

### 6.3 Do not silently deviate

If you must deviate from a contract, stop and report first. Deviation
without notification breaks reproducibility and the trust the contracts
are designed to preserve.

### 6.4 Preserve anti-leakage discipline

No fallback rule may override the anti-leakage constraints:

- Encoders, scalers, and resamplers are fit on training data only.
- The test partition is accessed only in Notebook 03.
- No training function receives the test arrays.

If a situation seems to require violating one of these, stop and report
to the project manager.

### 6.5 Preserve the frozen artifacts

The following files are frozen for the sprint. They may not be
regenerated or edited except through a formal PR that also updates every
downstream consumer:

- `data/processed/feature_names.json`
- `data/processed/split_indices.json`
- `data/processed/class_order.json`
- `data/processed/encoder_service.pkl`
- `data/processed/encoder_onehot_protocol_flag.pkl`
- `data/processed/scaler_tabnet.pkl`

---

## 7. Roles in the Sprint

| Role | Member | Primary Folder |
|---|---|---|
| 1 | Kit Dustin (PM) | `docs/contracts/`, `docs/reports/role-1-*` |
| 2 | Markie | `docs/reports/role-2-*` |
| 3 | Amber | `docs/reports/role-3-*` |
| 4 | Kenneth | `docs/reports/role-4-*` |

Each role reports to the project manager for coordination but owns its
folder's content.

---

## 8. How to Add a New Document

### 8.1 Adding a contract

1. Confirm the topic is not already covered by an existing contract.
2. Create the file under `docs/contracts/` with a name of the form
   `<scope>-<topic>-spec.md` or `<scope>-contract.md`.
3. Include the following sections:
   - Purpose
   - Responsibility Boundary
   - Interface (function signatures or schema)
   - Parameters or Search Space (if applicable)
   - Protocol
   - Artifacts
   - Anti-Patterns
   - Acceptance Criteria
   - Change Control
4. Open a PR.
5. Obtain approval from the project manager.
6. Merge.

### 8.2 Adding a task mandate

1. Create the file under `docs/tasks/` with a name of the form
   `role-<N>-<topic>.md`.
2. Reference the relevant contracts.
3. Open a PR.

### 8.3 Adding a report

Reports are non-negotiable outputs of every phase. Add them as the phase
completes. No PR required for report content, but reports must reference
the contracts and mandates they implement.

---

## 9. Quick Decision Flowchart

```
Decision needed
      |
      v
Is it covered by a contract?
      |                     |
     Yes                    No
      |                     |
      v                     v
Follow the contract.   Is it covered by a task mandate?
                        |                     |
                       Yes                    No
                        |                     |
                        v                     v
                  Follow the mandate.   Is it inside your role's scope?
                                        |                     |
                                       Yes                    No
                                        |                     |
                                        v                     v
                                  Decide and            Ask the owning role.
                                  document in
                                  your report.
```

---

## 10. Escalation

If the hierarchy does not resolve a conflict:

1. Post the conflict in the team channel.
2. Tag the project manager (Kit Dustin).
3. Wait for a decision before proceeding.
4. Once decided, the decision is recorded in the relevant contract or
   report.

Silent workarounds are not permitted. Undocumented deviations invalidate
any result that depends on them.

---

## 11. Change Control

This file is authoritative for documentation navigation and conflict
resolution. Any change requires:

1. A pull request that modifies this file.
2. A note in `docs/reports/` describing the change and the reason.
3. Approval by the project manager.

If a change to a contract contradicts this file's precedence rules, the
change must first update this file, then the contract.
```