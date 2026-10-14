"use client";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { login } from "@/lib/api";
import { Button, ErrorMsg, Field, Input } from "@/components/kit";

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
    <main className="flex min-h-screen items-center justify-center p-4">
      <form onSubmit={submit} className="w-full max-w-sm space-y-4 rounded-lg border border-border bg-card p-6 ">
        <div>
          <h1 className="text-xl font-semibold text-primary">AirLiquide GMAO+</h1>
          <p className="text-sm text-muted-foreground">Connexion au suivi SAV</p>
        </div>
        <ErrorMsg error={error} />
        <Field label="Adresse e-mail"><Input name="email" type="email" autoComplete="username" required /></Field>
        <Field label="Mot de passe"><Input name="password" type="password" autoComplete="current-password" required /></Field>
        <Button type="submit" disabled={busy} className="w-full">{busy ? "Connexion…" : "Se connecter"}</Button>
      </form>
    </main>
  );
}
