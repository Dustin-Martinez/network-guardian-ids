"use client";

import { useMemo, useState, useSyncExternalStore } from "react";
import Header from "@/components/Header";
import Sidebar from "@/components/Sidebar";
import LoginScreen from "@/components/LoginScreen";
import AnalyzeForm from "@/components/AnalyzeForm";
import ThreatGauge from "@/components/ThreatGauge";
import { ConfusionMatrix, FeatureImportances, TrafficChart } from "@/components/Charts";
import { ExplainView, HistoryView, ModelsView, SettingsView } from "@/components/Views";
import { THEME, type Prediction, type Session, type View } from "@/lib/data";
import type { ModelName } from "@/types";

function Dashboard({ user, onLogout }: { user: Session; onLogout: () => void }) {
  const [view, setView] = useState<View>("dashboard");
  const [result, setResult] = useState<Prediction | null>(null);
  const [history, setHistory] = useState<Prediction[]>([]);
  const [model, setModel] = useState<ModelName>("xgboost");

  function handleResult(p: Prediction) {
    setResult(p);
    setHistory((h) => [p, ...h].slice(0, 50));
  }
  function clearHistory() {
    setHistory([]);
    setResult(null);
  }

  return (
    <div style={THEME} className="min-h-screen bg-[color:var(--bg)] font-mono text-[color:var(--text)]">
      <Header user={user} onLogout={onLogout} />
      <div className="flex flex-col sm:flex-row">
        <Sidebar active={view} onNavigate={setView} />
        <main className="min-w-0 flex-1 space-y-5 p-5">
          {view === "dashboard" && (
            <>
              <AnalyzeForm onResult={handleResult} model={model} onModelChange={setModel} />
              <div className="grid gap-5 lg:grid-cols-2">
                <TrafficChart />
                <ThreatGauge result={result} history={history} />
                <ConfusionMatrix model={model} />
                <FeatureImportances model={model} />
              </div>
            </>
          )}
          {view === "analyze" && (
            <div className="grid gap-5 lg:grid-cols-[1fr_minmax(0,380px)]">
              <AnalyzeForm onResult={handleResult} model={model} onModelChange={setModel} />
              <ThreatGauge result={result} history={history} />
            </div>
          )}
          {view === "history" && <HistoryView history={history} onClear={clearHistory} />}
          {view === "models" && <ModelsView />}
          {view === "explain" && <ExplainView last={result} model={model} />}
          {view === "settings" && (
            <SettingsView user={user} count={history.length} onClear={clearHistory} onLogout={onLogout} />
          )}
        </main>
      </div>
    </div>
  );
}

const SESSION_KEY = "ng_session";
const listeners = new Set<() => void>();
const notify = () => listeners.forEach((l) => l());
function subscribe(cb: () => void) {
  listeners.add(cb);
  return () => {
    listeners.delete(cb);
  };
}
function getSnapshot(): string | null | undefined {
  try {
    return sessionStorage.getItem(SESSION_KEY);
  } catch {
    return null;
  }
}
function getServerSnapshot(): string | null | undefined {
  return undefined;
}

export default function Home() {
  const raw = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);

  const session = useMemo<Session | null>(() => {
    if (!raw) return null;
    try {
      return JSON.parse(raw) as Session;
    } catch {
      return null;
    }
  }, [raw]);

  function handleLogin(s: Session) {
    try {
      sessionStorage.setItem(SESSION_KEY, JSON.stringify(s));
    } catch {}
    notify();
  }
  function handleLogout() {
    try {
      sessionStorage.removeItem(SESSION_KEY);
    } catch {}
    notify();
  }

  if (raw === undefined) return <div style={THEME} className="min-h-screen bg-[color:var(--bg)]" />;
  return session ? <Dashboard user={session} onLogout={handleLogout} /> : <LoginScreen onLogin={handleLogin} />;
}