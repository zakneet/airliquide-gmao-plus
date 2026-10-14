"use client";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import { api } from "@/lib/api";
import {
  Button, Card, ErrorMsg, Field, Input, PageTitle, RadioTiles, Select, Textarea, useLoad,
} from "@/components/kit";
import {
  BIOHAZARD_STATUSES, VISUAL_CONDITIONS, type DeviceModel, type Dossier, type Option, type ReturnDeclaration,
} from "@/lib/types";

function ReceptionForm() {
  const router = useRouter();
  const preselected = useSearchParams().get("return") ?? "";
  const types = useLoad(() => api<Option[]>("/device-types/"));
  const models = useLoad(() => api<DeviceModel[]>("/device-models/"));
  const pending = useLoad(() => api<ReturnDeclaration[]>("/returns/?pending=1"));

  const [declId, setDeclId] = useState(preselected);
  const [serialInput, setSerial] = useState("");
  const [typeId, setTypeId] = useState("");
  const [visualInput, setVisual] = useState<string | null>(null);
  const [bioInput, setBio] = useState<string | null>(null);
  const [missingInput, setMissing] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const decl = pending.data?.find((r) => String(r.id) === declId);

  // Les réponses du questionnaire de retour servent de valeurs par défaut ;
  // une saisie du technicien les remplace.
  const serial = decl ? decl.serial_number : serialInput;
  const visual = visualInput ?? decl?.visual_condition ?? "GOOD";
  const bio = bioInput ?? decl?.biohazard_status ?? "UNKNOWN";
  const missing = missingInput ?? decl?.missing_accessories ?? "";

  function chooseDeclaration(id: string) {
    setDeclId(id);
    setVisual(null); setBio(null); setMissing(null);
  }

  async function submit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    setBusy(true); setError(null);
    try {
      const d = await api<Dossier>("/dossiers/reception/", {
        method: "POST",
        json: {
          return_declaration: decl ? decl.id : null,
          serial_number: serial,
          device_type: Number(typeId),
          model: f.get("model") ? Number(f.get("model")) : null,
          commercial: f.get("commercial"),
          visual_condition: visual,
          biohazard_status: bio,
          visual_state: f.get("visual_state"),
          missing_accessories: missing,
          hour_counter: f.get("hour_counter") || null,
          comment: f.get("comment"),
        },
      });
      router.push(`/dossiers/${d.id}`);
    } catch (err) {
      setError((err as Error).message);
      setBusy(false);
    }
  }

  const filtered = (models.data ?? []).filter((m) => String(m.device_type) === typeId);

  return (
    <form onSubmit={submit} className="space-y-4">
      <ErrorMsg error={error ?? types.error ?? pending.error} />

      <Card title="Retour annoncé">
        <Field label="Questionnaire de retour correspondant (facultatif)">
          <Select value={declId} onChange={(e) => chooseDeclaration(e.target.value)}>
            <option value="">Aucun : saisie manuelle</option>
            {pending.data?.map((r) => (
              <option key={r.id} value={r.id}>{r.return_id} · {r.serial_number}</option>
            ))}
          </Select>
        </Field>
        {decl && (
          <p className="mt-2 text-sm text-muted-foreground">
            Réponses du questionnaire reprises ci-dessous ; vérifiez-les à l&apos;arrivée de l&apos;appareil.
          </p>
        )}
      </Card>

      <Card title="Appareil">
        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Numéro de série *">
            <Input value={serial} onChange={(e) => setSerial(e.target.value)} required autoFocus
              readOnly={!!decl} className="ident" />
          </Field>
          <Field label="Type d'appareil *">
            <Select required value={typeId} onChange={(e) => setTypeId(e.target.value)}>
              <option value="">Choisir…</option>
              {types.data?.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
            </Select>
          </Field>
          <Field label="Modèle">
            <Select name="model" defaultValue="">
              <option value="">Non renseigné</option>
              {filtered.map((m) => <option key={m.id} value={m.id}>{m.name}</option>)}
            </Select>
          </Field>
          <Field label="Compteur horaire (C.H)">
            <Input name="hour_counter" type="number" step="0.1" min="0" inputMode="decimal" className="ident" />
          </Field>
          <Field label="Commercial"><Input name="commercial" /></Field>
        </div>
      </Card>

      <Card title="État à l'arrivée">
        <div className="grid gap-4 md:grid-cols-2">
          <RadioTiles legend="État visuel *" name="visual_condition" options={VISUAL_CONDITIONS}
            value={visual} onChange={setVisual} />
          <RadioTiles legend="Statut biologique *" name="biohazard_status" options={BIOHAZARD_STATUSES}
            value={bio} onChange={setBio} />
          <Field label="Accessoires manquants">
            <Input value={missing} onChange={(e) => setMissing(e.target.value)} />
          </Field>
          <Field label="Précisions sur l'état visuel"><Input name="visual_state" /></Field>
          <div className="md:col-span-2"><Field label="Commentaire"><Textarea name="comment" /></Field></div>
        </div>
        <p className="mt-3 text-sm text-muted-foreground">
          Un statut « Inconnu » ou « Contamination importante » signale le dossier à risque biologique.
        </p>
      </Card>

      <Button type="submit" disabled={busy}>{busy ? "Enregistrement…" : "Enregistrer la réception"}</Button>
    </form>
  );
}

export default function ReceptionPage() {
  return (
    <>
      <PageTitle sub="Créer le dossier SAV d'un appareil qui vient d'arriver.">Nouveau retour</PageTitle>
      <Suspense><ReceptionForm /></Suspense>
    </>
  );
}
