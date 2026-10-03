# API & Data Contract: Network Guardian IDS

This document defines the strict interface between the Next.js TSX client
and the Node.js Express backend, including the payload schema passed to
the Python inference bridge. It is the authoritative agreement between
Amber (frontend) and Markie (backend, bridge). Any change to field names,
types, or ordering requires an update to this file and a corresponding
change in `client/src/types/index.ts` and `server/predict_bridge.py`.

---

## 1. Endpoint Specification

- Protocol: HTTP POST
- URL: `http://localhost:5000/api/analyze`
- Content-Type: `application/json`
- Flow: Next.js client → Node.js Express → `predict_bridge.py` → Node.js Express → Next.js client

The Express server spawns `predict_bridge.py` as a subprocess via
`child_process.spawn()` and reads the prediction from the script's stdout.
No HTTP listener runs on the Python side.

---

## 2. Request Payload — Client to Server

The client sends a single network packet as a JSON object. Every field
carries the raw value from the KDD Cup 1999 feature space, not an
encoded integer. Encoding occurs exclusively inside the Python bridge
using the frozen encoder artifacts in `data/processed/`.

### TypeScript Interface — `client/src/types/index.ts`

```typescript
export interface NetworkPacketRequest {
  // Categorical fields — raw strings, encoded server-side.
  protocol_type: "tcp" | "udp" | "icmp";
  service: string;   // e.g. "http", "smtp", "ftp", "telnet"
  flag: string;      // e.g. "SF", "S0", "REJ", "RSTR"

  // Continuous and binary numeric fields — raw values.
  duration: number;
  src_bytes: number;
  dst_bytes: number;
  land: 0 | 1;
  wrong_fragment: number;
  urgent: number;
  hot: number;
  num_failed_logins: number;
  logged_in: 0 | 1;
  root_shell: 0 | 1;
  su_attempted: number;
  num_root: number;
  num_file_creations: number;
  num_shells: number;
  num_access_files: number;
  is_guest_login: 0 | 1;

  // Traffic statistics.
  count: number;
  srv_count: number;
  same_srv_rate: number;
  diff_srv_rate: number;
  srv_diff_host_rate: number;
  dst_host_count: number;
  dst_host_same_srv_rate: number;
  dst_host_diff_srv_rate: number;
  dst_host_same_src_port_rate: number;
  dst_host_srv_diff_host_rate: number;
  dst_host_srv_serror_rate: number;
  dst_host_srv_rerror_rate: number;
}
```

### JSON Example — Representative Normal SMTP Session

```json
{
  "protocol_type": "tcp",
  "service": "smtp",
  "flag": "SF",
  "duration": 0,
  "src_bytes": 215,
  "dst_bytes": 4503,
  "land": 0,
  "wrong_fragment": 0,
  "urgent": 0,
  "hot": 0,
  "num_failed_logins": 0,
  "logged_in": 1,
  "root_shell": 0,
  "su_attempted": 0,
  "num_root": 0,
  "num_file_creations": 0,
  "num_shells": 0,
  "num_access_files": 0,
  "is_guest_login": 0,
  "count": 1,
  "srv_count": 1,
  "same_srv_rate": 1.0,
  "diff_srv_rate": 0.0,
  "srv_diff_host_rate": 0.0,
  "dst_host_count": 1,
  "dst_host_same_srv_rate": 1.0,
  "dst_host_diff_srv_rate": 0.0,
  "dst_host_same_src_port_rate": 1.0,
  "dst_host_srv_diff_host_rate": 0.0,
  "dst_host_srv_serror_rate": 0.0,
  "dst_host_srv_rerror_rate": 0.0
}
```

---

## 3. Response Payload — Server to Client

The Express server returns a structured JSON object. On success, the
prediction field is one of the five canonical classes. On error, the
error field is populated and the prediction field is omitted.

### TypeScript Interface — `client/src/types/index.ts`

```typescript
export type ThreatClass = "normal" | "dos" | "probe" | "r2l" | "u2r";

export interface PredictionResponse {
  prediction: ThreatClass;
  confidence: number;   // Percentage in the range 0.00 to 100.00
  is_threat: boolean;   // true when prediction !== "normal"
  model: "random_forest" | "xgboost" | "tabnet";
  error?: string;
}
```

### JSON Example — Successful Prediction

```json
{
  "prediction": "dos",
  "confidence": 98.45,
  "is_threat": true,
  "model": "xgboost"
}
```

### JSON Example — Error Response

```json
{
  "prediction": "normal",
  "confidence": 0.0,
  "is_threat": false,
  "model": "xgboost",
  "error": "Failed to parse Python model prediction."
}
```

On error, `prediction`, `confidence`, and `is_threat` are set to safe
defaults so the client can render without null checks. The `error`
field signals the failure.

---

## 4. Server-Side Feature Assembly — Bridge Contract

The Python bridge reconstructs the exact 43-column feature vector
consumed by the trained models. This section documents the
transformation so that no ambiguity exists between client input and
model input.

### 4.1 Artifacts Loaded at Startup

The bridge loads the following files from `data/processed/`:

| Artifact | Purpose |
|---|---|
| `feature_names.json` | Authoritative feature ordering after encoding |
| `encoder_service.pkl` | Frequency encoder for the `service` column |
| `encoder_onehot_protocol_flag.pkl` | One-hot encoder for `protocol_type` and `flag` |
| `scaler_tabnet.pkl` | StandardScaler used only when serving the TabNet model |
| `class_order.json` | Integer-to-class-name mapping used to decode predictions |

Model binaries are loaded from `models/`:

| Artifact | Model |
|---|---|
| `rf_baseline.joblib` | Random Forest |
| `xgb_optuna.joblib` | XGBoost |
| `tabnet_best.pt` | PyTorch TabNet |

If any required artifact is missing, the bridge must exit with a
non-zero status and a diagnostic message on stderr. The Express
server translates a non-zero exit into an HTTP 500 response.

### 4.2 Transformation Pipeline

Given a `NetworkPacketRequest`, the bridge performs these steps in order:

1. Load the request JSON from stdin.
2. Construct a single-row pandas DataFrame with columns matching the
   raw KDD schema used during Phase 2 data preparation.
3. Apply `log1p` to the columns `duration`, `src_bytes`, and `dst_bytes`.
4. Apply `encoder_service.pkl` to produce the `service_freq` column.
5. Apply `encoder_onehot_protocol_flag.pkl` to produce the
   `protocol_type_*` and `flag_*` columns.
6. Reorder columns to the exact ordering in `feature_names.json`.
7. For Random Forest and XGBoost: pass the DataFrame directly to
   `model.predict_proba`.
8. For TabNet: apply `scaler_tabnet.pkl`, then call the model.
9. Map the argmax index back to a class name via `class_order.json`.
10. Emit the response JSON to stdout and exit with status 0.

### 4.3 Model Selection

The bridge accepts an optional `model` field in the request body. If
absent, the bridge defaults to `xgboost`. Valid values are
`random_forest`, `xgboost`, and `tabnet`. An invalid value returns
HTTP 400.

---

## 5. HTTP Status Codes and Error Handling

| Status | Condition | Response Body | Handler Responsibility |
|---|---|---|---|
| 200 OK | Prediction produced successfully | `PredictionResponse` with `prediction`, `confidence`, `is_threat`, `model` | Frontend renders the prediction UI |
| 400 Bad Request | Request body is missing required fields, contains an unknown `model` value, or fails schema validation | `PredictionResponse` with default fields and an `error` string | Backend validates `req.body` before spawning Python |
| 500 Internal Server Error | Python bridge crashed, model artifact missing, or prediction could not be parsed | `PredictionResponse` with default fields and an `error` string | Frontend displays a service unavailable alert |

The server never returns a bare error string. All error responses
conform to the `PredictionResponse` interface so that the frontend can
render consistently.

---

## 6. Validation Rules

The Node.js server validates the incoming request before spawning
Python. The following rules are enforced; a violation returns HTTP 400.

- `protocol_type` must be one of `"tcp"`, `"udp"`, or `"icmp"`.
- `service` and `flag` must be non-empty strings.
- All numeric fields must be present and finite.
- Binary fields (`land`, `logged_in`, `root_shell`, `is_guest_login`)
  must be 0 or 1.
- `duration`, `src_bytes`, and `dst_bytes` must be non-negative.
- Rate fields (`same_srv_rate`, `diff_srv_rate`, `serror_rate` family,
  `rerror_rate` family) must lie in the closed interval `[0.0, 1.0]`.

Validation is implemented in `server/validate.js` and imported by
`server.js`. The bridge assumes validated input and does not re-validate.

---

## 7. Versioning

This contract is version 1.0, frozen at the start of Phase 3. Any
change to field names, types, ordering, or endpoint semantics requires:

1. A pull request that updates this file.
2. A corresponding update to `client/src/types/index.ts`.
3. A corresponding update to `server/validate.js` and `server.js`.
4. A corresponding update to `server/predict_bridge.py`.
5. A note in `reports/` describing the change and its rationale.

No silent divergence is permitted between this file and the running
system. If the code and the contract disagree, the contract is
authoritative until the code is changed to match it, or the contract
is explicitly revised by the team.
```

---

## What Changed and Why

| Section | Previous state | New state | Reason |
|---|---|---|---|
| TypeScript `NetworkPacketRequest` | `protocol_type: number`, `service: number`, `flag: number` | All three are strings | Encoders fit in Phase 2 expect raw categorical values |
| JSON request example | Fabricated integers (`"service": 24`) | Realistic raw KDD record | Removes ambiguity about what the frontend sends |
| Response interface | 3 fields | 5 fields, added `model` | Client can display which model produced the prediction |
| Error response | Only `error` field | Full `PredictionResponse` with defaults | Frontend can render without null checks |
| New section 4 | None | Bridge contract — artifacts, transformation, model selection | Markie has no guesswork; the exact pipeline is documented |
| New section 6 | None | Validation rules | Prevents malformed payloads from reaching Python |
| New section 7 | None | Versioning policy | Prevents silent drift between contract and code |

---

## Team Coordination Required

Two follow-ups so the contract is honored:

### 1. Amber — update `client/src/types/index.ts`

The interface in the file must match section 2 of the contract. Amber should replace the existing `NetworkPacketRequest` with the version above. She also needs to adjust the form inputs: `protocol_type`, `service`, and `flag` become dropdowns or text inputs of strings, not integer fields.

### 2. Markie — align `server/predict_bridge.py` and `server/validate.js`

Markie's bridge must implement the transformation documented in section 4. If his current draft assumes pre-encoded integers, it needs revision. His validator must implement the rules in section 6.

### 3. Kenneth — nothing

The contract does not affect the training loop or video production.

---

## What to Do Now

1. Save the file contents above as `contracts/api_data_contract.md` (overwrite the existing version).
2. Commit and push:

```bash
git add contracts/api_data_contract.md
git commit -m "docs(contracts): align API contract with Phase 2 encoding scheme"
git push
```
