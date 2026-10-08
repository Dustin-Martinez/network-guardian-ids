"use client";

import { useState } from "react";
import Panel from "./Panel";
import { SAMPLES, analyze, type Prediction, type Protocol } from "@/lib/data";

type FormState = { src_bytes: string; duration: string; protocol_type: Protocol };
const EMPTY: FormState = { src_bytes: "", duration: "", protocol_type: "tcp" };

export default function AnalyzeForm({ onResult }: { onResult: (p: Prediction) => void }) {
  const [form, setForm] = useState<FormState>(EMPTY);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const bytes = Number(form.src_bytes);
  const dur = Number(form.duration);
  const valid = form.src_bytes !== "" && form.duration !== "" && bytes >= 0 && dur >= 0;

  async function handleAnalyze() {
    if (!valid) {
      setError("Enter source bytes and duration as numbers of 0 or more.");
      return;
    }
    setError(null);
    setLoading(true);
    try {
      onResult(await analyze({ src_bytes: bytes, duration: dur, protocol_type: form.protocol_type }));
    } catch {
      setError("The analysis service did not respond. Check that the server is running.");
    } finally {
      setLoading(false);
    }
  }

  const field =
    "w-full rounded-md border border-[color:var(--line)] bg-[color:var(--field)] px-3 py-2 text-[color:var(--text)] outline-none focus:border-[color:var(--safe)] focus-visible:ring-2 focus-visible:ring-[color:var(--safe)]";

  return (
    <Panel title="Analyze a connection">
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4 xl:items-end">
        <label className="block text-sm">
          <span className="mb-1 block text-[color:var(--muted)]">Source bytes</span>
          <input type="number" min={0} inputMode="numeric" value={form.src_bytes} placeholder="e.g. 490"
            onChange={(e) => setForm({ ...form, src_bytes: e.target.value })} className={field} />
        </label>
        <label className="block text-sm">
          <span className="mb-1 block text-[color:var(--muted)]">Duration (seconds)</span>
          <input type="number" min={0} inputMode="numeric" value={form.duration} placeholder="e.g. 2"
            onChange={(e) => setForm({ ...form, duration: e.target.value })} className={field} />
        </label>
        <label className="block text-sm">
          <span className="mb-1 block text-[color:var(--muted)]">Protocol</span>
          <select value={form.protocol_type}
            onChange={(e) => setForm({ ...form, protocol_type: e.target.value as Protocol })} className={field}>
            <option value="tcp">TCP</option>
            <option value="udp">UDP</option>
            <option value="icmp">ICMP</option>
          </select>
        </label>
        <button onClick={handleAnalyze} disabled={loading}
          className="rounded-md bg-[color:var(--safe)] px-4 py-2 font-semibold text-[color:var(--bg)] transition hover:bg-[color:var(--safe-hover)] disabled:opacity-50 outline-none focus-visible:ring-2 focus-visible:ring-white/60">
          {loading ? "Analyzing…" : "Analyze traffic"}
        </button>
      </div>
      {error && <p role="alert" className="mt-3 text-sm text-[color:var(--threat-soft)]">{error}</p>}
      <div className="mt-3 flex flex-wrap items-center gap-2 text-sm">
        <span className="text-[color:var(--muted)]">Load an example:</span>
        {SAMPLES.map((s) => (
          <button key={s.name} onClick={() => setForm(s.values)}
            className="rounded-md border border-[color:var(--line)] px-3 py-1 hover:border-[color:var(--safe)] outline-none focus-visible:ring-2 focus-visible:ring-[color:var(--safe)]">
            {s.name}
          </button>
        ))}
      </div>
    </Panel>
  );
}
