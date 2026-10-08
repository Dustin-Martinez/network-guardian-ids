# Team Task Delegation Matrix: Network Guardian IDS

This document formalizes the division of labor across the project
lifecycle. Each member has a dedicated operational mandate detailing
their exact phases, dependencies, and file responsibilities.

---

## Team Roster

| Member | Primary Role | Secondary Role | Operational Mandate |
|---|---|---|---|
| Kit Dustin | Project Manager | Data Preparation & Advanced Model Developer | `docs/tasks/1.md` |
| Markie | Paper Lead | Backend Designer | `docs/tasks/2.md` |
| Amber | Model Developer (Random Forest) | UI/UX Designer | `docs/tasks/3.md` |
| Kenneth | Execution Lead (XGBoost) | Technical Tester & Video Producer | `docs/tasks/4.md` |
| Dwayne | Evaluation Engineer (TabNet Executor) | Explainability Contributor | `docs/tasks/5.md` |

---

## Model Ownership

| Model | Code Owner | Execution Owner | Estimated Wall Time |
|---|---|---|---|
| Random Forest | Amber | Amber | 1.5–3 hours |
| XGBoost | Kit | Kenneth | 4–6 hours |
| TabNet | Kit | Dwayne | 6–8 hours |

Execution on three separate machines. No resource contention.

---

## Cross-Role Contracts

| Contract | Owner | Governs |
|---|---|---|
| `docs/contracts/api_data_contract.md` | Kit | Client, Express, bridge payloads |
| `docs/contracts/role-3-rf-architecture-spec.md` | Kit | Random Forest implementation for Amber |
| `docs/contracts/role-4-training-execution-spec.md` | Kit | XGBoost execution for Kenneth |
| `docs/contracts/role-5-training-execution-spec.md` | Kit | TabNet execution for Dwayne |
| `docs/contracts/branch_protection_policy.md` | Kit | Branch naming, PR rules, admin bypass |

---

## Workflow and Presentation Hand-Off Protocol

### Phase 1 — Data Preparation and Modeling Code

- **Kit** builds the data preparation pipeline. Writes `src/utils.py`,
  `src/data_prep.py`, `src/encoding.py`.
- **Kit** writes the core logic for XGBoost and TabNet in
  `src/models.py`.
- **Amber** writes the Random Forest logic in the RF section of
  `src/models.py` against the RF architecture contract.

### Phase 2 — Execution and Tuning

- **Kenneth** runs the XGBoost training loop (Notebook 02 Cells 7 and 8)
  following `docs/contracts/role-4-training-execution-spec.md`.
- **Dwayne** runs the TabNet training loop (Notebook 02 Cells 9 and 10)
  following `docs/contracts/role-5-training-execution-spec.md`.
- **Amber** runs the Random Forest training loop (Notebook 02 Cells 5
  and 6) following the RF architecture contract.

All three runs proceed on separate machines to parallelize compute.

### Phase 3 — Evaluation, XAI, and UI

- **Dwayne** produces confusion matrices, per-class metrics,
  precision-recall curves, and the model comparison figure.
- **Dwayne** produces SHAP summary plots for Random Forest and XGBoost,
  plus TabNet attention mask visualizations.
- **Markie** integrates Dwayne's figures into the paper and drafts the
  narrative interpretation.
- **Markie** builds the Node.js Express backend and the Python inference
  bridge (`server/server.js`, `server/predict_bridge.py`).
- **Amber** builds the Next.js dashboard and wires it to the backend.

### Phase 4 — Documentation and Video Delivery

- **Markie** finalizes the paper, executive summary, and discovery log.
- **Kenneth** produces the final video presentation (`.mp4`), ensuring
  all members appear on-camera to present their respective components.
- **Kit** runs the final review pass and manages the submission package.