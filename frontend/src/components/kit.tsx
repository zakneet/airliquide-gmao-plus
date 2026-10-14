"use client";
import { useEffect, useState, type ReactNode } from "react";
import {
  AlertTriangle, BadgeCheck, ClipboardList, Inbox, Package, ShieldCheck, Truck, Wrench,
  type LucideIcon,
} from "lucide-react";
import { Button as ShButton } from "@/components/ui/button";
import { Input as ShInput } from "@/components/ui/input";
import { Textarea as ShTextarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";
import { STATUSES, type Status } from "@/lib/types";

/* ---- Structure ---- */

export function Card({ title, children, action, className }:
  { title?: string; children: ReactNode; action?: ReactNode; className?: string }) {
  return (
    <section className={cn("rounded-lg border border-border bg-card p-4 sm:p-5", className)}>
      {(title || action) && (
        <div className="mb-3 flex items-center justify-between gap-3">
          <h2 className="text-base font-semibold">{title}</h2>
          {action}
        </div>
      )}
      {children}
    </section>
  );
}

export function PageTitle({ children, sub, actions }:
  { children: ReactNode; sub?: ReactNode; actions?: ReactNode }) {
  return (
    <header className="flex flex-wrap items-end justify-between gap-x-6 gap-y-3 pb-1">
      <div className="min-w-0">
        <h1 className="text-[1.75rem] font-semibold leading-tight">{children}</h1>
        {sub && <p className="mt-1 max-w-[65ch] text-sm text-muted-foreground">{sub}</p>}
      </div>
      {actions && <div className="flex gap-2">{actions}</div>}
    </header>
  );
}

export function Skeleton({ className }: { className?: string }) {
  return <div aria-hidden className={cn("skeleton", className)} />;
}

/** Lignes de chargement : mêmes dimensions que le contenu pour éviter tout saut de mise en page. */
export function ListSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div role="status" aria-label="Chargement" className="space-y-3">
      {Array.from({ length: rows }, (_, i) => <Skeleton key={i} className="h-12 w-full" />)}
    </div>
  );
}

export function EmptyState({ children }: { children: ReactNode }) {
  return <p className="rounded-md bg-muted px-4 py-6 text-center text-sm text-muted-foreground">{children}</p>;
}

/* ---- Formulaires (cibles ≥ 44 px) ---- */

export function Button({ variant = "primary", className, ...p }:
  React.ComponentProps<"button"> & { variant?: "primary" | "ghost" }) {
  return (
    <ShButton
      {...p}
      variant={variant === "primary" ? "default" : "outline"}
      className={cn("h-11 px-4 text-sm transition-[transform,background-color] duration-100 active:scale-[0.97]", className)}
    />
  );
}

export function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="space-y-1.5">
      <Label className="text-sm font-medium">{label}</Label>
      {children}
    </div>
  );
}

export const Input = ({ className, ...p }: React.ComponentProps<"input">) =>
  <ShInput {...p} className={cn("h-11 bg-card text-base sm:text-sm", className)} />;

export const Textarea = ({ className, ...p }: React.ComponentProps<"textarea">) =>
  <ShTextarea rows={3} {...p} className={cn("bg-card text-base sm:text-sm", className)} />;

export const Select = ({ className, ...p }: React.ComponentProps<"select">) => (
  <select
    {...p}
    className={cn(
      "h-11 w-full rounded-lg border border-input bg-card px-3 text-base text-foreground sm:text-sm",
      "disabled:opacity-50",
      className,
    )}
  />
);

export function ErrorMsg({ error }: { error: string | null }) {
  if (!error) return null;
  return (
    <p role="alert" className="flex items-start gap-2 rounded-md bg-danger-soft px-3 py-2 text-sm text-danger">
      <AlertTriangle className="mt-0.5 size-4 shrink-0" aria-hidden />
      <span>{error}</span>
    </p>
  );
}

/** Choix unique présenté en tuiles (équivalent des boutons radio du questionnaire papier/Google Forms). */
export function RadioTiles({ legend, name, options, value, onChange, disabled, columns = 2 }: {
  legend: string; name: string; options: readonly { value: string; label: string }[];
  value: string; onChange: (v: string) => void; disabled?: boolean; columns?: 2 | 3;
}) {
  return (
    <fieldset disabled={disabled} className="min-w-0">
      <legend className="mb-1.5 text-sm font-medium">{legend}</legend>
      <div className={cn("grid gap-2", columns === 3 ? "sm:grid-cols-3" : "sm:grid-cols-2")}>
        {options.map((o) => (
          <label
            key={o.value}
            className={cn(
              "flex min-h-11 cursor-pointer items-center gap-2.5 rounded-lg border px-3 text-sm transition-colors",
              "has-[input:focus-visible]:outline-2 has-[input:focus-visible]:outline-offset-2 has-[input:focus-visible]:outline-ring",
              value === o.value ? "border-primary bg-accent font-medium text-accent-foreground" : "border-input bg-card hover:bg-muted",
              disabled && "cursor-not-allowed opacity-60",
            )}
          >
            <input
              type="radio" name={name} value={o.value} checked={value === o.value}
              onChange={() => onChange(o.value)} className="size-4 accent-[var(--primary)]"
            />
            {o.label}
          </label>
        ))}
      </div>
    </fieldset>
  );
}

/* ---- Statut : libellé + icône, jamais la couleur seule ---- */

const STATUS_STYLE: Record<Status, { cls: string; Icon: LucideIcon }> = {
  RECU: { cls: "bg-secondary text-secondary-foreground", Icon: Inbox },
  DESINFECTE: { cls: "bg-info-soft text-info", Icon: ShieldCheck },
  DIAGNOSTIC_TERMINE: { cls: "bg-warn-soft text-warn", Icon: ClipboardList },
  REPARE: { cls: "bg-info-soft text-info", Icon: Wrench },
  QC_VALIDE: { cls: "bg-ok-soft text-ok", Icon: BadgeCheck },
  EN_STOCK: { cls: "bg-ok-soft text-ok", Icon: Package },
  LIVRE: { cls: "bg-muted text-muted-foreground", Icon: Truck },
};

export function StatusBadge({ status }: { status: Status }) {
  const { cls, Icon } = STATUS_STYLE[status];
  const label = STATUSES.find((s) => s.value === status)?.label ?? status;
  return (
    <span className={cn("inline-flex items-center gap-1.5 rounded-md px-2 py-1 text-xs font-medium", cls)}>
      <Icon className="size-3.5" aria-hidden />
      {label}
    </span>
  );
}

export function Stepper({ status }: { status: Status }) {
  const idx = STATUSES.findIndex((s) => s.value === status);
  return (
    <ol className="grid grid-cols-4 gap-1.5 sm:grid-cols-7" aria-label="Avancement du dossier">
      {STATUSES.map((s, i) => (
        <li
          key={s.value}
          aria-current={i === idx ? "step" : undefined}
          className={cn(
            "rounded-md border px-2 py-1.5 text-center text-xs",
            i < idx && "border-primary/30 bg-accent text-accent-foreground",
            i === idx && "border-primary bg-primary font-medium text-primary-foreground",
            i > idx && "border-border bg-card text-muted-foreground",
          )}
        >
          {s.label}
        </li>
      ))}
    </ol>
  );
}

/* ---- Données ---- */

export function fmt(d: string) {
  return new Date(d).toLocaleString("fr-FR", { dateStyle: "short", timeStyle: "short" });
}

/** Ancienneté lisible d'un dossier (« 3 j », « 5 h »). */
export function age(d: string) {
  const h = Math.max(0, Math.floor((Date.now() - new Date(d).getTime()) / 3_600_000));
  return h < 24 ? `${h} h` : `${Math.floor(h / 24)} j`;
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
  return { data, error, loading: data === null && error === null, reload: () => setTick((t) => t + 1) };
}

/** Ancienneté en heures (fonction pure vis-à-vis du rendu : l'horloge est lue ici). */
export function ageHours(d: string) {
  return (Date.now() - new Date(d).getTime()) / 3_600_000;
}
