## Data Ingestion Interface
Input datasets must adhere to the 41-feature KDD network connection format[cite: 3]:

```typescript
interface NetworkPacketRaw {
  duration: number;             // Continuous connection duration[cite: 3]
  protocol_type: string;        // Symbolic (tcp, udp, icmp)[cite: 3]
  service: string;              // Symbolic (http, ftp, smtp, etc.)[cite: 3]
  flag: string;                 // Symbolic connection status (SF, REJ, etc.)[cite: 3]
  src_bytes: number;            // Continuous bytes sent[cite: 3]
  dst_bytes: number;            // Continuous bytes received[cite: 3]
  land: number;                 // Symbolic binary indicator[cite: 3]
  wrong_fragment: number;       // Continuous count[cite: 3]
  urgent: number;               // Continuous count[cite: 3]
  num_failed_logins: number;    // Continuous count[cite: 3]
  logged_in: number;            // Symbolic binary indicator[cite: 3]
  num_compromised: number;      // Continuous count[cite: 3]
  root_shell: number;           // Continuous count[cite: 3]
  su_attempted: number;         // Continuous count[cite: 3]
  num_root: number;             // Continuous count[cite: 3]
  num_file_creations: number;   // Continuous count[cite: 3]
  num_shells: number;           // Continuous count[cite: 3]
  num_access_files: number;     // Continuous count[cite: 3]
  is_host_login: number;        // Symbolic binary indicator[cite: 3]
  is_guest_login: number;       // Symbolic binary indicator[cite: 3]
  // Additional statistical window metrics follow[cite: 3]
}

# Serialization Protocol

All pipeline components are serialized to the models/ folder using strict naming conventions:

- **Transformer Pipeline:** models/transformer_pipeline.joblib (Contains ColumnTransformer, scaling parameters, and frequency mappings).
- **Tree Models:** models/random_forest_v1.joblib, models/xgboost_v1.joblib.
- **TabNet Weights:** models/tabnet_v1.pt and models/tabnet_v1_network.pt.

# Model Inference Schema

Every prediction produces a structured JSON output format:

{
  "prediction": "u2r",
  "confidence": 94.25,
  "is_threat": true,
  "class_probabilities": {
    "normal": 0.12,
    "dos": 0.03,
    "probe": 0.10,
    "r2l": 0.50,
    "u2r": 94.25
  },
  "inference_time_ms": 4.12
}