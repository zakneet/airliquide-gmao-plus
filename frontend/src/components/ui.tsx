"use client";
import { useEffect, useState, type ReactNode } from "react";
import { STATUSES, type Status } from "@/lib/types";

export function Card({ title, children, action }: { title?: string; children: ReactNode; action?: ReactNode }) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      {(title || action) && (
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-base font-semibold text-slate-900">{title}</h2>
          {action}
        </div>
      )}
      {children}
    </section>
  );
}

export function Button({ variant = "primary", className = "", ...p }:
  React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "ghost" }) {
  const base = "inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition disabled:opacity-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-600";
  const v = variant === "primary" ? "bg-sky-700 text-white hover:bg-sky-800" : "border border-slate-300 bg-white text-slate-700 hover:bg-slate-50";
  return <button {...p} className={`${base} ${v} ${className}`} />;
}

export function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="block text-sm">
      <span className="mb-1 block font-medium text-slate-700">{label}</span>
      {children}
    </label>
  );
}

const inputCls = "w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:border-sky-600 focus:outline-none focus:ring-1 focus:ring-sky-600";
export const Input = (p: React.InputHTMLAttributes<HTMLInputElement>) => <input {...p} className={`${inputCls} ${p.className ?? ""}`} />;
export const Select = (p: React.SelectHTMLAttributes<HTMLSelectElement>) => <select {...p} className={`${inputCls} ${p.className ?? ""}`} />;
export const Textarea = (p: React.TextareaHTMLAttributes<HTMLTextAreaElement>) => <textarea rows={3} {...p} className={`${inputCls} ${p.className ?? ""}`} />;

export function ErrorMsg({ error }: { error: string | null }) {
  return error ? <p role="alert" className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-800">{error}</p> : null;
}

const COLORS: Record<Status, string> = {
  RECU: "bg-slate-100 text-slate-800",
  DESINFECTE: "bg-cyan-100 text-cyan-900",
  DIAGNOSTIC_TERMINE: "bg-amber-100 text-amber-900",
  REPARE: "bg-indigo-100 text-indigo-900",
  QC_VALIDE: "bg-emerald-100 text-emerald-900",
  EN_STOCK: "bg-green-100 text-green-900",
  LIVRE: "bg-slate-200 text-slate-700",
};

export function StatusBadge({ status }: { status: Status }) {
  const label = STATUSES.find((s) => s.value === status)?.label ?? status;
  return <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${COLORS[status]}`}>{label}</span>;
}

export function Stepper({ status }: { status: Status }) {
  const idx = STATUSES.findIndex((s) => s.value === status);
  return (
    <ol className="flex flex-wrap gap-1.5" aria-label="Avancement">
      {STATUSES.map((s, i) => (
        <li key={s.value}
          className={`rounded px-2 py-1 text-xs ${i < idx ? "bg-sky-100 text-sky-900" : i === idx ? "bg-sky-700 text-white" : "bg-slate-100 text-slate-500"}`}>
          {s.label}
        </li>
      ))}
    </ol>
  );
}

export function fmt(d: string) {
  return new Date(d).toLocaleString("fr-FR", { dateStyle: "short", timeStyle: "short" });
}

/** Charge des données et expose état de chargement / erreur. */
export function useLoad<T>(loader: () => Promise<T>, deps: unknown[] = []) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tick, setTick] = useState(0);
  useEffect(() => {
    let alive = true;
    loader().then((d) => alive && (setData(d), setError(null)))
      .catch((e) => alive && setError(e.message));
    return () => { alive = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, tick]);
  return { data, error, reload: () => setTick((t) => t + 1) };
}
