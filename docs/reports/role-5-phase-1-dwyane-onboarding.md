# Role 5 — Phase 1 Report: Dwayne Onboarding and Environment Verification

**Owner:** Dwayne (Role 5 — Evaluation Engineer, Explainability Contributor & TabNet Executor)  
**Phase:** 1 — Onboarding and Environment Verification  
**Status:** Completed  
**Date:** October 11, 2026  
**Related documents:**
- `docs/tasks/5.md` — Role 5 task mandate
- `docs/SETUP.md` — environment and data-preparation setup
- `docs/README.md` — documentation hierarchy
- `docs/contracts/role-5-training-execution-spec.md` — TabNet execution prerequisites

**AI Assistance Disclosure:** ChatGPT (OpenAI) was used as an AI-assisted support tool during this phase to help with troubleshooting, interpreting error messages. All commands and changes were reviewed and executed by the project member, who verified the resulting outputs in the local development environment.

---

## 1. Purpose

Record the completion of Role 5's initial repository, environment, and data-readiness checks before executing TabNet training.

## 2. Work Completed

- Used the repository at `C:\SCHOOL\I.S. PROJECT\network-guardian-ids`.
- Activated the project's `.venv` environment with Python 3.11.9.
- Ran `python src/verify_env.py`; the environment verification passed.
- Confirmed the required project dependencies imported successfully.
- Confirmed the processed training data was available and had the expected dimensions:
  - `X_train`: `(109188, 43)`
  - `y_train`: `(109188,)`
- Confirmed the class order: `normal`, `dos`, `probe`, `r2l`, `u2r`.
- Checked the frozen artifact hashes recorded for the following files:
  - `data/processed/class_order.json`
  - `data/processed/split_indices.json`
  - `data/processed/feature_names.json`
  - `src/models.py`
- Confirmed the expected hashes matched the values supplied by the project workflow.
- Opened Notebook 02 and ran the shared prerequisite cells (Cells 2–4) without errors before the TabNet run.

## 3. Verification Results

| Check | Result |
|---|---|
| Python version | Python 3.11.9 |
| Virtual environment | `.venv` activated |
| `src/verify_env.py` | Passed |
| `X_train` shape | `(109188, 43)` |
| `y_train` shape | `(109188,)` |
| Class order | `normal`, `dos`, `probe`, `r2l`, `u2r` |
| Frozen hash checks | Passed |
| Shared Notebook 02 prerequisite cells | Ran without errors |

### Frozen hash values checked

| Artifact | SHA-256 |
|---|---|
| `data/processed/class_order.json` | `63b3d7da8141a720abd0fb006c5ab285b4d4f6c2068bcc67304c35a40d08f52a` |
| `data/processed/split_indices.json` | `6b1272a7063348b1ba26ce60be2a6c492df6464fb228e1eb42e452011971f5db` |
| `data/processed/feature_names.json` | `d014bf4733de5e439169d5a5d346be4a0c2bef8080379ef27da6149357f2cef8` |
| `src/models.py` | `38c8e622642e2f77cefe9b704639e9c1fb448d46dde2453876175feefbaa4d2d` |

## 4. Issues and Resolution

No blocking environment or data-integrity errors were reported during the initial verification phase. Notebook 02 was initially found to be empty in the local repository history; this was reported to Kit, who subsequently pushed an updated notebook. The updated notebook was pulled and confirmed to contain valid notebook JSON and nonzero content.

## 5. Artifacts and Files

This phase verified existing project files and generated/processed data locally. No processed datasets or model artifacts were committed as part of this phase.

## 6. Outcome

**Phase 1 completed.** The environment and processed training data met the recorded prerequisites for proceeding with TabNet execution.

## 7. Next Step

Proceed to the TabNet training execution procedure in `docs/contracts/role-5-training-execution-spec.md`. Do not access the test arrays during training; test-set evaluation is reserved for Notebook 03.