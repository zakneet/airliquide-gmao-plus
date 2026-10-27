"use client";
import { useState } from "react";
import { downloadCsv } from "@/lib/api";
import { Button, Card, ErrorMsg, Field, Input, Select } from "@/components/kit";
import { STATUSES } from "@/lib/types";

export default function ReportsPage() {
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    const q = new URLSearchParams();
    for (const k of ["status", "date_from", "date_to"]) if (f.get(k)) q.set(k, String(f.get(k)));
    try {
      setError(null);
      await downloadCsv(`/reports/dossiers.csv?${q}`, "dossiers_sav.csv");
    } catch (err) {
      setError((err as Error).message);
    }
  }

  return (
    <>
      <h1 className="text-2xl font-semibold">Rapports</h1>
      <Card title="Export des dossiers SAV (CSV)">
        <form onSubmit={onSubmit} className="grid gap-3 sm:grid-cols-3">
          <div className="sm:col-span-3"><ErrorMsg error={error} /></div>
          <Field label="Statut">
            <Select name="status" defaultValue=""><option value="">Tous</option>
              {STATUSES.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
            </Select>
          </Field>
          <Field label="Du"><Input type="date" name="date_from" /></Field>
          <Field label="Au"><Input type="date" name="date_to" /></Field>
          <div className="sm:col-span-3"><Button type="submit">Télécharger</Button></div>
        </form>
      </Card>
    </>
  );
}
