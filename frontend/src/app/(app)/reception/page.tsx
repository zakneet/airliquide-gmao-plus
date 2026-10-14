"use client";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { api } from "@/lib/api";
import { Button, Card, ErrorMsg, Field, Input, Select, Textarea, useLoad } from "@/components/kit";
import type { DeviceModel, Dossier, Option } from "@/lib/types";

export default function ReceptionPage() {
  const router = useRouter();
  const types = useLoad(() => api<Option[]>("/device-types/"));
  const models = useLoad(() => api<DeviceModel[]>("/device-models/"));
  const [typeId, setTypeId] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    const body: Record<string, unknown> = {
      serial_number: f.get("serial_number"),
      device_type: Number(f.get("device_type")),
      model: f.get("model") ? Number(f.get("model")) : null,
      commercial: f.get("commercial"),
      visual_state: f.get("visual_state"),
      missing_accessories: f.get("missing_accessories"),
      biohazard: f.get("biohazard") === "on",
      comment: f.get("comment"),
    };
    setBusy(true);
    try {
      const d = await api<Dossier>("/dossiers/reception/", { method: "POST", json: body });
      router.push(`/dossiers/${d.id}`);
    } catch (err) {
      setError((err as Error).message);
      setBusy(false);
    }
  }

  const filtered = (models.data ?? []).filter((m) => String(m.device_type) === typeId);

  return (
    <>
      <h1 className="text-2xl font-semibold">Nouveau retour SAV</h1>
      <Card>
        <form onSubmit={submit} className="grid gap-4 sm:grid-cols-2">
          <div className="sm:col-span-2"><ErrorMsg error={error ?? types.error} /></div>
          <Field label="Numéro de série *"><Input name="serial_number" required autoFocus /></Field>
          <Field label="Type d'appareil *">
            <Select name="device_type" required value={typeId} onChange={(e) => setTypeId(e.target.value)}>
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
          <Field label="Commercial"><Input name="commercial" /></Field>
          <Field label="État visuel"><Input name="visual_state" /></Field>
          <Field label="Accessoires manquants"><Input name="missing_accessories" /></Field>
          <label className="flex items-center gap-2 text-sm sm:col-span-2">
            <input type="checkbox" name="biohazard" className="h-4 w-4" />
            Risque biologique signalé
          </label>
          <div className="sm:col-span-2"><Field label="Commentaire"><Textarea name="comment" /></Field></div>
          <div className="sm:col-span-2">
            <Button type="submit" disabled={busy}>{busy ? "Enregistrement…" : "Enregistrer la réception"}</Button>
          </div>
        </form>
      </Card>
    </>
  );
}
