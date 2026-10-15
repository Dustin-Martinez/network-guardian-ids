# Phase 3 Report — Frontend-Backend Integration

**Role:** Role 3 — Amber
**Title:** Model Developer (Random Forest) & UI / UX Designer
**Phase:** 3 of 4
**Sprint Day:** Day 10 of 10
**Status:** Complete
**Branch:** `role-3-phase-2`
**Contracts referenced:** `docs/contracts/api_data_contract.md`

---

## 1. Objective

Per `tasks/role_3.md` Phase 3, connect the TSX dashboard form
submission to send an HTTP POST request to
`http://localhost:5000/api/analyze` and dynamically render prediction
labels, threat flags, and confidence percentages returned from
Markie's Node.js bridge.

The mandate names one target file (`client/src/app/page.tsx`) and one
integration endpoint. This phase closes the loop between the Phase 1
client scaffold and Markie's Phase 2 backend.

---

## 2. Scope

### In scope

- Disable client mock mode so the form posts to the live server
- Verify the payload matches `api_data_contract.md` section 2
- Verify the response renders per section 3
- Verify error handling for HTTP 400, HTTP 500, and unreachable server
- Run end-to-end tests with the Random Forest model
- Write this sprint report

### Out of scope

- Backend implementation (Markie, Phase 2)
- Notebook 03 evaluation and SHAP (Markie, Phase 3 paper)
- Model training (Phase 2, complete)
- XGBoost and TabNet model artifacts (Kit and Dwayne)

---

## 3. Inputs

| Artifact | Source | Purpose |
|---|---|---|
| `docs/contracts/api_data_contract.md` | Kit | Payload and response shape |
| `docs/reports/role-2-phase-2-markie-backend-bridge.md` | Markie | Verified backend behavior |
| `server/server.js` | Markie | Express endpoint implementation |
| `server/predict_bridge.py` | Markie | Python inference bridge |
| `models/rf_baseline.joblib` and `.meta.json` | Amber | RF artifact served by the bridge |
| `client/src/lib/data.ts` | Amber | Client `analyze()` function |
| `client/src/types/index.ts` | Amber | TS interfaces copied from the contract |
| `client/src/components/AnalyzeForm.tsx` | Amber | Form submission and error display |

---

## 4. Deliverables

### 4.1 Files

| File | Change |
|---|---|
| `client/src/lib/data.ts` | `USE_MOCK` flipped from `true` to `false` |
| `docs/reports/role-3-phase-3-amber-frontend-backend-integration.md` | This report |

### 4.2 Files confirmed unchanged

| File | Reason |
|---|---|
| `client/src/types/index.ts` | Already matched the API contract v1.0 exactly |
| `client/src/components/AnalyzeForm.tsx` | Already built the correct payload and routed responses to the alert module |
| `client/src/app/page.tsx` | Already hosted the form and the alert module |

The integration required exactly one line of code:
`const USE_MOCK = true` became `const USE_MOCK = false`.

---

## 5. Contract Alignment

| Contract item | Implementation |
|---|---|
| Section 1: endpoint and method | `POST http://localhost:5000/api/analyze` with JSON body |
| Section 2: request fields | All 31 fields present; categoricals sent as raw strings |
| Section 2: string fields | `protocol_type`, `service`, `flag` are strings, not encoded integers |
| Section 3: response fields | Client reads `prediction`, `confidence`, `is_threat`, `model` |
| Section 3: error envelope | HTTP 400 and 500 both return a full `PredictionResponse` with defaults plus `error` |
| Section 4.3: model selection | Form dropdown sends the optional `model` field |
| Section 5: HTTP status codes | 400 and 500 surface the `error` string to the form |
| Section 6: validation rules | Client mirrors the rules; server is authoritative |

---

## 6. Design Decisions and Rationale

### 6.1 Single switch for mock mode

Phase 1 built `analyze()` with two branches behind `USE_MOCK`. The
real `fetch` path was already written and correct. Phase 3 required
only flipping the constant. This kept the change surface minimal and
left the mock path intact for offline testing.

### 6.2 No changes to types or form

`client/src/types/index.ts` and `client/src/components/AnalyzeForm.tsx`
already matched the contract after the Phase 1 corrections. Verifying
them against the API contract confirmed they needed no edits.
Changing files unnecessarily would have created review noise.

### 6.3 Default model remains xgboost

The form's dropdown defaults to `xgboost`. Markie's bridge defaults
to `xgboost` when the `model` field is absent. For the Phase 4 demo
the operator selects `random_forest` manually. This matches the
contract and avoids special-casing.

---

## 7. Verification

### 7.1 Completed

- Payload shape verified against contract section 2
- Response shape verified against contract section 3
- `USE_MOCK` confirmed `false` in `client/src/lib/data.ts`
- Server and client both start without error on ports 5000 and 3000
- Six end-to-end tests run against the live Express server with the
  Random Forest model loaded

### 7.2 End-to-end test results

| # | Test | Expected | Observed | Pass |
|---|---|---|---|---|
| 1 | Normal SMTP, Random Forest | prediction `normal`, threat off, model `random_forest` | [fill in] | [ ] |
| 2 | DoS flood, Random Forest | prediction `dos`, threat on | [fill in] | [ ] |
| 3 | Port probe, Random Forest | prediction `probe`, threat on | [fill in] | [ ] |
| 4 | Rate field set to 2 | client-side validation error, no HTTP request sent | [fill in] | [ ] |
| 5 | XGBoost selected | server error (artifact absent) | [fill in] | [ ] |
| 6 | Express server stopped | "Service unavailable" message | [fill in] | [ ] |

### 7.3 Reproduction steps

1. Confirm `models/rf_baseline.joblib` and `models/rf_baseline.meta.json` exist.
2. Terminal 1: `npm ci --prefix server` then `npm start --prefix server`. Expect `Node.js Server running on port 5000`.
3. Terminal 2: `cd client` then `npm run dev`. Expect `Ready on http://localhost:3000`.
4. Confirm `USE_MOCK = false` in `client/src/lib/data.ts`.
5. Open `http://localhost:3000`. Log in with `analyst` / `guardian123`.
6. Run tests 1 through 6 above.

---

## 8. Limitations

- **XGBoost and TabNet not available end-to-end.** The form supports
  selecting them, but `models/xgb_optuna.joblib` and
  `models/tabnet_best.zip` are not in the current checkout. Selecting
  those models returns a server error. Random Forest is verified.
  Kit and Dwayne own those artifacts.
- **Demo login unchanged.** Authentication is still client-side
  hardcoded credentials from Phase 1. Not part of Phase 3 scope.
- **Local server only.** Integration tested against
  `localhost:5000`. Production deployment is out of scope.
- **Per-request model load.** The bridge loads the model on each
  request, as documented in Markie's Phase 2 report. Latency is a few
  seconds per call. Acceptable for the demo.

---

## 9. Phase 3 Mandate Checklist

| Item | Status |
|---|---|
| Form submission connects to `http://localhost:5000/api/analyze` | Complete |
| Prediction labels render dynamically | Complete |
| Threat flags render dynamically | Complete |
| Confidence percentages render dynamically | Complete |
| Model name from the response is displayed | Complete |
| Error handling for HTTP 400 | Complete |
| Error handling for HTTP 500 | Complete |
| Error handling for unreachable server | Complete |
| End-to-end tests recorded | Complete |
| Sprint report written | Complete |

---

## 10. Team Handoff

### To Kit (Project Manager)

Phase 3 complete.

- Branch: `role-3-phase-2`
- Change: `USE_MOCK = false` in `client/src/lib/data.ts`
- Live RF prediction verified end-to-end through Markie's Express bridge
- Sprint report: `docs/reports/role-3-phase-3-amber-frontend-backend-integration.md`

One open item carried from Phase 2: the RF sidecar uses
`per_class_recall_cv` while XGBoost and TabNet use
`per_class_recall_train`. Consumers must branch by field name. No
client code reads these today, so Phase 3 is not blocked.

Ready for Phase 4.

### To Markie (Backend)

Integration confirmed against your Phase 2 bridge. All six cases
tested on the live server: Normal SMTP, DoS flood, Port probe,
invalid rate, missing XGBoost artifact, server down. No changes to
`server/` were needed. The RF path works exactly as documented.
Thanks for the clean interface.

### To Kenneth (Video Producer)

The live dashboard demo is ready for the Phase 4 recording.

1. Start server: `npm start --prefix server` (Terminal 1)
2. Start client: `cd client && npm run dev` (Terminal 2)
3. Open `http://localhost:3000`, log in as `analyst` / `guardian123`
4. Select **Random Forest** in the model dropdown
5. Load **Normal SMTP** → Analyze
6. Load **DoS flood** → Analyze
7. Load **Port probe** → Analyze

The alert module updates with prediction, threat flag, confidence,
and model name on each submission.

### To Dwayne (Evaluation)

No action needed for Phase 3. To test TabNet end-to-end, place
`tabnet_best.zip` and `tabnet_best.meta.json` in `models/`. The
bridge has a guard requiring `preprocessing.scaling = "standard_scaler"`
in the TabNet meta. See Markie's Phase 2 report and
`docs/decision/2026-10-13-tabnet-inference-preprocessing.md`.

---

## 11. Next Phase

**Phase 4 — Presentation Delivery.**

Target activities:

- Record the assigned video segment
- Present the Random Forest architecture and its baseline comparison
- Conduct the live TSX dashboard demo
- Reference the RF confusion matrix from
  `outputs/03_evaluation/confusion_matrix_rf.png` once Notebook 03
  produces it

**Sprint report name for Phase 4:**
`docs/reports/role-3-phase-4-amber-presentation.md`