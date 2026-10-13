# Role 2 Phase 2 Report: Backend Bridge and Frontend Handoff

**Owner:** Markie (Role 2)
**Date:** 2026-10-13 (Asia/Manila)
**Branch:** `feature/role-2-backend-bridge`
**Status:** Backend implemented and real RF inference verified; XGBoost artifact handoff and TabNet preprocessing confirmation pending.
**Contract:** `docs/contracts/api_data_contract.md`
**Related mandate:** `docs/tasks/role_2.md`, Phase 2

## 1. Problem and implemented behavior

The previous server accepted unchecked requests, relied on JSON key order, loaded a noncontractual model filename, and did not handle Python startup or exit failures. The bridge now validates all 31 raw fields, applies the saved encoders and log transformations, orders the 43 engineered features from the frozen manifest, loads the selected model and its metadata, and returns a validated PredictionResponse. Failures return structured HTTP 400 or 500 responses rather than fabricated successful predictions.

## 2. Delivered files

- `server/server.js`: Express route, local frontend CORS, JSON parsing, Python subprocess lifecycle, timeout, bounded output, and response validation.
- `server/validate.js`: all required numeric, categorical, binary, non-negative, rate and model-selection rules.
- `server/predict_bridge.py`: root-independent paths, frozen encoder reuse, feature ordering, model/metadata checks, class-aware probability decoding, JSON-only stdout, stderr diagnostics.
- `server/examples/normal-smtp.json`: complete raw request example.
- `server/tests/api.test.js`: HTTP and subprocess failure checks.
- `server/tests/test_bridge.py`: feature assembly, unknown-category behavior, shuffled class decoding, metadata rejection and TabNet guard checks.
- `server/README.md`: setup, startup, request, test and frontend integration instructions.

The four Phase 1 documentation reports are included in this feature branch so Amber and Kit can access the previously local work.

## 3. HTTP interface

POST `http://localhost:5000/api/analyze`, Content-Type `application/json`.

Optional `model`: `random_forest`, `xgboost` (default), or `tabnet`. Supply the 31 raw fields from the API contract; categorical fields are strings. Never send an encoded feature array.

Success: HTTP 200 with `prediction`, `confidence` (0-100 percentage), `is_threat`, and `model`. Error: HTTP 400 for invalid requests or HTTP 500 for bridge/model failures, with default values and an `error` string. The frontend must check both the HTTP status and `error`; default `normal` in an error envelope is not a prediction.

The contract's opening response paragraph says to omit prediction on errors, while its example, interface and status table specify defaults. This implementation follows the more specific default-field envelope already handled by Amber's client.

## 4. Artifact requirements and model readiness

Common preprocessing: `data/processed/feature_names.json`, `class_order.json`, `encoder_service.pkl`, `encoder_onehot_protocol_flag.pkl`. Generate using the corrected Notebook 01, following `docs/SETUP.md`.

| Model | Files in local models directory | Validation status |
|---|---|---|
| Random Forest | `rf_baseline.joblib`, `rf_baseline.meta.json` | Real HTTP inference tested using Amber's open PR #13 artifact at branch `role-3-phase-2`, commit `3706260` |
| XGBoost | `xgb_optuna.joblib`, `xgb_optuna.meta.json` | Supported bridge path; unavailable locally, so no real-model claim |
| TabNet | `tabnet_best.zip`, `tabnet_best.meta.json`, plus `scaler_tabnet.pkl` | Guarded until Kit confirms training/inference preprocessing |

Amber's model was brought into this local checkout only for integration verification. Its model files were not recommitted in Markie's backend change and are not included in the PR. This does not imply Kit has accepted the RF training results.

Model metadata must match the canonical class order and exact feature_names.json ordering. The bridge maps probability columns using the actual model.classes_ ordering rather than assuming the argmax index equals a family ID. It does not evaluate test-set performance.

## 5. TabNet decision required

The API contract names a `.pt` file, while the specific TabNet execution contract and actual trainer save a native `.zip`. The bridge follows the specific model contract and loads `tabnet_best.zip` through TabNetClassifier.load_model.

A more important inconsistency remains: the API contract requires StandardScaler at TabNet inference, but the current trainer consumes unscaled engineered arrays. Applying the scaler to the current model would change its input distribution. The bridge deliberately returns an error until a handoff explicitly confirms scaler-trained preprocessing in metadata as `preprocessing.scaling = standard_scaler`. This additional field is a proposed readiness assertion, not an existing metadata contract requirement. Do not add it merely to bypass the guard: it must describe the actual training inputs, and its adoption requires Kit's decision.

See `docs/decision/2026-10-13-tabnet-inference-preprocessing.md`. No trainer, frozen encoder, model metadata, or API contract was silently edited. RF and XGBoost operation is independent of this question.

## 6. Verification performed

- `npm test` in server: **10 tests passed**.
- `.venv/Scripts/python.exe -m unittest discover -s server/tests -p test_bridge.py -v`: **3 tests passed**.
- Real RF request through Express to the Python subprocess returned HTTP 200: `prediction=normal`, `confidence=81.31`, `is_threat=false`, `model=random_forest` for the SMTP example.
- Reversed JSON key order produced the same response.
- Localhost frontend CORS header checked.
- Actual missing-model path returned HTTP 500 with an error envelope.
- No new training, test-set scoring, confusion matrices, or SHAP calculations were performed.

The example response is an integration smoke check, not an accuracy estimate or model evaluation result. Process fixtures are used only in automated failure-path tests; the real API never substitutes them for missing models.

## 7. Handoff to Amber

1. Review this PR and obtain the backend branch. Preserve your existing client work; merge the reviewed backend changes rather than resetting your branch.
2. Complete corrected Notebook 01 and ensure the selected model plus metadata exists locally. For the immediate demo, select Random Forest; default XGBoost returns a useful error until its artifact arrives.
3. Run `npm ci --prefix server`, then `npm start --prefix server` from the repository root.
4. In your frontend integration phase, set `USE_MOCK = false` in `client/src/lib/data.ts`. The API_URL already points to the correct route. This backend change does not edit Amber's client files.
5. Submit all 31 raw fields and select `random_forest`. Check the model label, prediction, confidence and threat indicator.
6. Test an invalid input and an unavailable model. The client must display the returned error, not a safe traffic result.
7. Report end-to-end UI validation before calling frontend integration complete.

## 8. Limitations and next steps

Per-request subprocess/model loading incurs latency and memory cost. The bridge runs on localhost, with a 60-second timeout and a 32 KB request limit. This is a course prototype, not a deployed streaming IDS. Confidence is a model probability, not a calibrated certainty guarantee.

Await Kenneth's XGBoost artifacts and Kit's TabNet preprocessing decision. Keep final paper metrics distinct from this backend smoke test. The existing Word manuscript remains an editable local draft; it is not part of this code handoff.

## AI assistance disclosure

Codex assisted with the implementation, source review, tests, report and integration checks. Markie and the team should review the branch and confirm the artifact/preprocessing decisions before merging to main.
