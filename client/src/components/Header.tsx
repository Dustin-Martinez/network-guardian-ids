"use client";

import { useState } from "react";
import { STATUSES, type Session } from "@/lib/data";

export default function Header({ user, onLogout }: { user: Session; onLogout: () => void }) {
  const [statusId, setStatusId] = useState("online");
  const [menuOpen, setMenuOpen] = useState(false);
  const status = STATUSES.find((s) => s.id === statusId) ?? STATUSES[0];

  return (
    <header className="flex items-center gap-4 border-b border-[color:var(--line)] px-5 py-3">
      <h1 className="text-xl font-semibold">
        <span className="text-[color:var(--threat)]">◈</span> Network Guardian
      </h1>
      <input
        aria-label="Search"
        placeholder="Search..."
        className="mx-auto hidden w-full max-w-xl rounded-md border border-[color:var(--line)] bg-[color:var(--panel)] px-4 py-2 text-sm outline-none focus-visible:ring-2 focus-visible:ring-[color:var(--safe)] md:block"
      />
      <div className="relative ml-auto text-sm">
        <button
          onClick={() => setMenuOpen((o) => !o)}
          aria-haspopup="menu"
          aria-expanded={menuOpen}
          className="flex items-center gap-3 rounded-md px-2 py-1 outline-none hover:bg-[color:var(--panel)] focus-visible:ring-2 focus-visible:ring-[color:var(--safe)]"
        >
          <span className="relative flex h-9 w-9 items-center justify-center rounded-full border border-[color:var(--line)] bg-[color:var(--panel)]">
            {user.name[0].toUpperCase()}
            <span className="absolute -bottom-0.5 -right-0.5 h-3 w-3 rounded-full border-2 border-[color:var(--bg)]" style={{ background: status.color }} />
          </span>
          <span className="text-left leading-tight">
            <span className="block">{user.name}</span>
            <span className="block text-xs text-[color:var(--muted)]">{status.label}</span>
          </span>
          <span aria-hidden className="text-[color:var(--muted)]">▾</span>
        </button>

        {menuOpen && (
          <>
            <button aria-label="Close menu" className="fixed inset-0 z-10 cursor-default" onClick={() => setMenuOpen(false)} />
            <div
              role="menu"
              onKeyDown={(e) => e.key === "Escape" && setMenuOpen(false)}
              className="absolute right-0 z-20 mt-2 w-64 rounded-xl border border-[color:var(--line)] bg-[color:var(--bg)] p-4 shadow-xl"
            >
              <p className="font-semibold">{user.name}</p>
              <p className="text-xs text-[color:var(--muted)]">{user.role}</p>
              <p className="mb-1 mt-4 text-xs text-[color:var(--muted)]">Status</p>
              {STATUSES.map((st) => (
                <button
                  key={st.id}
                  role="menuitemradio"
                  aria-checked={st.id === statusId}
                  onClick={() => setStatusId(st.id)}
                  className={`flex w-full items-center gap-2 rounded-md px-2 py-2 text-left outline-none hover:bg-[color:var(--panel)] focus-visible:ring-2 focus-visible:ring-[color:var(--safe)] ${
                    st.id === statusId ? "bg-[color:var(--panel)]" : ""
                  }`}
                >
                  <span className="h-2.5 w-2.5 rounded-full" style={{ background: st.color }} />
                  {st.label}
                </button>
              ))}
              <button
                role="menuitem"
                onClick={onLogout}
                className="mt-3 w-full rounded-md border border-[color:var(--line)] px-3 py-2 text-left outline-none hover:border-[color:var(--threat)] hover:text-[color:var(--threat-soft)] focus-visible:ring-2 focus-visible:ring-[color:var(--safe)]"
              >
                Sign out
              </button>
            </div>
          </>
        )}
      </div>
    </header>
  );
}
