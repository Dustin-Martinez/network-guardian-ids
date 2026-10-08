import type { CSSProperties } from "react";

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

/* ---------- types ---------- */
export type Protocol = "tcp" | "udp" | "icmp";
export type Input = { src_bytes: number; duration: number; protocol_type: Protocol };
export type Prediction = { label: string; isThreat: boolean; confidence: number; at: string; input: Input };
export type Session = { name: string; role: string };
export type View = "dashboard" | "analyze" | "history" | "models" | "explain" | "settings";

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
export const SAMPLES: { name: string; values: { src_bytes: string; duration: string; protocol_type: Protocol } }[] = [
  { name: "Web browsing", values: { src_bytes: "490", duration: "2", protocol_type: "tcp" } },
  { name: "Ping flood", values: { src_bytes: "1032", duration: "0", protocol_type: "icmp" } },
  { name: "Large transfer", values: { src_bytes: "250000", duration: "45", protocol_type: "tcp" } },
];

/**
 * PHASE 1 PLACEHOLDER: rough local heuristic so the UI works before the backend exists.
 * PHASE 3: replace the body with
 *   const res = await fetch("http://localhost:5000/api/analyze", {
 *     method: "POST",
 *     headers: { "Content-Type": "application/json" },
 *     body: JSON.stringify(input),
 *   });
 *   return res.json(); // then map the response to Prediction
 */
export async function analyze(input: Input): Promise<Prediction> {
  await new Promise((r) => setTimeout(r, 400));
  const burst = input.duration === 0 && input.src_bytes > 500;
  const heavy = input.src_bytes > 100000;
  const isThreat = burst || heavy || input.protocol_type === "icmp";
  const label = burst ? "DoS" : heavy ? "Probe" : isThreat ? "Suspicious" : "Normal";
  const confidence = isThreat ? (burst ? 93.2 : 78.4) : 88.1;
  return { label, isThreat, confidence, at: new Date().toLocaleTimeString(), input };
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
