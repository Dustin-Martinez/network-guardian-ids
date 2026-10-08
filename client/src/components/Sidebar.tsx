"use client";

import { NAV, type View } from "@/lib/data";

export default function Sidebar({ active, onNavigate }: { active: View; onNavigate: (v: View) => void }) {
  const item = (id: View, name: string, icon: string, extra = "") => (
    <button
      key={id}
      onClick={() => onNavigate(id)}
      aria-current={active === id ? "page" : undefined}
      className={`flex shrink-0 flex-col items-center gap-1 px-4 py-3 text-xs outline-none focus-visible:ring-2 focus-visible:ring-[color:var(--safe)] sm:px-2 sm:py-5 ${extra} ${
        active === id
          ? "border-b-4 border-[color:var(--threat)] bg-[color:var(--threat-bg)] text-[color:var(--threat-soft)] sm:border-b-0 sm:border-l-4"
          : "border-b-4 border-transparent text-[color:var(--muted)] hover:text-[color:var(--text)] sm:border-b-0 sm:border-l-4"
      }`}
    >
      <span className="text-2xl leading-none">{icon}</span>
      {name}
    </button>
  );

  return (
    <nav
      aria-label="Main"
      className="flex w-full shrink-0 overflow-x-auto border-b border-[color:var(--line)] bg-[color:var(--panel)] sm:w-28 sm:flex-col sm:overflow-visible sm:border-b-0 sm:border-r"
    >
      {NAV.map((n) => item(n.id, n.name, n.icon))}
      {item("settings", "Settings", "⚙", "sm:mt-auto")}
    </nav>
  );
}
