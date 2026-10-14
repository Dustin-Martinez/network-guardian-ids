# Handoff — Phase 3 Frontend-Backend Integration

**From:** Amber (Role 3) — Model Developer (Random Forest) & UI / UX Designer
**To:** Kit (Role 1) — Project Manager; Markie (Role 2) — Paper Lead;
Kenneth (Role 4) — Video Producer; Dwayne (Role 5) — Evaluation Engineer
**Date:** 2026-10-15
**Status:** Complete — pending push to `role-3-phase-2`
**Related:** `docs/contracts/api_data_contract.md`,
`docs/reports/role-3-phase-3-amber-frontend-backend-integration.md`,
`docs/reports/role-2-phase-2-markie-backend-bridge.md`,
`docs/handoffs/ui_usage_guide.md`.

---

## 1. Purpose

This document records the completion of the Phase 3 frontend-backend
integration. Before this work, the dashboard's threat gauge was driven
by a local mock predictor inside `client/src/lib/data.ts`. After this
work, the threat gauge submits to Markie's Express backend at
`POST /api/analyze`, which spawns `predict_bridge.py`, loads the
selected model, and returns a real prediction.

The integration uses Random Forest for the demo because it is the only
model artifact currently committed on the branch. XGBoost and TabNet
paths in the bridge are ready but require their artifacts to be present
in `models/`.

---

## 2. What Changed

### Modified

| File | Change |
|---|---|
| `client/src/lib/data.ts` | `USE_MOCK` switched from `true` to `false` |

### Confirmed unchanged

| File | Reason |
|---|---|
| `client/src/types/index.ts` | Already matched `api_data_contract.md` v1.0 exactly |
| `client/src/components/AnalyzeForm.tsx` | Already built the correct payload and surfaced backend errors |
| `client/src/app/page.tsx` | Already hosted the form and routed results to the alert module |

### Added

| File | Purpose |
|---|---|
| `docs/reports/role-3-phase-3-amber-frontend-backend-integration.md` | Full phase report |

The Phase 3 code change is a single line. Everything else required no
edits because the Phase 1 scaffold was built against the contract.

---

## 3. Integration Summary

| Layer | Implementation |
|---|---|
| Endpoint | `POST http://localhost:5000/api/analyze` |
| Content-Type | `application/json` |
| Request | `NetworkPacketRequest` plus optional `model` |
| Response | `PredictionResponse` with `prediction`, `confidence`, `is_threat`, `model` |
| Error envelope | HTTP 400 and 500 return default fields plus `error` string |
| Client mock | Disabled |

---

## 4. Data Flow
AnalyzeForm (client)
↓ builds NetworkPacketRequest from form values
analyze() in client/src/lib/data.ts
↓ POST to http://localhost:5000/api/analyze
server.js (Express)
↓ validates, spawns predict_bridge.py
predict_bridge.py
↓ loads models/<selected>.joblib, applies frozen encoders
↓ returns JSON prediction to stdout
server.js
↓ returns PredictionResponse to the client
AnalyzeForm
↓ routes result to ThreatGauge
ThreatGauge renders prediction, threat flag, confidence, model


The client reads the same fields the contract defines. No transformation
happens on the client beyond form-string to number conversion, which
already existed in Phase 1.

---

## 5. Verification Summary

Full reproduction steps are in section 7 of the phase report. Summary:

| Test | Expectation |
|---|---|
| Normal SMTP, Random Forest | `normal`, threat off |
| DoS flood, Random Forest | `dos`, threat on |
| Port probe, Random Forest | `probe`, threat on |
| Invalid rate field | Client-side validation error, no HTTP request sent |
| XGBoost selected | Server error — artifact not present |
| Express server stopped | "Service unavailable" surfaced in the form |

---

## 6. Handoff Actions

### 6.1 To Kit (Role 1) — Project Manager

Phase 3 is complete on `role-3-phase-2`. The only client change is
`USE_MOCK = false`.

One open item carried from Phase 2 that affects downstream consumers:
the RF sidecar uses `per_class_recall_cv` while XGBoost and TabNet use
`per_class_recall_train`. These fields measure different quantities.
Notebook 03 and the paper's comparison table should branch by field
name, or the schema should be unified. No client code reads these
fields today, so the live demo is unaffected.

### 6.2 To Markie (Role 2) — Paper Lead

Integration confirmed against your Phase 2 backend bridge. All six
end-to-end cases ran against the live Express server on port 5000.
No changes to `server/` were needed.

The response envelope handling in `client/src/lib/data.ts` matches
the shape documented in your Phase 2 report: the client reads
`body.error` even on a 200, in case the backend returns an error
envelope with a success status.

### 6.3 To Kenneth (Role 4) — Video Producer

The dashboard is ready for the Phase 4 recording. Recording steps:

1. Terminal 1: `npm start --prefix server`. Expect `running on port 5000`.
2. Terminal 2: `cd client && npm run dev`. Expect `Ready on http://localhost:3000`.
3. Open `http://localhost:3000`, log in as `analyst` / `guardian123`.
4. Select **Random Forest** in the model dropdown.
5. Load **Normal SMTP session** → Analyze.
6. Load **DoS flood** → Analyze.
7. Load **Port probe** → Analyze.

The alert module updates with prediction, threat flag, confidence, and
model name on each submission. The threat gauge color changes from
cyan (normal) to pink (threat) between steps 5 and 6.

### 6.4 To Dwayne (Role 5) — Evaluation Engineer

No action needed for Phase 3. If you want to test TabNet end-to-end,
place `tabnet_best.zip` and `tabnet_best.meta.json` in `models/`. The
bridge has a guard requiring `preprocessing.scaling = "standard_scaler"`
in the TabNet meta sidecar. See Markie's Phase 2 report and
`docs/decision/2026-10-13-tabnet-inference-preprocessing.md`.

XGBoost end-to-end testing is blocked on the same missing artifact. The
bridge path is ready; only the file is absent.

---

## 7. Known Issues and Constraints

### 7.1 XGBoost and TabNet artifacts absent

The form dropdown offers all three models, but only Random Forest has
its artifact committed to the branch. Selecting XGBoost or TabNet
returns a server error from the bridge. This is expected and is not a
Phase 3 defect — the artifacts belong to Kit and Dwayne.

### 7.2 Cross-model sidecar schema inconsistency

The RF sidecar uses `per_class_recall_cv`; XGBoost and TabNet use
`per_class_recall_train`. These measure different quantities on
different data. The paper's comparison table must branch by field
name or Kit must unify the schema.

### 7.3 Demo login remains client-side

Authentication is still the Phase 1 hardcoded credential list. Not
part of Phase 3 scope. Replacing it with a server endpoint is a
future consideration.

### 7.4 Local server only

Integration tested against `localhost:5000` and `localhost:3000`.
Production deployment is out of scope for this prototype.

---

## 8. Cross-References

| Document | Purpose |
|---|---|
| `docs/contracts/api_data_contract.md` | Payload and response contract |
| `docs/reports/role-3-phase-3-amber-frontend-backend-integration.md` | Full Phase 3 sprint report |
| `docs/reports/role-2-phase-2-markie-backend-bridge.md` | Backend bridge implementation |
| `docs/contracts/artifact_transfer_policy.md` | Artifact transfer rules |
| `docs/handoffs/ui_usage_guide.md` | Dashboard user guide |
| `docs/handoffs/ui_content.md` | Panel data provenance |
| `docs/handoffs/xgboost.md` | XGBoost handoff (artifact pending) |

---

## 9. Confirmation

The Phase 3 frontend-backend integration is complete. The client posts
to the live Express endpoint. Random Forest predictions are verified
end-to-end. The phase report is written. The `USE_MOCK` switch is
disabled on the branch.

Phase 3 of Role 3 is closed.

---

**Signed off by:** Amber (Role 3) — Model Developer (Random Forest) & UI / UX Designer
**Date:** 2026-10-15