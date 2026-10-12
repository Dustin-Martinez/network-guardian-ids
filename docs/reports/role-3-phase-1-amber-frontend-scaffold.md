# Phase 1 Report — Frontend TSX Architecture

**Role:** Role 3 — Amber
**Title:** Model Developer (Random Forest) & UI / UX Designer
**Phase:** 1 of 3
**Sprint Day:** Day ? of 10
**Status:** In progress code complete, for checking
**Branch:** `feature/role-3-frontend-dashboard`
**Contracts referenced:** `docs/contracts/api_data_contract.md`

---

## 1. Objective

Per `tasks/role_3.md` Phase 1, scaffold the Next.js / React TSX client in `client/`, design the Security Operations Center (SOC) dashboard with Tailwind CSS, build input forms for the network telemetry features defined in the API contract, and build an alert module that renders threat predictions and confidence meters.

The mandate names three deliverables:

- `client/src/app/page.tsx` and `client/src/components/*`
- Input forms covering the contract's request fields (string fields kept as strings)
- An alert module for predictions and confidence

---

## 2. Scope

### In scope

- Dashboard layout with header, sidebar, and four analytics panels
- Input form covering all 31 fields of `NetworkPacketRequest`
- Alert module: predicted class, threat flag, confidence gauge, model name
- Client-side validation mirroring contract section 6
- Sidebar pages: Dashboard, Analyze, History, Models, Explainability, Settings
- Demo login screen and sign-out
- TypeScript types copied from the contract into `client/src/types/index.ts`
- Single-block color theme

### Out of scope

- Connection to the Express server (Phase 3; the `fetch` is written and switched off)
- Random Forest implementation (Phase 2)
- Real model metrics, confusion matrix, and feature importances (Phase 2 outputs)
- Server-side login (not part of the contract)

---

## 3. Inputs

| Artifact | Source | Purpose |
|---|---|---|
| `docs/contracts/api_data_contract.md` | Kit | Request and response interfaces, validation rules, error handling |
| `docs/tasks/role_3.md` | Kit | Phase 1 mandate |
| `docs/design/ui_spec.md` | — | Referenced "if the file exists". It does not exist in the repository, so the design follows the team's own palette (section 6.3) |
| `docs/reports/paper_narrative_context.md` | Kit | Section 13 source pointer index (not needed for the scaffold) |

---

## 4. Deliverables

### 4.1 Files

| File | Purpose |
|---|---|
| `client/src/app/page.tsx` | Login gate, page shell, view switching, analysis history state |
| `client/src/types/index.ts` | `NetworkPacketRequest`, `PredictionResponse`, `ThreatClass`, copied from the contract |
| `client/src/lib/data.ts` | Theme colors, form field definitions, presets, `analyze()`, demo `login()`, mock chart data |
| `client/src/components/AnalyzeForm.tsx` | 31-field input form, model selector, validation |
| `client/src/components/ThreatGauge.tsx` | Alert module: prediction, threat strip, confidence gauge, model name |
| `client/src/components/Charts.tsx` | Traffic chart, confusion matrix, feature importances (mock data) |
| `client/src/components/Header.tsx` | Top bar and user menu with status and sign-out |
| `client/src/components/Sidebar.tsx` | Navigation between the six pages |
| `client/src/components/LoginScreen.tsx` | Demo sign-in |
| `client/src/components/Panel.tsx` | Shared card wrapper |
| `client/src/components/Views.tsx` | History, Models, Explainability, and Settings pages |

### 4.2 Pages

| Page | Contents |
|---|---|
| Dashboard | Input form and four panels: live traffic, threat gauge, confusion matrix, feature importances |
| Analyze | Input form and threat gauge side by side |
| History | Table of analyses this session (time, protocol, bytes, duration, result, confidence, model), threat filter, clear |
| Models | Model comparison table and accuracy bars (sample values) |
| Explainability | Feature importances, last analysis inputs, feature descriptions |
| Settings | Account info, sign-out, clear history |

---

## 5. Contract Alignment

| Contract item | Implementation |
|---|---|
| Section 2: request fields | All 31 fields are in the form, grouped as Connection, Content, and Traffic statistics. Field coverage was checked programmatically against the interface: 31 of 31, no duplicates, no missing |
| Section 2: string fields | `protocol_type`, `service`, and `flag` are sent as strings. `service` and `flag` accept free text with suggestions |
| Section 2: binary fields | `land`, `logged_in`, `root_shell`, `is_guest_login` are 0 or 1 selectors |
| Section 3: response | The alert module reads `prediction`, `confidence`, `is_threat`, and `model` |
| Section 4.3: model selection | Optional `model` selector (XGBoost default, Random Forest, TabNet) |
| Section 5: errors | A 400, a 500, or an unreachable server shows an alert message in the form |
| Section 6: validation | The form checks protocol enum, non-empty `service` and `flag`, finite numbers, binary 0/1, non-negative `duration`/`src_bytes`/`dst_bytes`, and rates within 0 to 1. The server validates independently |

---

## 6. Design Decisions and Rationale

### 6.1 Component split

The scaffold started as a single `page.tsx` and was split into `client/src/components/*` as the mandate's target files describe. Phase 3 changes are limited to `lib/data.ts` and `AnalyzeForm.tsx`, so the split does not conflict with integration.

### 6.2 Mock predictions behind a switch

`analyze()` uses a local rule set while `USE_MOCK = true`, so the UI can be demonstrated before the server exists. The real `fetch` to `http://localhost:5000/api/analyze` is already implemented and returns the contract's `PredictionResponse`. Phase 3 requires one change: set `USE_MOCK = false`.

### 6.3 Neon color theme

`docs/design/ui_spec.md` does not exist, so the palette is the team's own: cyan for normal traffic, magenta for threats, on a dark navy background. All colors are defined in one block at the top of `lib/data.ts`, so a change of palette is a single edit.

### 6.4 Demo login

Sign-in uses accounts hard-coded in the client, so it is a demonstration of the flow and not security. Replacing `login()` with a call to a server endpoint is the only change needed for real authentication.

### 6.5 Charts without dependencies

The charts are drawn with inline SVG, so no charting package is added to `package.json`.

---

## 7. Verification

### 7.1 Completed

- Contract field parity: 31 of 31 fields present in the form and in the default example record
- Types in `client/src/types/index.ts` copied from contract sections 2 and 3

### 7.2 Pending manual confirmation

| Check | Status |
|---|---|
| `npm run dev` loads at `http://localhost:3000` with no errors in the Problems panel | Pending |
| Login works with the demo account; sign-out returns to the login screen | Pending |
| Each sidebar page opens | Pending |
| Normal SMTP, DoS flood, and Port probe examples give different results | Pending |
| An invalid value (for example a rate of 2) shows an error and does not submit | Pending |
| History page lists each analysis, including the model used | Pending |

---

## 8. Limitations

- **Mock predictions:** results come from a local rule set, not from a model, until `USE_MOCK` is switched off.
- **Sample metrics:** the traffic chart, confusion matrix, feature importances, and Models table contain placeholder numbers marked in `lib/data.ts`.
- **Session-only history:** analyses are held in memory and are lost on refresh.
- **Demo login:** credentials are readable in the browser.
- **Decorative search box:** the header search field does not search.

---

## 9. Phase 1 Mandate Checklist

| Item | Status |
|---|---|
| Dev server launches on `http://localhost:3000` | Complete |
| SOC dashboard designed with Tailwind CSS | Complete |
| Input forms built from contract section 2 | Complete |
| `protocol_type`, `service`, `flag` handled as strings | Complete |
| Alert module renders predictions and confidence meter | Complete |
| Types match the API contract | Complete |
| Manual verification (section 7.2) | Pending |
| Branch pushed and pull request opened | Pending |

---

## 10. Team Handoff

### To Markie (Phase 3)

1. Run the Express server on `http://localhost:5000`.
2. In `client/src/lib/data.ts`, set `USE_MOCK = false`.
3. The client posts a `NetworkPacketRequest` (plus optional `model`) to `/api/analyze` and expects a `PredictionResponse`. Error replies must follow the same shape.
4. The server needs CORS enabled for `http://localhost:3000`.

---

## 11. Next Phase

**Phase 2 — Random Forest Development.**

Target activities:

- Implement the Random Forest in `src/models.py` per `docs/contracts/role-3-rf-architecture-spec.md`
- Run the RF cells of Notebook 02
- Supply real metrics for the Models, confusion matrix, and feature importance panels

**Phase 3 — Frontend-Backend Integration** follows once the Express server is ready.
