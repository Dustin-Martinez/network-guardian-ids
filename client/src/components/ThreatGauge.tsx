import Panel from "./Panel";
import { CLASS_LABEL, type Prediction } from "@/lib/data";

const ARC = "M43.43,156.57 A80,80 0 1 1 156.57,156.57";

export default function ThreatGauge({ result, history = [] }: { result: Prediction | null; history?: Prediction[] }) {
  const pct = result?.confidence ?? 0;
  const color = result?.is_threat ? "var(--threat)" : "var(--safe)";

  return (
    <Panel title="Threat classification gauge">
      <div className="relative mx-auto w-full max-w-[300px]">
        <svg viewBox="0 0 200 200" className="w-full" role="meter" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100} aria-label="Prediction confidence">
          <path d={ARC} fill="none" stroke="var(--line)" strokeWidth="12" strokeLinecap="round" pathLength={100} />
          <path d={ARC} fill="none" stroke={color} strokeWidth="12" strokeLinecap="round" pathLength={100}
            strokeDasharray={`${pct} 100`}
            style={{ transition: "stroke-dasharray 600ms ease", filter: `drop-shadow(0 0 6px ${color})` }} />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
          <span className="text-xs uppercase tracking-wide text-[color:var(--muted)]">Prediction</span>
          <span className="text-4xl font-bold" style={{ color: result ? color : "var(--muted)" }}>{result ? CLASS_LABEL[result.prediction] : "—"}</span>
          <span className="mt-2 text-xs uppercase tracking-wide text-[color:var(--muted)]">Confidence</span>
          <span className="text-lg tabular-nums">{result ? `${pct.toFixed(1)}%` : "No data"}</span>
          {result && <span className="text-xs text-[color:var(--muted)]">{result.model}</span>}
        </div>
      </div>
      <div aria-live="polite"
        className={`mt-2 rounded-md px-3 py-2 text-center text-sm ${result?.is_threat ? "bg-[color:var(--threat-bg)] text-[color:var(--threat-soft)]" : "text-[color:var(--muted)]"}`}>
        {result ? (result.is_threat ? `Threat detected: ${CLASS_LABEL[result.prediction]}` : "No threat detected") : "Run an analysis to see a prediction."}
      </div>
      {history.length > 0 && (
        <ul className="mt-3 flex flex-wrap gap-2 text-xs text-[color:var(--muted)]">
          {history.slice(0, 5).map((h, i) => (
            <li key={i} className="rounded-md border border-[color:var(--line)] px-2 py-1">
              <span className={`mr-1 inline-block h-2 w-2 rounded-full ${h.is_threat ? "bg-[color:var(--threat)]" : "bg-[color:var(--safe)]"}`} />
              {CLASS_LABEL[h.prediction]} {h.confidence.toFixed(0)}%
            </li>
          ))}
        </ul>
      )}
    </Panel>
  );
}
