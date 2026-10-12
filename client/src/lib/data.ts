import type { CSSProperties } from "react";
import type { AnalyzeRequest, ModelName, NetworkPacketRequest, PredictionResponse, ThreatClass } from "@/types";

/* ============================================================
   EDIT COLORS HERE
   Change any hex value below and the whole site updates.
   ============================================================ */
export const THEME = {
  "--bg": "#0a0c16",          // page background
  "--panel": "#11152280",     // cards and sidebar (last 2 digits = transparency)
  "--field": "#0a0c16",       // inputs
  "--line": "#2a2f4a",        // borders and grid lines
  "--text": "#eceffa",        // main text
  "--muted": "#9aa0bd",       // secondary text
  "--safe": "#22e5f0",        // normal traffic: cyan lines, bars, buttons
  "--safe-hover": "#6af0f7",  // button hover
  "--threat": "#ff3fa4",      // threats: pink lines, gauge, alerts
  "--threat-bg": "#2a0f21",   // alert strip background on a threat
  "--threat-soft": "#ff8cc8", // error message text
} as CSSProperties;

/* ---------- app types (API types live in @/types) ---------- */
export type Prediction = PredictionResponse & { at: string; input: NetworkPacketRequest };
export type Session = { name: string; role: string };
export type View = "dashboard" | "analyze" | "history" | "models" | "explain" | "settings";
export const CLASS_LABEL: Record<ThreatClass, string> = { normal: "Normal", dos: "DoS", probe: "Probe", r2l: "R2L", u2r: "U2R" };

/* ---------- navigation + status ---------- */
export const NAV: { id: View; name: string; icon: string }[] = [
  { id: "dashboard", name: "Dashboard", icon: "▦" },
  { id: "analyze", name: "Analyze", icon: "◎" },
  { id: "history", name: "History", icon: "↺" },
  { id: "models", name: "Models", icon: "⛁" },
  { id: "explain", name: "Explainability", icon: "✦" },
];
export const STATUSES = [
  { id: "online", label: "Online", color: "var(--safe)" },
  { id: "away", label: "Away", color: "#ffb020" },
  { id: "busy", label: "Do not disturb", color: "var(--threat)" },
];

/* ============================================================
   MOCK DATA (Phase 1 only). Replace with real results later:
   - traffic: live counts from the backend (Phase 3)
   - matrix, features, models: Random Forest evaluation (Phase 2)
   ============================================================ */
export const TRAFFIC_NORMAL = [20, 60, 100, 75, 55, 120, 170, 90, 60, 100, 110, 110, 108];
export const TRAFFIC_DOS = [22, 40, 60, 50, 40, 70, 95, 130, 120, 95, 85, 110, 160];
export const CLASSES = ["normal", "dos", "probe", "r2l", "u2r"];
export const MATRIX = [
  [0.95, 0.03, 0.01, 0.01, 0.0],
  [0.02, 0.96, 0.01, 0.01, 0.0],
  [0.02, 0.08, 0.85, 0.03, 0.02],
  [0.05, 0.02, 0.03, 0.88, 0.02],
  [0.1, 0.02, 0.03, 0.05, 0.8],
];
export const FEATURES = [
  { name: "src_bytes", value: 265 },
  { name: "dst_bytes", value: 220 },
  { name: "count", value: 155 },
  { name: "same_srv_rate", value: 100 },
  { name: "service_freq", value: 55 },
];
export const FEATURE_HELP: Record<string, string> = {
  src_bytes: "Bytes sent from the source. Floods and large transfers often show unusual values.",
  dst_bytes: "Bytes sent back from the destination. Very low replies can mean the target is overwhelmed.",
  count: "Connections to the same host in a short window. High counts point to scanning or DoS.",
  same_srv_rate: "Share of those connections that hit the same service. High values suggest a targeted attack.",
  service_freq: "How often the requested service is used on this network.",
  duration: "Length of the connection in seconds. Many very short connections can signal DoS.",
  protocol_type: "tcp, udp or icmp. ICMP floods are a common DoS pattern.",
};
// SAMPLE VALUES until Phase 2 produces real metrics
export const MODELS = [
  { name: "Random Forest", kind: "Bagging ensemble", accuracy: 99.1, precision: 98.8, recall: 98.9, f1: 98.8 },
  { name: "Gradient Boosting", kind: "Boosting ensemble", accuracy: 99.3, precision: 99.0, recall: 99.1, f1: 99.0 },
  { name: "Neural Network", kind: "Deep learning", accuracy: 98.7, precision: 98.2, recall: 98.4, f1: 98.3 },
];

/* ============================================================
   ANALYZE. Contract: docs/contracts/api_data_contract.md
   PHASE 3: set USE_MOCK to false once Markie's server is running on port 5000.
   ============================================================ */
const API_URL = "http://localhost:5000/api/analyze";
const USE_MOCK = true;

function mockPredict(p: NetworkPacketRequest): Pick<PredictionResponse, "prediction" | "confidence"> {
  if (p.flag === "S0" && p.count >= 200) return { prediction: "dos", confidence: 98.4 };
  if (p.diff_srv_rate >= 0.5 || (p.flag === "REJ" && p.count >= 50)) return { prediction: "probe", confidence: 91.7 };
  if (p.num_failed_logins >= 3) return { prediction: "r2l", confidence: 84.2 };
  if (p.root_shell === 1) return { prediction: "u2r", confidence: 79.5 };
  return { prediction: "normal", confidence: 97.3 };
}

export async function analyze(req: AnalyzeRequest): Promise<Prediction> {
  const { model, ...packet } = req;
  const at = new Date().toLocaleTimeString();
  const chosen: ModelName = model ?? "xgboost";

  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 400));
    const m = mockPredict(packet);
    return { ...m, is_threat: m.prediction !== "normal", model: chosen, at, input: packet };
  }

  let res: Response;
  try {
    res = await fetch(API_URL, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(req) });
  } catch {
    throw new Error("Service unavailable. Check that the server is running on port 5000.");
  }
  const body: PredictionResponse | null = await res.json().catch(() => null);
  if (!body) throw new Error("Service unavailable. The server sent an unreadable reply.");
  if (!res.ok || body.error) throw new Error(body.error ?? "Service unavailable.");
  return { ...body, at, input: packet };
}

/* ============================================================
   LOGIN (Phase 1 demo). These accounts are readable in the browser,
   so this is NOT real security.
   PHASE 3: replace login() with a POST to your Node server
   (e.g. http://localhost:5000/api/login) that returns { name, role }.
   ============================================================ */
const DEMO_USERS = [
  { username: "analyst", password: "guardian123", name: "Analyst", role: "SOC analyst" },
  { username: "admin", password: "admin123", name: "Admin", role: "Administrator" },
];
export async function login(username: string, password: string): Promise<Session> {
  await new Promise((r) => setTimeout(r, 400));
  const u = DEMO_USERS.find((d) => d.username === username.trim().toLowerCase() && d.password === password);
  if (!u) throw new Error("Invalid login");
  return { name: u.name, role: u.role };
}

/* ============================================================
   FORM FIELDS: one entry per field in NetworkPacketRequest.
   kind: select | text | number | binary (0/1) | rate (0.0 to 1.0)
   ============================================================ */
export type FieldKind = "select" | "text" | "number" | "binary" | "rate";
export type FieldName = keyof NetworkPacketRequest;
export type FormValues = Record<FieldName, string>;
export type FieldDef = { name: FieldName; kind: FieldKind };
const f = (kind: FieldKind, ...names: FieldName[]): FieldDef[] => names.map((name) => ({ name, kind }));

export const FIELD_GROUPS: { title: string; open: boolean; fields: FieldDef[] }[] = [
  {
    title: "Connection",
    open: true,
    fields: [
      ...f("select", "protocol_type"),
      ...f("text", "service", "flag"),
      ...f("number", "duration", "src_bytes", "dst_bytes"),
    ],
  },
  {
    title: "Content",
    open: false,
    fields: [
      ...f("binary", "land", "logged_in", "root_shell", "is_guest_login"),
      ...f("number", "wrong_fragment", "urgent", "hot", "num_failed_logins", "su_attempted", "num_root", "num_file_creations", "num_shells", "num_access_files"),
    ],
  },
  {
    title: "Traffic statistics",
    open: false,
    fields: [
      ...f("number", "count", "srv_count", "dst_host_count"),
      ...f("rate", "same_srv_rate", "diff_srv_rate", "srv_diff_host_rate", "dst_host_same_srv_rate", "dst_host_diff_srv_rate",
        "dst_host_same_src_port_rate", "dst_host_srv_diff_host_rate", "dst_host_srv_serror_rate", "dst_host_srv_rerror_rate"),
    ],
  },
];
export const SERVICES = ["http", "smtp", "ftp", "ftp_data", "telnet", "domain_u", "private", "ecr_i", "eco_i", "auth", "finger", "pop_3", "ssh", "other"];
export const FLAGS = ["SF", "S0", "S1", "S2", "S3", "REJ", "RSTO", "RSTR", "RSTOS0", "SH", "OTH"];
export const MODEL_OPTIONS: { id: ModelName; label: string }[] = [
  { id: "xgboost", label: "XGBoost" },
  { id: "random_forest", label: "Random Forest" },
  { id: "tabnet", label: "TabNet" },
];

// Normal SMTP session: the example record from the contract
export const NORMAL_PRESET: FormValues = {
  protocol_type: "tcp", service: "smtp", flag: "SF", duration: "0", src_bytes: "215", dst_bytes: "4503",
  land: "0", wrong_fragment: "0", urgent: "0", hot: "0", num_failed_logins: "0", logged_in: "1", root_shell: "0",
  su_attempted: "0", num_root: "0", num_file_creations: "0", num_shells: "0", num_access_files: "0", is_guest_login: "0",
  count: "1", srv_count: "1", same_srv_rate: "1", diff_srv_rate: "0", srv_diff_host_rate: "0", dst_host_count: "1",
  dst_host_same_srv_rate: "1", dst_host_diff_srv_rate: "0", dst_host_same_src_port_rate: "1",
  dst_host_srv_diff_host_rate: "0", dst_host_srv_serror_rate: "0", dst_host_srv_rerror_rate: "0",
};
export const PRESETS: { name: string; values: FormValues }[] = [
  { name: "Normal SMTP session", values: NORMAL_PRESET },
  {
    name: "DoS flood",
    values: { ...NORMAL_PRESET, service: "http", flag: "S0", src_bytes: "0", dst_bytes: "0", logged_in: "0", count: "511", srv_count: "511",
      dst_host_count: "255", dst_host_same_src_port_rate: "0.01", dst_host_srv_serror_rate: "1" },
  },
  {
    name: "Port probe",
    values: { ...NORMAL_PRESET, service: "private", flag: "REJ", src_bytes: "0", dst_bytes: "0", logged_in: "0", count: "120", srv_count: "4",
      same_srv_rate: "0.03", diff_srv_rate: "0.9", dst_host_count: "255", dst_host_same_srv_rate: "0.02",
      dst_host_diff_srv_rate: "0.8", dst_host_srv_rerror_rate: "1" },
  },
];
