"use client";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useState, type ReactNode } from "react";
import { toast } from "sonner";
import {
  BadgeCheck, ClipboardList, ImagePlus, Inbox, Package, ShieldAlert, ShieldCheck, Truck, Wrench,
  type LucideIcon,
} from "lucide-react";
import { api, mediaUrl } from "@/lib/api";
import { cn } from "@/lib/utils";
import { ErrorMsg, fmt, ListSkeleton, StatusBadge, useLoad } from "@/components/kit";
import { StepForm, type Submit } from "@/components/step-forms";
import {
  BIOHAZARD_STATUSES, NEXT_STEP, STATUSES, VISUAL_CONDITIONS, labelOf, type Dossier,
} from "@/lib/types";

const STEPS: { title: string; Icon: LucideIcon; action: string; success: string }[] = [
  { title: "Réception", Icon: Inbox, action: "", success: "" },
  { title: "Désinfection", Icon: ShieldCheck, action: "disinfection", success: "Désinfection validée" },
  { title: "Diagnostic", Icon: ClipboardList, action: "diagnosis", success: "Diagnostic enregistré" },
  { title: "Réparation", Icon: Wrench, action: "repair", success: "Réparation enregistrée" },
  { title: "Contrôle qualité", Icon: BadgeCheck, action: "quality-control", success: "Contrôle qualité enregistré" },
  { title: "Stock livrable", Icon: Package, action: "stock-entry", success: "Appareil placé en stock" },
  { title: "Livraison", Icon: Truck, action: "delivery", success: "Livraison enregistrée" },
];

function Fact({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div>
      <dt className="text-xs text-muted-foreground">{label}</dt>
      <dd className="text-sm">{children}</dd>
    </div>
  );
}

function StepSummary({ i, d }: { i: number; d: Dossier }) {
  switch (i) {
    case 0:
      return (
        <dl className="grid gap-x-6 gap-y-2 sm:grid-cols-2">
          <Fact label="État visuel">
            {labelOf(VISUAL_CONDITIONS, d.visual_condition)}{d.visual_state && ` · ${d.visual_state}`}
          </Fact>
          <Fact label="Statut biologique">{labelOf(BIOHAZARD_STATUSES, d.biohazard_status)}</Fact>
          <Fact label="Compteur horaire (C.H)"><span className="ident">{d.hour_counter ?? "–"}</span></Fact>
          <Fact label="Accessoires manquants">{d.missing_accessories || "Aucun signalé"}</Fact>
          {d.commercial && <Fact label="Commercial">{d.commercial}</Fact>}
          {d.comment && <Fact label="Commentaire">{d.comment}</Fact>}
        </dl>
      );
    case 1:
      return d.disinfection ? (
        <p className="text-sm">
          {d.disinfection.product || "Produit non précisé"}
          {d.disinfection.comment && <span className="text-muted-foreground"> · {d.disinfection.comment}</span>}
        </p>
      ) : null;
    case 2:
      return d.diagnosis ? (
        <div className="space-y-1.5 text-sm">
          {d.diagnosis.faults.length === 0 ? (
            <p className="text-muted-foreground">Aucune panne constatée.</p>
          ) : (
            <ul className="flex flex-wrap gap-1.5">
              {d.diagnosis.faults.map((f) => (
                <li key={f.name}
                  className={cn("rounded-md px-2 py-1 text-xs font-medium",
                    f.severity === "CRITIQUE" ? "bg-danger-soft text-danger"
                      : f.severity === "MAJEURE" ? "bg-warn-soft text-warn" : "bg-muted text-muted-foreground")}>
                  {f.name} · {f.severity.toLowerCase()}
                </li>
              ))}
            </ul>
          )}
          {d.diagnosis.comment && <p className="text-muted-foreground">{d.diagnosis.comment}</p>}
        </div>
      ) : null;
    case 3:
      return d.repair ? (
        <div className="space-y-1 text-sm">
          <p>
            Durée <strong className="tabular-nums">{d.repair.duration_minutes} min</strong>
            {d.repair.parts_exit_document && <> · Doc PR <span className="ident">{d.repair.parts_exit_document}</span></>}
          </p>
          {d.repair.parts.length > 0 && (
            <ul className="text-muted-foreground">
              {d.repair.parts.map((p) => <li key={p.reference}>{p.quantity} × <span className="ident">{p.reference}</span> · {p.name}</li>)}
            </ul>
          )}
          {d.repair.tests && <p className="text-muted-foreground">Tests : {d.repair.tests}</p>}
        </div>
      ) : null;
    case 4:
      return (
        <ul className="space-y-1.5 text-sm">
          {d.quality_controls?.map((q) => (
            <li key={q.id} className="flex flex-wrap items-baseline gap-x-3">
              <strong className={q.result === "CONFORME" ? "text-ok" : "text-danger"}>
                {q.result === "CONFORME" ? "Conforme" : "Non conforme"}
              </strong>
              <span className="text-xs text-muted-foreground">{fmt(q.at)}</span>
              <span className="text-muted-foreground">
                {[q.purity && `pureté ${q.purity} %`, q.flow_pressure,
                  q.audible_alarm_ok === null ? "" : q.audible_alarm_ok ? "alarme OK" : "alarme non conforme"]
                  .filter(Boolean).join(" · ")}
              </span>
              {q.comment && <span className="w-full text-muted-foreground">{q.comment}</span>}
            </li>
          ))}
        </ul>
      );
    case 5: {
      const m = d.stock_movements?.find((x) => x.kind === "ENTREE");
      return m ? <p className="text-sm">Emplacement <span className="ident font-medium">{m.location}</span></p> : null;
    }
    case 6:
      return d.delivery ? (
        <p className="text-sm">
          {d.delivery.recipient}
          {d.delivery.delivery_note && <> · bon <span className="ident">{d.delivery.delivery_note}</span></>}
        </p>
      ) : null;
    default:
      return null;
  }
}

export default function DossierPage() {
  const { id } = useParams<{ id: string }>();
  const { data: d, error, reload } = useLoad(() => api<Dossier>(`/dossiers/${id}/`), [id]);
  const [actionError, setActionError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [justDone, setJustDone] = useState<number>(-1);

  if (error) return <ErrorMsg error={error} />;
  if (!d) return <ListSkeleton rows={6} />;

  const statusIdx = STATUSES.findIndex((s) => s.value === d.status);
  const current = statusIdx + 1; // étape attendue ; 7 = dossier terminé
  const finished = current >= STEPS.length;

  const submit: Submit = async (action, body) => {
    setBusy(true); setActionError(null);
    try {
      const before = d.status;
      const updated = await api<Dossier>(`/dossiers/${id}/${action}/`, { method: "POST", json: body });
      reload();
      if (updated.status !== before) {
        setJustDone(current);
        toast.success(STEPS[current].success);
      } else {
        toast.warning("Contrôle non conforme enregistré : l'appareil reste à l'étape réparation.");
      }
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
      toast.success("Photo ajoutée");
      reload();
    } catch (err) {
      setActionError((err as Error).message);
    } finally {
      setBusy(false); e.target.value = "";
    }
  }

  const stamp = (i: number) => d.history?.find((h) => h.to_status === STATUSES[i].value && h.from_status !== h.to_status);

  return (
    <>
      <header className="space-y-3">
        <div className="flex flex-wrap items-center gap-3">
          <StatusBadge status={d.status} />
          <span className="ident text-sm text-muted-foreground">{d.reference}</span>
        </div>
        <h1 className="ident text-[1.75rem] font-semibold leading-tight">{d.device.serial_number}</h1>
        <p className="text-sm text-muted-foreground">
          {d.device.type_name}{d.device.model_name && ` · ${d.device.model_name}`}
          {" · "}
          <Link href={`/devices/${d.device.id}`} className="text-link hover:underline">
            Fiche de vie <span className="ident">{d.device.internal_code}</span>
          </Link>
        </p>
        {d.biohazard && (
          <p role="note" className="flex items-center gap-2 rounded-md bg-danger-soft px-3 py-2.5 text-sm font-medium text-danger">
            <ShieldAlert className="size-4 shrink-0" aria-hidden />
            Risque biologique : {labelOf(BIOHAZARD_STATUSES, d.biohazard_status).toLowerCase()}. Désinfecter avant toute manipulation.
          </p>
        )}
      </header>

      <div className="grid gap-10 lg:grid-cols-[minmax(0,1fr)_300px]">
        <ol className="relative" aria-label="Parcours du dossier">
          {STEPS.map((step, i) => {
            const done = i < current;
            const isCurrent = i === current && !finished;
            const at = stamp(i);
            const last = i === STEPS.length - 1;
            return (
              <li key={step.title} className="relative flex gap-4 pb-8 last:pb-0" aria-current={isCurrent ? "step" : undefined}>
                {!last && (
                  <span aria-hidden className={cn(
                    "absolute left-[15px] top-9 h-[calc(100%-2.25rem)] w-0.5 rounded-full transition-colors duration-300",
                    i < current - 1 || (i === current - 1 && !finished) ? "bg-primary" : "bg-border",
                  )} />
                )}
                <span aria-hidden className={cn(
                  "z-10 grid size-8 shrink-0 place-items-center rounded-full border-2 transition-colors duration-200",
                  done && "border-primary bg-primary text-primary-foreground",
                  isCurrent && "border-primary bg-card text-primary",
                  !done && !isCurrent && "border-border bg-card text-muted-foreground",
                )}>
                  {done ? (
                    <svg viewBox="0 0 24 24" className="size-4" fill="none" stroke="currentColor" strokeWidth="3"
                      strokeLinecap="round" strokeLinejoin="round">
                      <path d="M5 12.5l4.5 4.5L19 7.5" className={justDone === i ? "check-draw" : undefined} />
                    </svg>
                  ) : <step.Icon className="size-4" />}
                </span>

                <div className="min-w-0 flex-1 pt-0.5">
                  <div className="flex flex-wrap items-baseline justify-between gap-x-4">
                    <h2 className={cn("text-base font-semibold", !done && !isCurrent && "text-muted-foreground")}>
                      {step.title}
                    </h2>
                    {done && (at || i === 0) && (
                      <span className="text-xs text-muted-foreground">
                        {fmt(at?.at ?? d.received_at)}{at?.user_name && ` · ${at.user_name}`}
                      </span>
                    )}
                    {isCurrent && <span className="text-sm font-medium text-link">{NEXT_STEP[STATUSES[statusIdx].value]}</span>}
                  </div>

                  {done && <div className="mt-2"><StepSummary i={i} d={d} /></div>}

                  {isCurrent && (
                    <div key={d.status} className="reveal mt-3">
                      <div>
                        <div className="rounded-lg border border-border bg-card p-4 sm:p-5">
                          <ErrorMsg error={actionError} />
                          {i === 4 && (d.quality_controls?.length ?? 0) > 0 && (
                            <div className="mb-4 rounded-md bg-warn-soft px-3 py-2 text-sm text-warn">
                              <StepSummary i={4} d={d} />
                            </div>
                          )}
                          <div className={actionError ? "mt-3" : ""}>
                            <StepForm d={d} submit={submit} busy={busy} />
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </li>
            );
          })}
        </ol>

        <aside className="space-y-8 lg:sticky lg:top-8 lg:self-start">
          <section aria-labelledby="photos">
            <h2 id="photos" className="mb-2 text-base font-semibold">Photos ({d.photos?.length ?? 0})</h2>
            {(d.photos?.length ?? 0) > 0 && (
              <ul className="mb-3 grid grid-cols-3 gap-2">
                {d.photos?.map((p) => (
                  <li key={p.id}>
                    <a href={mediaUrl(p.image)} target="_blank" rel="noreferrer">
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img src={mediaUrl(p.image)} alt="Photo du dossier" className="aspect-square w-full rounded-md object-cover" />
                    </a>
                  </li>
                ))}
              </ul>
            )}
            <label className={cn(
              "flex min-h-11 cursor-pointer items-center justify-center gap-2 rounded-lg border border-dashed border-input px-3 text-sm transition-colors hover:bg-muted",
              busy && "pointer-events-none opacity-50",
            )}>
              <ImagePlus className="size-4" aria-hidden />
              Ajouter une photo
              <input type="file" accept="image/jpeg,image/png,image/webp" onChange={upload} className="sr-only" />
            </label>
            <p className="mt-1.5 text-xs text-muted-foreground">JPEG, PNG ou WebP · 5 Mo maximum</p>
          </section>

          <section aria-labelledby="hist">
            <h2 id="hist" className="mb-2 text-base font-semibold">Historique</h2>
            <ol className="space-y-2.5 text-sm">
              {[...(d.history ?? [])].reverse().map((h) => (
                <li key={h.id}>
                  <p className="text-xs text-muted-foreground">{fmt(h.at)} · {h.user_name || "—"}</p>
                  <p>{h.comment || `${h.from_status} → ${h.to_status}`}</p>
                </li>
              ))}
            </ol>
          </section>
        </aside>
      </div>
    </>
  );
}
