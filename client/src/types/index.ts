/**
 * API contract types. These MUST match docs/contracts/api_data_contract.md (v1.0).
 * If the contract changes, update this file in the same pull request.
 */

export interface NetworkPacketRequest {
  // Categorical fields: raw strings, encoded server-side.
  protocol_type: "tcp" | "udp" | "icmp";
  service: string; // e.g. "http", "smtp", "ftp", "telnet"
  flag: string; // e.g. "SF", "S0", "REJ", "RSTR"

  // Continuous and binary numeric fields: raw values.
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

export type ThreatClass = "normal" | "dos" | "probe" | "r2l" | "u2r";

export interface PredictionResponse {
  prediction: ThreatClass;
  confidence: number; // Percentage, 0.00 to 100.00
  is_threat: boolean; // true when prediction !== "normal"
  model: "random_forest" | "xgboost" | "tabnet";
  error?: string;
}

/* Contract section 4.3: the request body may carry an optional `model` (default xgboost). */
export type ModelName = PredictionResponse["model"];
export type AnalyzeRequest = NetworkPacketRequest & { model?: ModelName };
