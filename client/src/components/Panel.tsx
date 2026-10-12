import type { ReactNode } from "react";

export default function Panel({ title, right, children }: { title: string; right?: ReactNode; children: ReactNode }) {
  return (
    <section className="rounded-xl border border-[color:var(--line)] bg-[color:var(--panel)] p-5 backdrop-blur">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm uppercase tracking-wide">{title}</h2>
        {right}
      </div>
      {children}
    </section>
  );
}
