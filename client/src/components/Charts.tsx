"use client";

import { useEffect, useState } from "react";
import Panel from "./Panel";
import {
  CLASSES,
  loadClassDistribution,
  loadConfusionMatrices,
  loadFeatureImportances,
  MODEL_DISPLAY,
  type ClassDistribution,
  type ConfusionMatrixPayload,
  type FeatureImportancePayload,
} from "@/lib/data";
import type { ModelName } from "@/types";

/* ---------------------------------------------------------------------
   TrafficChart — real class distribution from split_indices.json.
   --------------------------------------------------------------------- */
export function TrafficChart() {
  const [data, setData] = useState<ClassDistribution | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadClassDistribution().then(setData).catch((e) => setError(String(e)));
  }, []);

  if (error) return <Panel title="Class distribution"><p className="text-sm text-[color:var(--threat-soft)]">{error}</p></Panel>;
  if (!data) return <Panel title="Class distribution"><p className="text-sm text-[color:var(--muted)]">Loading…</p></Panel>;

  const max = Math.max(...CLASSES.flatMap((c) => [data.train[c] ?? 0, data.test[c] ?? 0]));

  return (
    <Panel
      title="Class distribution"
      right={
        <span className="flex items-center gap-4 text-xs text-[color:var(--muted)]">
          <span><span className="mr-1 inline-block h-2 w-2 rounded-full bg-[color:var(--safe)]" />train</span>
          <span><span className="mr-1 inline-block h-2 w-2 rounded-full bg-[color:var(--threat)]" />test</span>
        </span>
      }
    >
      <div className="space-y-3">
        {CLASSES.map((c) => (
          <div key={c} className="grid grid-cols-[5rem_1fr] items-center gap-3 text-sm">
            <span className="text-right uppercase tracking-wide text-[color:var(--muted)]">{c}</span>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <div className="h-4 flex-1 rounded-sm bg-[color:var(--line)]">
                  <div className="h-full rounded-sm bg-[color:var(--safe)]"
                       style={{ width: `${((data.train[c] ?? 0) / max) * 100}%`, boxShadow: "0 0 8px var(--safe)" }} />
                </div>
                <span className="w-16 text-right text-xs tabular-nums">{(data.train[c] ?? 0).toLocaleString()}</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="h-4 flex-1 rounded-sm bg-[color:var(--line)]">
                  <div className="h-full rounded-sm bg-[color:var(--threat)]"
                       style={{ width: `${((data.test[c] ?? 0) / max) * 100}%`, boxShadow: "0 0 8px var(--threat)" }} />
                </div>
                <span className="w-16 text-right text-xs tabular-nums">{(data.test[c] ?? 0).toLocaleString()}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </Panel>
  );
}

/* ---------------------------------------------------------------------
   ConfusionMatrix — real test-set confusion matrix for the selected model.
   --------------------------------------------------------------------- */
export function ConfusionMatrix({ model }: { model: ModelName }) {
  const [payload, setPayload] = useState<ConfusionMatrixPayload | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadConfusionMatrices().then(setPayload).catch((e) => setError(String(e)));
  }, []);

  const title = `Confusion matrix — ${MODEL_DISPLAY[model]}`;

  if (error) return <Panel title={title}><p className="text-sm text-[color:var(--threat-soft)]">{error}</p></Panel>;
  if (!payload) return <Panel title={title}><p className="text-sm text-[color:var(--muted)]">Loading…</p></Panel>;

  const matrix = payload[model];
  if (!matrix) return <Panel title={title}><p className="text-sm text-[color:var(--muted)]">No matrix for this model.</p></Panel>;

  const rowSums = matrix.map((row) => row.reduce((a, b) => a + b, 0));

  return (
    <Panel title={title}>
      <div className="grid grid-cols-[auto_1fr] gap-x-3">
        <div className="grid grid-rows-5 gap-1 text-right text-xs text-[color:var(--muted)]">
          {CLASSES.map((c) => (<span key={c} className="flex items-center justify-end">{c}</span>))}
        </div>
        <div>
          <div className="grid grid-cols-5 gap-1">
            {matrix.map((row, r) =>
              row.map((v, c) => {
                const ratio = rowSums[r] > 0 ? v / rowSums[r] : 0;
                const intensity = Math.max(ratio, 0.03);
                return (
                  <div key={`${r}-${c}`}
                       title={`actual ${CLASSES[r]}, predicted ${CLASSES[c]}: ${v}`}
                       className="flex aspect-[2/1] items-center justify-center text-[10px]"
                       style={{
                         background: `color-mix(in srgb, ${r === c ? "var(--safe)" : "var(--threat)"} ${intensity * 100}%, var(--bg))`,
                         color: intensity > 0.5 ? "var(--bg)" : "var(--muted)",
                       }}>
                    {v}
                  </div>
                );
              })
            )}
          </div>
          <div className="mt-2 grid grid-cols-5 gap-1 text-center text-xs text-[color:var(--muted)]">
            {CLASSES.map((c) => (<span key={c}>{c}</span>))}
          </div>
        </div>
      </div>
      <p className="mt-3 text-xs text-[color:var(--muted)]">
        Test-set counts. Source: <span className="text-[color:var(--safe)]">outputs/03_evaluation/test_predictions.csv</span>.
      </p>
    </Panel>
  );
}

/* ---------------------------------------------------------------------
   FeatureImportances — real importances for the selected model.
   --------------------------------------------------------------------- */
export function FeatureImportances({ model }: { model: ModelName }) {
  const [payload, setPayload] = useState<FeatureImportancePayload | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadFeatureImportances().then(setPayload).catch((e) => setError(String(e)));
  }, []);

  const title = `Top feature importances — ${MODEL_DISPLAY[model]}`;

  if (error) return <Panel title={title}><p className="text-sm text-[color:var(--threat-soft)]">{error}</p></Panel>;
  if (!payload) return <Panel title={title}><p className="text-sm text-[color:var(--muted)]">Loading…</p></Panel>;

  const features = payload[model] ?? [];
  if (features.length === 0) {
    return (
      <Panel title={title}>
        <p className="text-sm text-[color:var(--muted)]">
          Feature importance is not available for this model in the current artifact set.
          See the SHAP summary plots in the papers Explainability section.
        </p>
      </Panel>
    );
  }

  const max = Math.max(...features.map((f) => f.value));

  return (
    <Panel title={title}>
      <ul className="space-y-3 text-sm">
        {features.map((f) => (
          <li key={f.name} className="grid grid-cols-[9rem_1fr_3rem] items-center gap-3">
            <span className="text-right text-[color:var(--muted)]">{f.name}</span>
            <div className="h-5 rounded-sm bg-[color:var(--line)]">
              <div className="h-full rounded-sm bg-[color:var(--safe)]"
                   style={{ width: `${(f.value / max) * 100}%`, boxShadow: "0 0 10px var(--safe)" }} />
            </div>
            <span className="text-right text-xs tabular-nums">{f.value.toFixed(3)}</span>
          </li>
        ))}
      </ul>
    </Panel>
  );
}