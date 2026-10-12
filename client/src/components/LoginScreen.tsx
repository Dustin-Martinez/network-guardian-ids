"use client";

import { useState, type FormEvent } from "react";
import { THEME, login, type Session } from "@/lib/data";

export default function LoginScreen({ onLogin }: { onLogin: (s: Session) => void }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      onLogin(await login(username, password));
    } catch {
      setError("Wrong username or password. Check both and try again.");
    } finally {
      setLoading(false);
    }
  }

  const field =
    "w-full rounded-md border border-[color:var(--line)] bg-[color:var(--field)] px-3 py-2 text-[color:var(--text)] outline-none focus:border-[color:var(--safe)] focus-visible:ring-2 focus-visible:ring-[color:var(--safe)]";

  return (
    <div style={THEME} className="flex min-h-screen items-center justify-center bg-[color:var(--bg)] p-5 font-mono text-[color:var(--text)]">
      <form
        onSubmit={submit}
        className="w-full max-w-sm rounded-xl border border-[color:var(--line)] bg-[color:var(--panel)] p-6 backdrop-blur"
        style={{ boxShadow: "0 0 30px color-mix(in srgb, var(--safe) 15%, transparent)" }}
      >
        <h1 className="text-2xl font-semibold">
          <span className="text-[color:var(--threat)]">◈</span> Network Guardian
        </h1>
        <p className="mb-5 mt-1 text-sm text-[color:var(--muted)]">Sign in to the security operations center.</p>
        <label className="mb-4 block text-sm">
          <span className="mb-1 block text-[color:var(--muted)]">Username</span>
          <input value={username} onChange={(e) => setUsername(e.target.value)} autoComplete="username" autoFocus className={field} />
        </label>
        <label className="mb-4 block text-sm">
          <span className="mb-1 block text-[color:var(--muted)]">Password</span>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" className={field} />
        </label>
        {error && <p role="alert" className="mb-4 text-sm text-[color:var(--threat-soft)]">{error}</p>}
        <button
          type="submit"
          disabled={loading || !username || !password}
          className="w-full rounded-md bg-[color:var(--safe)] px-4 py-2.5 font-semibold text-[color:var(--bg)] transition hover:bg-[color:var(--safe-hover)] disabled:opacity-50 outline-none focus-visible:ring-2 focus-visible:ring-white/60"
        >
          {loading ? "Signing in…" : "Sign in"}
        </button>
        <p className="mt-5 border-t border-[color:var(--line)] pt-4 text-xs text-[color:var(--muted)]">
          Demo account: <span className="text-[color:var(--text)]">analyst</span> / <span className="text-[color:var(--text)]">guardian123</span>
        </p>
      </form>
    </div>
  );
}
