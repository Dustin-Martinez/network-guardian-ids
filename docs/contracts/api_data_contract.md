This document serves as the strict technical agreement between Amber (Frontend) and Markie (Backend). It guarantees the Next.js UI sends exactly what the Express server expects, and the Node.js API returns exactly what the UI needs to render the dashboard.

---

### File Path: `contracts/api_data_contract.md`

```markdown
# API & Data Contract: Network Guardian IDS

This contract defines the strict data structures, types, and network protocols required for communication between the Next.js TSX Client (Frontend) and the Node.js Express API / Python Bridge (Backend).

---

## 1. Endpoint Specification

* **Protocol:** HTTP POST
* **URL:** `http://localhost:5000/api/analyze`
* **Content-Type:** `application/json`
* **Flow:** Next.js Client ➔ Node.js Server ➔ `predict_bridge.py` ➔ Node.js Server ➔ Next.js Client

---

## 2. Request Payload (Frontend to Backend)

The frontend must send a JSON object containing the network packet features. Because the Python bridge uses `data.values()` to construct the NumPy array, **all expected features must be present in the exact order required by the model**.

### TypeScript Interface (For Amber's TSX Dashboard)
*Save this in `client/src/types/index.ts`*
```typescript
export interface NetworkPacketRequest {
  duration: number;
  protocol_type: number; // e.g., Encoded integer (tcp=1, udp=2, icmp=3)
  service: number;       // e.g., Encoded integer (http, ftp, etc.)
  flag: number;          // e.g., Encoded integer (SF, S0, REJ)
  src_bytes: number;
  dst_bytes: number;
  wrong_fragment: number;
  urgent: number;
  hot: number;
  num_failed_logins: number;
  // ... (Include all 41 KDD features defined in Notebook 01) ...
  dst_host_srv_serror_rate: number;
}

```

### JSON Example Payload (For Markie's API Testing)

```json
{
  "duration": 0,
  "protocol_type": 1,
  "service": 24,
  "flag": 1,
  "src_bytes": 215,
  "dst_bytes": 4503,
  "wrong_fragment": 0,
  "urgent": 0,
  "hot": 0,
  "num_failed_logins": 0,
  "dst_host_srv_serror_rate": 0.0
}

```

---

## 3. Response Payload (Backend to Frontend)

The Express server will parse the standard output (`stdout`) from the Python bridge and return a structured JSON response.

### TypeScript Interface (For Amber's TSX Dashboard)

*Save this in `client/src/types/index.ts*`

```typescript
export interface PredictionResponse {
  prediction: "normal" | "dos" | "probe" | "r2l" | "u2r" | "unknown";
  confidence: number;    // Percentage (0.00 to 100.00)
  is_threat: boolean;    // true if prediction is NOT 'normal'
  error?: string;        // Populated only if an exception occurs in Python/Node
}

```

### JSON Example Response (Success)

```json
{
  "prediction": "dos",
  "confidence": 98.45,
  "is_threat": true
}

```

### JSON Example Response (Error)

```json
{
  "error": "Failed to parse Python model prediction."
}

```

---

## ⚙️ 4. HTTP Status Codes & Error Handling

Both developers must handle the following HTTP status scenarios:

| Status Code | Description | Handler Responsibility |
| --- | --- | --- |
| **200 OK** | Packet analyzed successfully. | **Frontend:** Render prediction UI. |
| **400 Bad Request** | Missing or malformed JSON payload. | **Backend:** Express must validate `req.body` before spawning Python. |
| **500 Internal Error** | Python script crashed or model failed to load. | **Frontend:** Display "Service Unavailable" alert to the user. |

```