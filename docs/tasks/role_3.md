# Operational Mandate: Role 3 - Amber
**Title:** Model Developer (Random Forest) & UI / UX Designer

## Phase 1: Frontend TSX Architecture
* **Dependencies:** None. (Can be started concurrently with Data Prep).
* **Target Directory:** `client/` (Next.js/React TSX App Router).
* **Target Files:** `client/src/app/page.tsx`, `client/src/components/*`.
* **Instructions:** 
  1. Navigate to `client/` (`cd client`) and run `npm run dev` to launch the dev server on `http://localhost:3000`.
  2. Design the Security Operations Center (SOC) interactive dashboard using Tailwind CSS.
  3. Build input forms for key network telemetry features (e.g., `src_bytes`, `duration`, `protocol_type`) and an alert module to render threat predictions and confidence meters.

## Phase 2: Random Forest Development
* **Dependencies:** **BLOCKER** - Wait for Kit Dustin to push the cleaned dataset to `data/processed/`.
* **Target Files:** `src/models.py`.
* **Instructions:** Implement the baseline Random Forest classifier. This serves as the primary bagging ensemble comparison against the boosting and deep learning models. Set up the configuration to output feature importances to answer the rubric requirement regarding redundant features.
* **Handoff:** Notify Kenneth when the Random Forest class is ready for integration into the master training script.

## Phase 3: Frontend-Backend Integration
* **Dependencies:** **BLOCKER** - Wait for Markie to start the Node.js Express server (`cd server; node server.js`).
* **Target Files:** `client/src/app/page.tsx`.
* **Instructions:** Connect the TSX dashboard form submission to send an HTTP POST request to `http://localhost:5000/api/analyze`. Dynamically render prediction labels, threat flags, and confidence percentages returned from Markie's Node.js bridge.

## Phase 4: Presentation Delivery
* **Instructions:** Record your assigned video segment. You will present the Random Forest architecture, its baseline performance comparison, and conduct the live demonstration of the TSX UI dashboard.