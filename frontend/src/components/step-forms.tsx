"use client";
import { useState } from "react";
import { Plus } from "lucide-react";
import { api } from "@/lib/api";
import { Button, Field, Input, Select, Textarea, useLoad } from "@/components/kit";
import { QC_CHECKLIST, type Dossier, type Fault, type Part } from "@/lib/types";

export type Submit = (action: string, body: unknown) => Promise<void>;

function toIso(v: FormDataEntryValue | null) {
  return v ? new Date(String(v)).toISOString() : "";
}

const tile =
  "flex min-h-11 cursor-pointer items-center gap-2.5 rounded-lg border border-input bg-card px-3 text-sm transition-colors hover:bg-muted has-[input:checked]:border-primary has-[input:checked]:bg-accent";

/** Formulaire de l'étape en cours : un seul formulaire à la fois, au bon endroit du parcours. */
export function StepForm({ d, submit, busy }: { d: Dossier; submit: Submit; busy: boolean }) {
  const faults = useLoad(() => api<Fault[]>(`/faults/?device_type=${d.device.device_type}`), [d.device.device_type]);
  const parts = useLoad(() => api<Part[]>("/parts/"));
  const [nParts, setNParts] = useState(0);

  const onSubmit = (action: string, build: (f: FormData) => unknown) => (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    return submit(action, build(new FormData(e.currentTarget)));
  };
  const submitBtn = (label: string) => (
    <Button type="submit" disabled={busy}>{busy ? "Enregistrement…" : label}</Button>
  );

  switch (d.status) {
    case "RECU":
      return (
        <form className="space-y-4" onSubmit={onSubmit("disinfection", (f) => ({
          product: f.get("product"), comment: f.get("comment"), validated: f.get("validated") === "on" }))}>
          <Field label="Produit / méthode"><Input name="product" /></Field>
          <Field label="Commentaire"><Textarea name="comment" /></Field>
          <label className={tile}>
            <input type="checkbox" name="validated" defaultChecked className="size-4 accent-[var(--primary)]" />
            Désinfection réalisée et validée
          </label>
          {submitBtn("Valider la désinfection")}
        </form>
      );

    case "DESINFECTE": {
      const list = faults.data?.filter((x) => x.active) ?? [];
      return (
        <form className="space-y-4" onSubmit={onSubmit("diagnosis", (f) => ({
          comment: f.get("comment"),
          faults: list.filter((x) => f.get(`fault-${x.id}`) === "on").map((x) => ({
            fault: x.id, severity: f.get(`sev-${x.id}`) })),
        }))}>
          <fieldset className="space-y-2">
            <legend className="mb-1.5 text-sm font-medium">Pannes constatées</legend>
            {faults.data && list.length === 0 && (
              <p className="text-sm text-muted-foreground">
                Aucune panne au catalogue pour ce type d&apos;appareil : le Responsable SAV peut en ajouter.
              </p>
            )}
            <ul className="grid gap-2">
              {list.map((x) => (
                <li key={x.id} className={`${tile} justify-between`}>
                  <label className="flex flex-1 cursor-pointer items-center gap-2.5 py-2">
                    <input type="checkbox" name={`fault-${x.id}`} className="size-4 accent-[var(--primary)]" />
                    {x.name}
                  </label>
                  <Select name={`sev-${x.id}`} defaultValue="MAJEURE" aria-label={`Gravité : ${x.name}`} className="!h-9 !w-32">
                    <option value="MINEURE">Mineure</option>
                    <option value="MAJEURE">Majeure</option>
                    <option value="CRITIQUE">Critique</option>
                  </Select>
                </li>
              ))}
            </ul>
          </fieldset>
          <Field label="Observations"><Textarea name="comment" /></Field>
          {submitBtn("Terminer le diagnostic")}
        </form>
      );
    }

    case "DIAGNOSTIC_TERMINE":
      return (
        <form className="space-y-4" onSubmit={onSubmit("repair", (f) => ({
          started_at: toIso(f.get("started_at")), ended_at: toIso(f.get("ended_at")),
          tests: f.get("tests"), comment: f.get("comment"),
          parts_exit_document: f.get("parts_exit_document"),
          parts: Array.from({ length: nParts }, (_, i) => ({ part: Number(f.get(`part-${i}`)), quantity: Number(f.get(`qty-${i}`)) }))
            .filter((p) => p.part),
        }))}>
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Début *"><Input type="datetime-local" name="started_at" required /></Field>
            <Field label="Fin *"><Input type="datetime-local" name="ended_at" required /></Field>
          </div>
          <fieldset className="space-y-2">
            <legend className="mb-1.5 text-sm font-medium">Pièces remplacées</legend>
            {Array.from({ length: nParts }, (_, i) => (
              <div key={i} className="flex gap-2">
                <Select name={`part-${i}`} aria-label="Pièce">
                  <option value="">Choisir une pièce…</option>
                  {parts.data?.map((p) => <option key={p.id} value={p.id}>{p.reference} · {p.name}</option>)}
                </Select>
                <Input type="number" name={`qty-${i}`} min={1} defaultValue={1} aria-label="Quantité" className="!w-24" />
              </div>
            ))}
            <Button type="button" variant="ghost" onClick={() => setNParts(nParts + 1)}>
              <Plus className="mr-2 size-4" aria-hidden />Ajouter une pièce
            </Button>
          </fieldset>
          <Field label="Document de sortie pièces (PR)"><Input name="parts_exit_document" className="ident" /></Field>
          <Field label="Tests effectués"><Textarea name="tests" /></Field>
          <Field label="Commentaire"><Textarea name="comment" /></Field>
          {submitBtn("Enregistrer la réparation")}
        </form>
      );

    case "REPARE":
      return (
        <form className="space-y-4" onSubmit={onSubmit("quality-control", (f) => ({
          checklist: Object.fromEntries(QC_CHECKLIST.map((i) => [i, f.get(`qc-${i}`) === "on"])),
          purity: f.get("purity") || null,
          flow_pressure: f.get("flow_pressure"),
          audible_alarm_ok: f.get("alarm") === "ok" ? true : f.get("alarm") === "ko" ? false : null,
          comment: f.get("comment") }))}>
          <div className="grid gap-4 sm:grid-cols-3">
            <Field label="Pureté O₂ (%)">
              <Input name="purity" type="number" step="0.1" min="0" max="100" inputMode="decimal" className="ident" />
            </Field>
            <Field label="Débit / pression"><Input name="flow_pressure" placeholder="ex. 3 L/min" /></Field>
            <Field label="Alarme sonore">
              <Select name="alarm" defaultValue="">
                <option value="">Non testée</option>
                <option value="ok">Conforme</option>
                <option value="ko">Non conforme</option>
              </Select>
            </Field>
          </div>
          <fieldset>
            <legend className="mb-1.5 text-sm font-medium">Checklist : cocher chaque point conforme</legend>
            <div className="grid gap-2 sm:grid-cols-2">
              {QC_CHECKLIST.map((i) => (
                <label key={i} className={tile}>
                  <input type="checkbox" name={`qc-${i}`} className="size-4 accent-[var(--primary)]" />{i}
                </label>
              ))}
            </div>
          </fieldset>
          <Field label="Commentaire (obligatoire si un point n'est pas conforme)"><Textarea name="comment" /></Field>
          {submitBtn("Enregistrer le contrôle")}
        </form>
      );

    case "QC_VALIDE":
      return (
        <form className="space-y-4" onSubmit={onSubmit("stock-entry", (f) => ({ location: f.get("location") }))}>
          <Field label="Emplacement *"><Input name="location" required className="ident" /></Field>
          {submitBtn("Placer en stock livrable")}
        </form>
      );

    case "EN_STOCK":
      return (
        <form className="space-y-4" onSubmit={onSubmit("delivery", (f) => ({
          recipient: f.get("recipient"), delivery_note: f.get("delivery_note"), comment: f.get("comment") }))}>
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Destinataire *"><Input name="recipient" required /></Field>
            <Field label="N° de bon de livraison"><Input name="delivery_note" className="ident" /></Field>
          </div>
          <Field label="Commentaire"><Textarea name="comment" /></Field>
          {submitBtn("Enregistrer la livraison")}
        </form>
      );

    default:
      return null;
  }
}
