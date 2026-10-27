"use client";
import Link from "next/link";
import { useState } from "react";
import { ShieldAlert } from "lucide-react";
import { api } from "@/lib/api";
import {
  Button, Card, EmptyState, ErrorMsg, Field, fmt, Input, PageTitle, RadioTiles, useLoad,
} from "@/components/kit";
import { BIOHAZARD_STATUSES, VISUAL_CONDITIONS, labelOf, type ReturnDeclaration } from "@/lib/types";

export default function ReturnsPage() {
  const [pendingOnly, setPendingOnly] = useState(true);
  const list = useLoad(() => api<ReturnDeclaration[]>(`/returns/${pendingOnly ? "?pending=1" : ""}`), [pendingOnly]);
  const [visual, setVisual] = useState("GOOD");
  const [bio, setBio] = useState("NORMAL");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [formKey, setFormKey] = useState(0);

  async function submit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    setBusy(true); setError(null);
    try {
      await api("/returns/", {
        method: "POST",
        json: {
          return_id: f.get("return_id"), serial_number: f.get("serial_number"),
          visual_condition: visual, biohazard_status: bio, missing_accessories: f.get("missing_accessories"),
        },
      });
      setFormKey((k) => k + 1); setVisual("GOOD"); setBio("NORMAL");
      list.reload();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <PageTitle sub="Questionnaire rempli avant l'arrivée de l'appareil. À la réception, le technicien le retrouve ici.">
        Retours annoncés
      </PageTitle>

      <Card title="Annoncer un retour">
        <form key={formKey} onSubmit={submit} className="grid gap-4 md:grid-cols-2">
          <div className="md:col-span-2"><ErrorMsg error={error} /></div>
          <Field label="ID de retour *"><Input name="return_id" required /></Field>
          <Field label="Numéro de série *"><Input name="serial_number" required className="ident" /></Field>
          <RadioTiles legend="État visuel *" name="visual_condition" options={VISUAL_CONDITIONS}
            value={visual} onChange={setVisual} />
          <RadioTiles legend="Statut biologique *" name="biohazard_status" options={BIOHAZARD_STATUSES}
            value={bio} onChange={setBio} />
          <div className="md:col-span-2">
            <Field label="Accessoires manquants"><Input name="missing_accessories" /></Field>
          </div>
          <div className="md:col-span-2"><Button type="submit" disabled={busy}>{busy ? "Envoi…" : "Enregistrer l'annonce"}</Button></div>
        </form>
      </Card>

      <Card
        title="Retours"
        action={
          <Button variant="ghost" className="h-9" onClick={() => setPendingOnly((v) => !v)}>
            {pendingOnly ? "Afficher tous" : "Afficher en attente"}
          </Button>
        }
      >
        <ErrorMsg error={list.error} />
        {list.data?.length === 0 && <EmptyState>{pendingOnly ? "Aucun retour en attente de réception." : "Aucun retour enregistré."}</EmptyState>}
        <ul className="divide-y divide-border">
          {list.data?.map((r) => (
            <li key={r.id} className="flex flex-wrap items-center justify-between gap-3 py-3">
              <div className="min-w-0">
                <p className="flex flex-wrap items-center gap-2">
                  <span className="ident font-medium">{r.serial_number}</span>
                  <span className="text-sm text-muted-foreground">retour {r.return_id}</span>
                  {r.biohazard_status !== "NORMAL" && (
                    <span className="inline-flex items-center gap-1 text-xs font-medium text-danger">
                      <ShieldAlert className="size-3.5" aria-hidden />{labelOf(BIOHAZARD_STATUSES, r.biohazard_status)}
                    </span>
                  )}
                </p>
                <p className="text-sm text-muted-foreground">
                  {labelOf(VISUAL_CONDITIONS, r.visual_condition)}
                  {r.missing_accessories && ` · manque : ${r.missing_accessories}`} · annoncé le {fmt(r.declared_at)}
                </p>
              </div>
              {r.received ? (
                <Link href={`/dossiers/${r.dossier_id}`} className="text-sm font-medium text-link hover:underline">Réceptionné</Link>
              ) : (
                <Link href={`/reception?return=${r.id}`}
                  className="inline-flex h-11 items-center rounded-lg bg-primary px-4 text-sm font-medium text-primary-foreground">
                  Réceptionner
                </Link>
              )}
            </li>
          ))}
        </ul>
      </Card>
    </>
  );
}
