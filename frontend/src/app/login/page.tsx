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
      <section className="hidden bg-primary p-12 text-primary-foreground lg:flex lg:flex-col lg:justify-between">
        <div>
          <p className="text-2xl font-semibold">AirLiquide GMAO+</p>
          <p className="mt-1 text-sm opacity-80">Maintenance et SAV des dispositifs médicaux</p>
        </div>
        <ul className="space-y-7">
          {POINTS.map(({ Icon, title, text }) => (
            <li key={title} className="flex gap-4">
              <Icon className="mt-0.5 size-5 shrink-0 opacity-90" aria-hidden />
              <div>
                <p className="font-medium">{title}</p>
                <p className="mt-0.5 max-w-md text-sm opacity-80">{text}</p>
              </div>
            </li>
          ))}
        </ul>
        <p className="text-xs opacity-70">Accès réservé au personnel autorisé.</p>
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
