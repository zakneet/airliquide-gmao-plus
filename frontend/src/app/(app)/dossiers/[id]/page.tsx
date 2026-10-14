"use client";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useState } from "react";
import { api } from "@/lib/api";
import { Button, Card, ErrorMsg, Field, fmt, Input, Select, Stepper, StatusBadge, Textarea, useLoad } from "@/components/ui";
import { NEXT_STEP, QC_CHECKLIST, type Dossier, type Fault, type Part } from "@/lib/types";

type Submit = (action: string, body: unknown) => Promise<void>;

function toIso(v: FormDataEntryValue | null) {
  return v ? new Date(String(v)).toISOString() : "";
}

function StepForm({ d, submit, busy }: { d: Dossier; submit: Submit; busy: boolean }) {
  const faults = useLoad(() => api<Fault[]>(`/faults/?device_type=${d.device.device_type}`), [d.device.device_type]);
  const parts = useLoad(() => api<Part[]>("/parts/"));
  const [nParts, setNParts] = useState(0);

  const onSubmit = (action: string, build: (f: FormData) => unknown) => (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    return submit(action, build(new FormData(e.currentTarget)));
  };
  const submitBtn = (label: string) => <Button type="submit" disabled={busy}>{busy ? "Enregistrement…" : label}</Button>;

  switch (d.status) {
    case "RECU":
      return (
        <form className="space-y-3" onSubmit={onSubmit("disinfection", (f) => ({
          product: f.get("product"), comment: f.get("comment"), validated: f.get("validated") === "on" }))}>
          <Field label="Produit / méthode"><Input name="product" /></Field>
          <Field label="Commentaire"><Textarea name="comment" /></Field>
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" name="validated" defaultChecked className="h-4 w-4" /> Désinfection réalisée et validée
          </label>
          {submitBtn("Valider la désinfection")}
        </form>
      );
    case "DESINFECTE":
      return (
        <form className="space-y-3" onSubmit={onSubmit("diagnosis", (f) => ({
          comment: f.get("comment"),
          faults: (faults.data ?? []).filter((x) => f.get(`fault-${x.id}`) === "on").map((x) => ({
            fault: x.id, severity: f.get(`sev-${x.id}`) })),
        }))}>
          <p className="text-sm font-medium text-slate-700">Pannes détectées</p>
          {faults.data?.length === 0 && <p className="text-sm text-slate-500">Aucune panne au catalogue pour ce type : le Responsable SAV peut en ajouter.</p>}
          <ul className="space-y-2">
            {faults.data?.filter((x) => x.active).map((x) => (
              <li key={x.id} className="flex items-center justify-between gap-3 rounded-md border border-slate-200 px-3 py-2">
                <label className="flex items-center gap-2 text-sm"><input type="checkbox" name={`fault-${x.id}`} className="h-4 w-4" />{x.name}</label>
                <Select name={`sev-${x.id}`} defaultValue="MAJEURE" aria-label={`Gravité ${x.name}`} className="!w-36">
                  <option value="MINEURE">Mineure</option><option value="MAJEURE">Majeure</option><option value="CRITIQUE">Critique</option>
                </Select>
              </li>
            ))}
          </ul>
          <Field label="Observations"><Textarea name="comment" /></Field>
          {submitBtn("Terminer le diagnostic")}
        </form>
      );
    case "DIAGNOSTIC_TERMINE":
      return (
        <form className="space-y-3" onSubmit={onSubmit("repair", (f) => ({
          started_at: toIso(f.get("started_at")), ended_at: toIso(f.get("ended_at")),
          tests: f.get("tests"), comment: f.get("comment"),
          parts: Array.from({ length: nParts }, (_, i) => ({ part: Number(f.get(`part-${i}`)), quantity: Number(f.get(`qty-${i}`)) }))
            .filter((p) => p.part),
        }))}>
          <div className="grid gap-3 sm:grid-cols-2">
            <Field label="Début *"><Input type="datetime-local" name="started_at" required /></Field>
            <Field label="Fin *"><Input type="datetime-local" name="ended_at" required /></Field>
          </div>
          <div className="space-y-2">
            <p className="text-sm font-medium text-slate-700">Pièces remplacées</p>
            {Array.from({ length: nParts }, (_, i) => (
              <div key={i} className="flex gap-2">
                <Select name={`part-${i}`} aria-label="Pièce"><option value="">Choisir…</option>
                  {parts.data?.map((p) => <option key={p.id} value={p.id}>{p.reference} · {p.name}</option>)}
                </Select>
                <Input type="number" name={`qty-${i}`} min={1} defaultValue={1} aria-label="Quantité" className="!w-24" />
              </div>
            ))}
            <Button type="button" variant="ghost" onClick={() => setNParts(nParts + 1)}>Ajouter une pièce</Button>
          </div>
          <Field label="Tests effectués"><Textarea name="tests" /></Field>
          <Field label="Commentaire"><Textarea name="comment" /></Field>
          {submitBtn("Enregistrer la réparation")}
        </form>
      );
    case "REPARE":
      return (
        <form className="space-y-3" onSubmit={onSubmit("quality-control", (f) => ({
          checklist: Object.fromEntries(QC_CHECKLIST.map((i) => [i, f.get(`qc-${i}`) === "on"])),
          comment: f.get("comment") }))}>
          <fieldset className="grid gap-2 sm:grid-cols-2">
            <legend className="mb-1 text-sm font-medium text-slate-700">Checklist (cocher si conforme)</legend>
            {QC_CHECKLIST.map((i) => (
              <label key={i} className="flex items-center gap-2 rounded-md border border-slate-200 px-3 py-2 text-sm">
                <input type="checkbox" name={`qc-${i}`} className="h-4 w-4" />{i}
              </label>
            ))}
          </fieldset>
          <Field label="Commentaire (obligatoire si non conforme)"><Textarea name="comment" /></Field>
          {submitBtn("Valider le contrôle")}
        </form>
      );
    case "QC_VALIDE":
      return (
        <form className="space-y-3" onSubmit={onSubmit("stock-entry", (f) => ({ location: f.get("location") }))}>
          <Field label="Emplacement *"><Input name="location" required /></Field>
          {submitBtn("Placer en stock livrable")}
        </form>
      );
    case "EN_STOCK":
      return (
        <form className="space-y-3" onSubmit={onSubmit("delivery", (f) => ({
          recipient: f.get("recipient"), delivery_note: f.get("delivery_note"), comment: f.get("comment") }))}>
          <Field label="Destinataire *"><Input name="recipient" required /></Field>
          <Field label="N° de bon de livraison"><Input name="delivery_note" /></Field>
          <Field label="Commentaire"><Textarea name="comment" /></Field>
          {submitBtn("Enregistrer la livraison")}
        </form>
      );
    default:
      return <p className="text-sm text-slate-600">Ce dossier est terminé.</p>;
  }
}

export default function DossierPage() {
  const { id } = useParams<{ id: string }>();
  const { data: d, error, reload } = useLoad(() => api<Dossier>(`/dossiers/${id}/`), [id]);
  const [actionError, setActionError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const submit: Submit = async (action, body) => {
    setBusy(true); setActionError(null);
    try {
      await api(`/dossiers/${id}/${action}/`, { method: "POST", json: body });
      reload();
    } catch (e) {
      setActionError((e as Error).message);
    } finally {
      setBusy(false);
    }
  };

  async function upload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    const fd = new FormData();
    fd.append("image", file);
    fd.append("kind", "AUTRE");
    setBusy(true); setActionError(null);
    try {
      await api(`/dossiers/${id}/photos/`, { method: "POST", body: fd });
      reload();
    } catch (err) {
      setActionError((err as Error).message);
    } finally {
      setBusy(false); e.target.value = "";
    }
  }

  if (error) return <ErrorMsg error={error} />;
  if (!d) return <p className="text-slate-600">Chargement…</p>;

  return (
    <>
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <h1 className="text-xl font-bold text-slate-900">{d.reference}</h1>
          <p className="text-sm text-slate-600">
            <Link className="text-sky-700 underline" href={`/devices/${d.device.id}`}>{d.device.internal_code}</Link>
            {" · "}N° série {d.device.serial_number} · {d.device.type_name}
          </p>
        </div>
        <StatusBadge status={d.status} />
      </div>
      <Stepper status={d.status} />
      {d.biohazard && <p className="rounded-md bg-red-50 px-3 py-2 text-sm font-medium text-red-800">Risque biologique signalé à la réception.</p>}

      <Card title={`Étape suivante : ${NEXT_STEP[d.status]}`}>
        <ErrorMsg error={actionError} />
        <div className="mt-2"><StepForm key={d.status} d={d} submit={submit} busy={busy} /></div>
      </Card>

      <Card title="Réception">
        <dl className="grid gap-2 text-sm sm:grid-cols-2">
          <div><dt className="text-slate-500">Reçu le</dt><dd>{fmt(d.received_at)}</dd></div>
          <div><dt className="text-slate-500">Commercial</dt><dd>{d.commercial || "–"}</dd></div>
          <div><dt className="text-slate-500">État visuel</dt><dd>{d.visual_state || "–"}</dd></div>
          <div><dt className="text-slate-500">Accessoires manquants</dt><dd>{d.missing_accessories || "–"}</dd></div>
        </dl>
      </Card>

      {d.diagnosis && (
        <Card title="Diagnostic">
          <ul className="text-sm">
            {d.diagnosis.faults.map((f) => <li key={f.name}>{f.name} <span className="text-slate-500">({f.severity.toLowerCase()})</span></li>)}
            {d.diagnosis.faults.length === 0 && <li className="text-slate-500">Aucune panne détectée.</li>}
          </ul>
          {d.diagnosis.comment && <p className="mt-2 text-sm text-slate-700">{d.diagnosis.comment}</p>}
        </Card>
      )}
      {d.repair && (
        <Card title="Réparation">
          <p className="text-sm">Durée : <strong>{d.repair.duration_minutes} min</strong></p>
          <ul className="mt-1 text-sm">
            {d.repair.parts.map((p) => <li key={p.reference}>{p.quantity} × {p.reference} · {p.name}</li>)}
          </ul>
        </Card>
      )}
      {!!d.quality_controls?.length && (
        <Card title="Contrôles qualité">
          <ul className="space-y-1 text-sm">
            {d.quality_controls.map((q) => (
              <li key={q.id}>{fmt(q.at)} · <strong className={q.result === "CONFORME" ? "text-emerald-700" : "text-red-700"}>
                {q.result === "CONFORME" ? "Conforme" : "Non conforme"}</strong>{q.comment && ` · ${q.comment}`}</li>
            ))}
          </ul>
        </Card>
      )}

      <Card title={`Photos (${d.photos?.length ?? 0})`}>
        <div className="flex flex-wrap gap-2">
          {d.photos?.map((p) => (
            // eslint-disable-next-line @next/next/no-img-element
            <img key={p.id} src={p.image} alt="Photo du dossier" className="h-24 w-24 rounded-md object-cover" />
          ))}
        </div>
        <label className="mt-3 block text-sm">
          <span className="mb-1 block font-medium text-slate-700">Ajouter une photo (JPEG, PNG, WebP · 5 Mo max)</span>
          <input type="file" accept="image/jpeg,image/png,image/webp" onChange={upload} disabled={busy} />
        </label>
      </Card>

      <Card title="Historique">
        <ol className="space-y-2 border-l-2 border-slate-200 pl-4 text-sm">
          {[...(d.history ?? [])].reverse().map((h) => (
            <li key={h.id}>
              <p className="text-xs text-slate-500">{fmt(h.at)} · {h.user_name || "—"}</p>
              <p>{h.comment || `${h.from_status} → ${h.to_status}`}</p>
            </li>
          ))}
        </ol>
      </Card>
    </>
  );
}
