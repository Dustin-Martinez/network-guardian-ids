import Panel from "./Panel";
import { CLASSES, FEATURES, MATRIX, TRAFFIC_DOS, TRAFFIC_NORMAL } from "@/lib/data";

function smooth(pts: [number, number][]) {
  let d = `M${pts[0][0]},${pts[0][1]}`;
  for (let i = 0; i < pts.length - 1; i++) {
    const p0 = pts[i - 1] ?? pts[i], p1 = pts[i], p2 = pts[i + 1], p3 = pts[i + 2] ?? p2;
    d += ` C${p1[0] + (p2[0] - p0[0]) / 6},${p1[1] + (p2[1] - p0[1]) / 6} ${p2[0] - (p3[0] - p1[0]) / 6},${p2[1] - (p3[1] - p1[1]) / 6} ${p2[0]},${p2[1]}`;
  }
  return d;
}

export function TrafficChart() {
  const X = (i: number) => 40 + i * (430 / 12);
  const Y = (v: number) => 190 - (v / 200) * 180;
  const line = (data: number[]) => smooth(data.map((v, i) => [X(i), Y(v)] as [number, number]));
  return (
    <Panel
      title="Live network traffic"
      right={
        <span className="flex items-center gap-4 text-xs text-[color:var(--muted)]">
          <span><span className="mr-1 inline-block h-2 w-2 rounded-full bg-[color:var(--safe)]" />normal</span>
          <span><span className="mr-1 inline-block h-2 w-2 rounded-full bg-[color:var(--threat)]" />dos</span>
        </span>
      }
    >
      <svg viewBox="0 0 480 220" className="w-full" role="img" aria-label="Live network traffic, normal versus DoS">
        {[0, 50, 100, 150, 200].map((v) => (
          <g key={v}>
            <line x1="40" x2="470" y1={Y(v)} y2={Y(v)} stroke="var(--line)" />
            <text x="32" y={Y(v) + 4} textAnchor="end" fontSize="10" fill="var(--muted)">{v}</text>
          </g>
        ))}
        {[0, 2, 4, 6, 8, 10, 12].map((i) => (
          <text key={i} x={X(i)} y="208" textAnchor="middle" fontSize="10" fill="var(--muted)">{i * 20}</text>
        ))}
        <path d={line(TRAFFIC_DOS)} fill="none" stroke="var(--threat)" strokeWidth="2.5" style={{ filter: "drop-shadow(0 0 5px var(--threat))" }} />
        <path d={line(TRAFFIC_NORMAL)} fill="none" stroke="var(--safe)" strokeWidth="2.5" style={{ filter: "drop-shadow(0 0 5px var(--safe))" }} />
      </svg>
    </Panel>
  );
}

export function ConfusionMatrix() {
  return (
    <Panel title="Confusion matrix">
      <div className="grid grid-cols-[auto_1fr] gap-x-3">
        <div className="grid grid-rows-5 gap-1 text-right text-xs text-[color:var(--muted)]">
          {CLASSES.map((c) => (<span key={c} className="flex items-center justify-end">{c}</span>))}
        </div>
        <div>
          <div className="grid grid-cols-5 gap-1">
            {MATRIX.map((row, r) =>
              row.map((v, c) => (
                <div key={`${r}-${c}`} title={`actual ${CLASSES[r]}, predicted ${CLASSES[c]}: ${v}`}
                  className="flex aspect-[2/1] items-center justify-center text-[10px]"
                  style={{
                    background: `color-mix(in srgb, ${r === c ? "var(--safe)" : "var(--threat)"} ${Math.max(v, 0.04) * 100}%, var(--bg))`,
                    color: v > 0.5 ? "var(--bg)" : "var(--muted)",
                  }}>
                  {v.toFixed(2)}
                </div>
              ))
            )}
          </div>
          <div className="mt-2 grid grid-cols-5 gap-1 text-center text-xs text-[color:var(--muted)]">
            {CLASSES.map((c) => (<span key={c}>{c}</span>))}
          </div>
        </div>
      </div>
    </Panel>
  );
}

export function FeatureImportances() {
  return (
    <Panel title="Top feature importances">
      <ul className="space-y-3 text-sm">
        {FEATURES.map((f) => (
          <li key={f.name} className="grid grid-cols-[7rem_1fr] items-center gap-3">
            <span className="text-right text-[color:var(--muted)]">{f.name}</span>
            <div className="h-5 rounded-sm bg-[color:var(--line)]">
              <div className="h-full rounded-sm bg-[color:var(--safe)]" style={{ width: `${(f.value / 300) * 100}%`, boxShadow: "0 0 10px var(--safe)" }} />
            </div>
          </li>
        ))}
      </ul>
    </Panel>
  );
}
