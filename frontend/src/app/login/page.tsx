"use client";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { ClipboardCheck, History, ShieldCheck } from "lucide-react";
import { login } from "@/lib/api";
import { Button, ErrorMsg, Field, Input } from "@/components/kit";

const POINTS = [
  { Icon: History, title: "Une fiche de vie par appareil", text: "Chaque retour, intervention et pièce reste rattaché au même numéro de série." },
  { Icon: ShieldCheck, title: "Désinfection avant tout", text: "Aucune étape suivante sans désinfection validée et risque biologique signalé." },
  { Icon: ClipboardCheck, title: "Contrôle qualité tracé", text: "Mesures, checklist et technicien enregistrés avant la mise en stock." },
];

const CIRCUIT = ["Réception", "Désinfection", "Diagnostic", "Réparation", "Contrôle", "Stock", "Livraison"];

/** Le circuit d'un appareil, de la réception à la livraison. Géométrie pure, tracé animé une fois. */
function Circuit() {
  const xs = CIRCUIT.map((_, i) => 14 + (i * (460 - 28)) / (CIRCUIT.length - 1));
  return (
    <figure aria-label="Circuit d'un appareil : réception, désinfection, diagnostic, réparation, contrôle, stock, livraison">
      <svg viewBox="0 0 460 28" className="w-full" fill="none" aria-hidden>
        <path d="M14 14H446" pathLength={1} className="line-draw" stroke="oklch(0.55 0.1 258)" strokeWidth="2" strokeLinecap="round" />
        {xs.map((x, i) => (
          <circle key={x} cx={x} cy={14} r={i === 0 || i === CIRCUIT.length - 1 ? 6 : 4.5}
            className="node-in" style={{ ["--i" as string]: i }}
            fill={i === 0 ? "oklch(0.96 0.01 250)" : "oklch(0.2 0.05 258)"}
            stroke="oklch(0.75 0.06 255)" strokeWidth="2" />
        ))}
      </svg>
      <figcaption className="mt-2 grid grid-cols-7 text-[11px] leading-tight text-ink-muted">
        {CIRCUIT.map((c) => <span key={c} className="text-center first:text-left last:text-right">{c}</span>)}
      </figcaption>
    </figure>
  );
}

export default function LoginPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    setBusy(true);
    try {
      await login(String(f.get("email")), String(f.get("password")));
      router.replace("/");
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="grid min-h-screen lg:grid-cols-[minmax(0,1.1fr)_minmax(0,1fr)]">
      <section className="hidden bg-ink p-12 text-ink-foreground lg:flex lg:flex-col lg:justify-between">
        <div>
          <p className="text-2xl font-semibold tracking-tight">AirLiquide GMAO+</p>
          <p className="mt-1 text-sm text-ink-muted">Maintenance et SAV des dispositifs médicaux</p>
        </div>
        <div className="space-y-12">
          <Circuit />
          <ul className="space-y-6">
            {POINTS.map(({ Icon, title, text }) => (
              <li key={title} className="flex gap-4">
                <Icon className="mt-0.5 size-5 shrink-0 text-ink-muted" aria-hidden />
                <div>
                  <p className="font-medium">{title}</p>
                  <p className="mt-0.5 max-w-md text-sm text-ink-muted">{text}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>
        <p className="text-xs text-ink-muted">Accès réservé au personnel autorisé.</p>
      </section>

      <section className="flex items-center justify-center p-6">
        <form onSubmit={submit} className="w-full max-w-sm space-y-5">
          <div>
            <p className="text-sm font-medium text-primary lg:hidden">AirLiquide GMAO+</p>
            <h1 className="text-2xl font-semibold">Connexion</h1>
            <p className="mt-1 text-sm text-muted-foreground">Utilisez votre compte professionnel.</p>
          </div>
          <ErrorMsg error={error} />
          <Field label="Adresse e-mail"><Input name="email" type="email" autoComplete="username" required /></Field>
          <Field label="Mot de passe"><Input name="password" type="password" autoComplete="current-password" required /></Field>
          <Button type="submit" disabled={busy} className="w-full">{busy ? "Connexion…" : "Se connecter"}</Button>
        </form>
      </section>
    </main>
  );
}
