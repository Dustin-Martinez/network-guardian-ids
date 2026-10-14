"use client";

import { useState } from "react";
import Panel from "./Panel";
import {
  FIELD_GROUPS, FLAGS, MODEL_OPTIONS, NORMAL_PRESET, PRESETS, SERVICES, analyze,
  type FieldDef, type FormValues, type Prediction,
} from "@/lib/data";
import type { ModelName, NetworkPacketRequest } from "@/types";

const NON_NEGATIVE = (n: string) => ["duration", "src_bytes", "dst_bytes"].includes(n);

function validate(v: FormValues): string | null {
  if (!["tcp", "udp", "icmp"].includes(v.protocol_type)) return "protocol_type must be tcp, udp or icmp.";
  if (!v.service.trim()) return "service cannot be empty.";
  if (!v.flag.trim()) return "flag cannot be empty.";
  for (const g of FIELD_GROUPS) {
    for (const f of g.fields) {
      if (f.kind === "select" || f.kind === "text") continue;
      const raw = v[f.name];
      const n = Number(raw);
      if (raw.trim() === "" || !Number.isFinite(n)) return `${f.name} must be a number.`;
      if (f.kind === "binary" && n !== 0 && n !== 1) return `${f.name} must be 0 or 1.`;
      if (f.kind === "rate" && (n < 0 || n > 1)) return `${f.name} must be between 0 and 1.`;
      if ((f.kind === "number" || NON_NEGATIVE(f.name)) && n < 0) return `${f.name} cannot be negative.`;
    }
  }
  return null;
}

function toRequest(v: FormValues, model: ModelName) {
  const out: Record<string, string | number> = { protocol_type: v.protocol_type, service: v.service.trim(), flag: v.flag.trim() };
  for (const g of FIELD_GROUPS) for (const f of g.fields) if (f.kind !== "select" && f.kind !== "text") out[f.name] = Number(v[f.name]);
  return { ...(out as unknown as NetworkPacketRequest), model };
}

export default function AnalyzeForm({
  onResult,
  model,
  onModelChange,
}: {
  onResult: (p: Prediction) => void;
  model: ModelName;
  onModelChange: (m: ModelName) => void;
}) {
  const [values, setValues] = useState<FormValues>(NORMAL_PRESET);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleAnalyze() {
    const problem = validate(values);
    if (problem) return setError(problem);
    setError(null);
    setLoading(true);
    try {
      onResult(await analyze(toRequest(values, model)));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Service unavailable.");
    } finally {
      setLoading(false);
    }
  }

  const field =
    "w-full rounded-md border border-[color:var(--line)] bg-[color:var(--field)] px-3 py-2 text-[color:var(--text)] outline-none focus:border-[color:var(--safe)] focus-visible:ring-2 focus-visible:ring-[color:var(--safe)]";

  function input(f: FieldDef) {
    const set = (val: string) => setValues({ ...values, [f.name]: val });
    const v = values[f.name];
    if (f.kind === "select")
      return (
        <select value={v} onChange={(e) => set(e.target.value)} className={field}>
          <option value="tcp">tcp</option><option value="udp">udp</option><option value="icmp">icmp</option>
        </select>
      );
    if (f.kind === "binary")
      return (
        <select value={v} onChange={(e) => set(e.target.value)} className={field}>
          <option value="0">0</option><option value="1">1</option>
        </select>
      );
    if (f.kind === "text")
      return (
        <>
          <input value={v} list={`${f.name}-list`} onChange={(e) => set(e.target.value)} className={field} />
          <datalist id={`${f.name}-list`}>{(f.name === "service" ? SERVICES : FLAGS).map((o) => <option key={o} value={o} />)}</datalist>
        </>
      );
    return (
      <input type="number" inputMode="decimal" step={f.kind === "rate" ? 0.01 : "any"} min={0} max={f.kind === "rate" ? 1 : undefined}
        value={v} onChange={(e) => set(e.target.value)} className={field} />
    );
  }

  return (
    <Panel title="Analyze a connection">
      <div className="mb-4 flex flex-wrap items-end gap-3">
        <label className="text-sm">
          <span className="mb-1 block text-[color:var(--muted)]">Model</span>
          <select value={model} onChange={(e) => onModelChange(e.target.value as ModelName)} className={field}>
            {MODEL_OPTIONS.map((m) => <option key={m.id} value={m.id}>{m.label}</option>)}
          </select>
        </label>
        <button onClick={handleAnalyze} disabled={loading}
          className="rounded-md bg-[color:var(--safe)] px-4 py-2 font-semibold text-[color:var(--bg)] transition hover:bg-[color:var(--safe-hover)] disabled:opacity-50 outline-none focus-visible:ring-2 focus-visible:ring-white/60">
          {loading ? "Analyzing…" : "Analyze traffic"}
        </button>
        <div className="flex flex-wrap items-center gap-2 text-sm sm:ml-auto">
          <span className="text-[color:var(--muted)]">Load an example:</span>
          {PRESETS.map((p) => (
            <button key={p.name} onClick={() => setValues(p.values)}
              className="rounded-md border border-[color:var(--line)] px-3 py-1 hover:border-[color:var(--safe)] outline-none focus-visible:ring-2 focus-visible:ring-[color:var(--safe)]">
              {p.name}
            </button>
          ))}
        </div>
      </div>

      {error && <p role="alert" className="mb-3 text-sm text-[color:var(--threat-soft)]">{error}</p>}

      <div className="space-y-3">
        {FIELD_GROUPS.map((g) => (
          <details key={g.title} open={g.open} className="rounded-md border border-[color:var(--line)] px-3 py-2">
            <summary className="cursor-pointer text-sm">{g.title} <span className="text-[color:var(--muted)]">({g.fields.length} fields)</span></summary>
            <div className="mt-3 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
              {g.fields.map((f) => (
                <label key={f.name} className="block text-sm">
                  <span className="mb-1 block text-[color:var(--muted)]">{f.name}</span>
                  {input(f)}
                </label>
              ))}
            </div>
          </details>
        ))}
      </div>
    </Panel>
  );
}