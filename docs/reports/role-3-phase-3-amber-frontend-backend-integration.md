# Phase 3 Report — Frontend-Backend Integration

**Role:** Role 3 — Amber
**Title:** Model Developer (Random Forest) & UI / UX Designer
**Phase:** 3 of 4
**Sprint Day:** Day 9 of 10
**Status:** Complete
**Branch:** `role-3-phase-2`
**Contracts referenced:** `docs/contracts/api_data_contract.md`
**Backend reference:** `docs/reports/role-2-phase-2-markie-backend-bridge.md`

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
- Verify the response is rendered per section 3
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

| Item | Location |
|---|---|
| Mock switch disabled | `client/src/lib/data.ts` (`USE_MOCK = false`) |
| Sprint report | `docs/reports/role-3-phase-3-amber-frontend-backend-integration.md` |

No changes to `client/src/types/index.ts` were required. It already
matched the API contract v1.0 exactly.

No changes to `client/src/components/AnalyzeForm.tsx` were required.
It already built the payload with string categoricals, numeric
fields, and the selected model; it already routed responses to the
alert module and displayed errors from rejected promises.

No changes to `client/src/app/page.tsx` were required. It already
hosted the form and the alert module.

---

## 5. Integration Verified

### 5.1 Endpoint

- Method: `POST`
- URL: `http://localhost:5000/api/analyze`
- Content-Type: `application/json`

### 5.2 Request payload

The client sends `NetworkPacketRequest` plus the optional `model`
field. All 31 contract fields are present. Categorical fields
(`protocol_type`, `service`, `flag`) are sent as raw strings, not
encoded integers.

### 5.3 Response payload

The client reads `prediction`, `confidence`, `is_threat`, and
`model` from the response. On error, it reads the `error` string.

### 5.4 Error envelope

Both HTTP 400 and HTTP 500 return a full `PredictionResponse` with
default values plus an `error` string. The client surfaces this in
the form's alert area.

### 5.5 What actually changed

Phase 3 required exactly one line of code in the client:

```diff
- const USE_MOCK = true;
+ const USE_MOCK = false;