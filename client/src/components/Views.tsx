"use client";

import { useState } from "react";
import Panel from "./Panel";
import { FeatureImportances } from "./Charts";
import { FEATURE_HELP, MODELS, type Prediction, type Session } from "@/lib/data";

const btn =
  "rounded-md border border-[color:var(--line)] px-3 py-1.5 text-sm outline-none hover:border-[color:var(--safe)] focus-visible:ring-2 focus-visible:ring-[color:var(--safe)]";

export function HistoryView({ history, onClear }: { history: Prediction[]; onClear: () => void }) {
  const [threatsOnly, setThreatsOnly] = useState(false);
  const rows = threatsOnly ? history.filter((h) => h.isThreat) : history;
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
                {["Time", "Protocol", "Source bytes", "Duration", "Result", "Confidence"].map((h) => (
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
                    <span className={`mr-2 inline-block h-2 w-2 rounded-full ${h.isThreat ? "bg-[color:var(--threat)]" : "bg-[color:var(--safe)]"}`} />
                    {h.label}
                  </td>
                  <td className="px-3 py-2 tabular-nums">{h.confidence.toFixed(1)}%</td>
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
  return (
    <div className="space-y-5">
      <Panel title="Model comparison">
        <p className="mb-4 text-sm text-[color:var(--muted)]">
          Sample values for layout only. They will be replaced by the real evaluation results from the training script.
        </p>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="text-xs text-[color:var(--muted)]">
              <tr>
                {["Model", "Type", "Accuracy", "Precision", "Recall", "F1"].map((h) => (
                  <th key={h} className="border-b border-[color:var(--line)] px-3 py-2 font-normal">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {MODELS.map((m) => (
                <tr key={m.name} className="border-b border-[color:var(--line)] last:border-0">
                  <td className="px-3 py-3 font-semibold">{m.name}</td>
                  <td className="px-3 py-3 text-[color:var(--muted)]">{m.kind}</td>
                  {[m.accuracy, m.precision, m.recall, m.f1].map((v, i) => (
                    <td key={i} className="px-3 py-3 tabular-nums">{v.toFixed(1)}%</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>
      <Panel title="Accuracy">
        <ul className="space-y-3 text-sm">
          {MODELS.map((m) => (
            <li key={m.name} className="grid grid-cols-[9rem_1fr_3.5rem] items-center gap-3">
              <span className="text-[color:var(--muted)]">{m.name}</span>
              <div className="h-4 rounded-sm bg-[color:var(--line)]">
                <div className="h-full rounded-sm bg-[color:var(--safe)]" style={{ width: `${m.accuracy}%`, boxShadow: "0 0 10px var(--safe)" }} />
              </div>
              <span className="tabular-nums">{m.accuracy.toFixed(1)}%</span>
            </li>
          ))}
        </ul>
      </Panel>
    </div>
  );
}

export function ExplainView({ last }: { last: Prediction | null }) {
  return (
    <div className="grid gap-5 lg:grid-cols-2">
      <FeatureImportances />
      <Panel title="Last analysis">
        {last ? (
          <dl className="space-y-2 text-sm">
            <div className="flex justify-between"><dt className="text-[color:var(--muted)]">Result</dt><dd>{last.label} ({last.confidence.toFixed(1)}%)</dd></div>
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
