"use client";

import { useEffect, useState } from "react";
import Panel from "./Panel";
import { FeatureImportances } from "./Charts";
import {
  CLASS_LABEL,
  FEATURE_HELP,
  MODEL_DISPLAY,
  loadEvaluation,
  type EvaluationPayload,
  type Prediction,
  type Session,
} from "@/lib/data";
import type { ModelName } from "@/types";

const btn =
  "rounded-md border border-[color:var(--line)] px-3 py-1.5 text-sm outline-none hover:border-[color:var(--safe)] focus-visible:ring-2 focus-visible:ring-[color:var(--safe)]";

export function HistoryView({ history, onClear }: { history: Prediction[]; onClear: () => void }) {
  const [threatsOnly, setThreatsOnly] = useState(false);
  const rows = threatsOnly ? history.filter((h) => h.is_threat) : history;
  return (
    <Panel
      title="Analysis history"
      right={
        <div className="flex gap-2">
          <button onClick={() => setThreatsOnly((t) => !t)} aria-pressed={threatsOnly} className={btn}>
            {threatsOnly ? "Showing threats only" : "Show threats only"}
          </button>
          <button onClick={onClear} disabled={history.length === 0} className={`${btn} disabled:opacity-40`}>Clear</button>
        </div>
      }
    >
      {rows.length === 0 ? (
        <p className="py-8 text-center text-sm text-[color:var(--muted)]">
          {history.length === 0 ? "No analyses yet. Run one from the Analyze page." : "No threats in your history."}
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="text-xs text-[color:var(--muted)]">
              <tr>
                {["Time", "Protocol", "Source bytes", "Duration", "Result", "Confidence", "Model"].map((h) => (
                  <th key={h} className="border-b border-[color:var(--line)] px-3 py-2 font-normal">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((h, i) => (
                <tr key={i} className="border-b border-[color:var(--line)] last:border-0">
                  <td className="px-3 py-2">{h.at}</td>
                  <td className="px-3 py-2 uppercase">{h.input.protocol_type}</td>
                  <td className="px-3 py-2 tabular-nums">{h.input.src_bytes.toLocaleString()}</td>
                  <td className="px-3 py-2 tabular-nums">{h.input.duration}s</td>
                  <td className="px-3 py-2">
                    <span className={`mr-2 inline-block h-2 w-2 rounded-full ${h.is_threat ? "bg-[color:var(--threat)]" : "bg-[color:var(--safe)]"}`} />
                    {CLASS_LABEL[h.prediction]}
                  </td>
                  <td className="px-3 py-2 tabular-nums">{h.confidence.toFixed(1)}%</td>
                  <td className="px-3 py-2 text-[color:var(--muted)]">{MODEL_DISPLAY[h.model]}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Panel>
  );
}

export function ModelsView() {
  const [data, setData] = useState<EvaluationPayload | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadEvaluation().then(setData).catch((e) => setError(String(e)));
  }, []);

  if (error) return <Panel title="Model comparison"><p className="text-sm text-[color:var(--threat-soft)]">{error}</p></Panel>;
  if (!data) return <Panel title="Model comparison"><p className="text-sm text-[color:var(--muted)]">Loading…</p></Panel>;

  const order: ModelName[] = ["xgboost", "random_forest", "tabnet"];
  const rows = order
    .filter((k) => data.models[k])
    .map((k) => ({
      key: k,
      name: MODEL_DISPLAY[k],
      kind:
        k === "random_forest" ? "Bagging ensemble" :
        k === "xgboost" ? "Boosting ensemble" :
        "Deep learning",
      accuracy: data.models[k].accuracy * 100,
      macroF1: data.models[k].macro_f1 * 100,
      u2r: (data.models[k].per_class["u2r"]?.recall ?? 0) * 100,
      r2l: (data.models[k].per_class["r2l"]?.recall ?? 0) * 100,
    }));

  const maxF1 = Math.max(...rows.map((r) => r.macroF1));

  return (
    <div className="space-y-5">
      <Panel title="Test-set comparison">
        <p className="mb-4 text-sm text-[color:var(--muted)]">
          All numbers from the frozen test-set evaluation.
          Source: <span className="text-[color:var(--safe)]">outputs/03_evaluation/test_set_evaluation.json</span>.
        </p>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="text-xs text-[color:var(--muted)]">
              <tr>
                {["Model", "Type", "Accuracy", "Macro F1", "U2R recall", "R2L recall"].map((h) => (
                  <th key={h} className="border-b border-[color:var(--line)] px-3 py-2 font-normal">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.key} className="border-b border-[color:var(--line)] last:border-0">
                  <td className="px-3 py-3 font-semibold">{r.name}</td>
                  <td className="px-3 py-3 text-[color:var(--muted)]">{r.kind}</td>
                  <td className="px-3 py-3 tabular-nums">{r.accuracy.toFixed(2)}%</td>
                  <td className="px-3 py-3 tabular-nums">{r.macroF1.toFixed(2)}%</td>
                  <td className="px-3 py-3 tabular-nums">{r.u2r.toFixed(2)}%</td>
                  <td className="px-3 py-3 tabular-nums">{r.r2l.toFixed(2)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>
      <Panel title="Macro F1 (test set)">
        <ul className="space-y-3 text-sm">
          {rows.map((r) => (
            <li key={r.key} className="grid grid-cols-[9rem_1fr_4rem] items-center gap-3">
              <span className="text-[color:var(--muted)]">{r.name}</span>
              <div className="h-4 rounded-sm bg-[color:var(--line)]">
                <div className="h-full rounded-sm bg-[color:var(--safe)]"
                     style={{ width: `${(r.macroF1 / maxF1) * 100}%`, boxShadow: "0 0 10px var(--safe)" }} />
              </div>
              <span className="text-right tabular-nums">{r.macroF1.toFixed(2)}%</span>
            </li>
          ))}
        </ul>
      </Panel>
    </div>
  );
}

export function ExplainView({ last, model }: { last: Prediction | null; model: ModelName }) {
  return (
    <div className="grid gap-5 lg:grid-cols-2">
      <FeatureImportances model={model} />
      <Panel title="Last analysis">
        {last ? (
          <dl className="space-y-2 text-sm">
            <div className="flex justify-between"><dt className="text-[color:var(--muted)]">Result</dt><dd>{CLASS_LABEL[last.prediction]} ({last.confidence.toFixed(1)}%)</dd></div>
            <div className="flex justify-between"><dt className="text-[color:var(--muted)]">Protocol</dt><dd className="uppercase">{last.input.protocol_type}</dd></div>
            <div className="flex justify-between"><dt className="text-[color:var(--muted)]">Source bytes</dt><dd>{last.input.src_bytes.toLocaleString()}</dd></div>
            <div className="flex justify-between"><dt className="text-[color:var(--muted)]">Duration</dt><dd>{last.input.duration}s</dd></div>
          </dl>
        ) : (
          <p className="py-6 text-center text-sm text-[color:var(--muted)]">Run an analysis to see its inputs here.</p>
        )}
      </Panel>
      <div className="lg:col-span-2">
        <Panel title="What each feature means">
          <dl className="grid gap-x-8 gap-y-3 text-sm md:grid-cols-2">
            {Object.entries(FEATURE_HELP).map(([k, v]) => (
              <div key={k}>
                <dt className="text-[color:var(--safe)]">{k}</dt>
                <dd className="text-[color:var(--muted)]">{v}</dd>
              </div>
            ))}
          </dl>
        </Panel>
      </div>
    </div>
  );
}

export function SettingsView({ user, count, onClear, onLogout }: { user: Session; count: number; onClear: () => void; onLogout: () => void }) {
  return (
    <div className="grid gap-5 lg:grid-cols-2">
      <Panel title="Account">
        <p className="font-semibold">{user.name}</p>
        <p className="mb-4 text-sm text-[color:var(--muted)]">{user.role}</p>
        <button onClick={onLogout} className={btn}>Sign out</button>
      </Panel>
      <Panel title="Data">
        <p className="mb-4 text-sm text-[color:var(--muted)]">
          {count === 0 ? "No saved analyses." : `${count} saved ${count === 1 ? "analysis" : "analyses"} in this session.`}
        </p>
        <button onClick={onClear} disabled={count === 0} className={`${btn} disabled:opacity-40`}>Clear history</button>
      </Panel>
    </div>
  );
}