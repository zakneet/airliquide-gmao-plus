"use client";
import Link from "next/link";
import { ArrowUpRight, Clock, ShieldAlert } from "lucide-react";
import { api } from "@/lib/api";
import { age, ageHours, EmptyState, ErrorMsg, ListSkeleton, PageTitle, Skeleton, StatusBadge, useLoad } from "@/components/kit";
import { NEXT_STEP, type DashboardData, type Dossier, type Status } from "@/lib/types";

/** Chaque poste du circuit est nommé par l'action attendue de l'atelier. */
const STATIONS: { status: Status; action: string }[] = [
  { status: "RECU", action: "À désinfecter" },
  { status: "DESINFECTE", action: "À diagnostiquer" },
  { status: "DIAGNOSTIC_TERMINE", action: "À réparer" },
  { status: "REPARE", action: "À contrôler" },
  { status: "QC_VALIDE", action: "À mettre en stock" },
  { status: "EN_STOCK", action: "À livrer" },
];

const OLD_AFTER_HOURS = 72; // hypothèse : au-delà de 3 jours, un dossier est signalé comme ancien.

const today = new Date().toLocaleDateString("fr-FR", { weekday: "long", day: "numeric", month: "long" });

function Workload({ byStatus }: { byStatus: Record<Status, number> }) {
  const max = Math.max(1, ...STATIONS.map((s) => byStatus[s.status]));
  return (
    <ol className="grid grid-cols-3 gap-y-6 sm:grid-cols-6" aria-label="Charge par poste">
      {STATIONS.map((s, i) => {
        const n = byStatus[s.status];
        const pct = n === 0 ? 0 : Math.max(8, Math.round((n / max) * 100));
        return (
          <li key={s.status}>
            <Link
              href={`/dossiers?status=${s.status}`}
              title={`${n} dossier(s) · ${s.action.toLowerCase()}`}
              className="group block rounded-lg px-1 pb-2 pt-1 transition-colors hover:bg-muted"
            >
              <span className="block text-3xl font-semibold tabular-nums leading-none">{n}</span>
              <span className="mt-3 flex h-28 items-end border-b border-border">
                {n > 0 && (
                  <span
                    className="bar-rise block w-full max-w-14 rounded-t-[4px] bg-bar transition-colors duration-150 group-hover:bg-primary"
                    style={{ height: `${pct}%`, ["--i" as string]: i }}
                  />
                )}
              </span>
              <span className="mt-2 block text-sm font-medium leading-snug">{s.action}</span>
            </Link>
          </li>
        );
      })}
    </ol>
  );
}

function Facts({ data }: { data: DashboardData }) {
  const rows: [string, string][] = [
    ["Dossiers ouverts", String(data.open_dossiers)],
    ["Livrés", String(data.by_status.LIVRE)],
    ["Risque biologique en cours", String(data.biohazard_open)],
    ["Réparation moyenne", data.avg_repair_minutes === null ? "–" : `${data.avg_repair_minutes} min`],
    ["Non-conformité au contrôle", data.qc_failure_rate === null ? "–" : `${data.qc_failure_rate} % (${data.qc_total})`],
  ];
  return (
    <dl className="divide-y divide-border">
      {rows.map(([k, v]) => (
        <div key={k} className="flex items-baseline justify-between gap-4 py-2.5">
          <dt className="text-sm text-muted-foreground">{k}</dt>
          <dd className="font-semibold tabular-nums">{v}</dd>
        </div>
      ))}
    </dl>
  );
}

function TopFaults({ faults }: { faults: DashboardData["top_faults"] }) {
  if (faults.length === 0) return <EmptyState>Aucun diagnostic enregistré.</EmptyState>;
  const max = Math.max(...faults.map((f) => f.count));
  return (
    <ul className="space-y-3">
      {faults.map((f) => (
        <li key={f.name}>
          <div className="mb-1 flex justify-between text-sm">
            <span>{f.name}</span>
            <span className="font-semibold tabular-nums">{f.count}</span>
          </div>
          <div className="h-2 rounded-[2px] bg-muted">
            <div className="h-2 rounded-r-[4px] rounded-l-[2px] bg-bar" style={{ width: `${(f.count / max) * 100}%` }} />
          </div>
        </li>
      ))}
    </ul>
  );
}

export default function DashboardPage() {
  const stats = useLoad(() => api<DashboardData>("/dashboard/"));
  const dossiers = useLoad(() => api<Dossier[]>("/dossiers/"));
  const data = stats.data;

  const queue = (dossiers.data ?? [])
    .filter((d) => d.status !== "LIVRE")
    .sort((a, b) => +new Date(a.received_at) - +new Date(b.received_at))
    .slice(0, 8);

  return (
    <>
      <PageTitle
        sub={data ? `${data.open_dossiers} dossier(s) ouvert(s) dans l'atelier.` : "Chargement de l'activité…"}
        actions={
          <Link href="/reception"
            className="inline-flex h-11 items-center rounded-lg bg-primary px-4 text-sm font-medium text-primary-foreground transition-[transform,background-color] duration-100 hover:bg-primary/90 active:scale-[0.97]">
            Nouveau retour
          </Link>
        }
      >
        <span className="first-letter:uppercase">{today}</span>
      </PageTitle>

      <ErrorMsg error={stats.error ?? dossiers.error} />

      <section aria-labelledby="charge">
        <h2 id="charge" className="mb-3 text-base font-semibold">Charge de l&apos;atelier</h2>
        {data ? <Workload byStatus={data.by_status} /> : (
          <div className="grid grid-cols-3 gap-4 sm:grid-cols-6">
            {Array.from({ length: 6 }, (_, i) => <Skeleton key={i} className="h-44" />)}
          </div>
        )}
      </section>

      <div className="grid gap-10 lg:grid-cols-[minmax(0,1.7fr)_minmax(0,1fr)]">
        <section aria-labelledby="queue">
          <div className="mb-3 flex items-baseline justify-between">
            <h2 id="queue" className="text-base font-semibold">À traiter en premier</h2>
            <Link href="/dossiers" className="inline-flex items-center gap-1 text-sm font-medium text-link hover:underline">
              Tous les dossiers<ArrowUpRight className="size-3.5" aria-hidden />
            </Link>
          </div>
          {dossiers.loading && <ListSkeleton rows={5} />}
          {dossiers.data && queue.length === 0 && <EmptyState>Aucun dossier ouvert. L&apos;atelier est à jour.</EmptyState>}
          <ul className="divide-y divide-border border-y border-border">
            {queue.map((d) => {
              const hours = ageHours(d.received_at);
              const old = hours >= OLD_AFTER_HOURS;
              return (
                <li key={d.id}>
                  <Link
                    href={`/dossiers/${d.id}`}
                    className="-mx-2 flex min-h-[3.75rem] items-center justify-between gap-4 rounded-md px-2 py-2.5 transition-colors duration-150 hover:bg-muted"
                  >
                    <div className="min-w-0">
                      <p className="flex flex-wrap items-center gap-x-3 gap-y-0.5">
                        <span className="ident font-medium">{d.device.serial_number}</span>
                        {d.biohazard && (
                          <span className="inline-flex items-center gap-1 text-xs font-medium text-danger">
                            <ShieldAlert className="size-3.5" aria-hidden />Risque biologique
                          </span>
                        )}
                      </p>
                      <p className="truncate text-sm text-muted-foreground">
                        {d.device.type_name} · {NEXT_STEP[d.status]}
                      </p>
                    </div>
                    <div className="flex shrink-0 items-center gap-4">
                      <span className="hidden sm:block"><StatusBadge status={d.status} /></span>
                      <span className={`inline-flex w-14 items-center justify-end gap-1 text-sm tabular-nums ${old ? "font-semibold text-warn" : "text-muted-foreground"}`}>
                        {old && <Clock className="size-3.5" aria-hidden />}
                        <span className="sr-only">Ancienneté : </span>{age(d.received_at)}
                      </span>
                    </div>
                  </Link>
                </li>
              );
            })}
          </ul>
        </section>

        <div className="space-y-9">
          <section aria-labelledby="facts">
            <h2 id="facts" className="mb-1 text-base font-semibold">En chiffres</h2>
            {data ? <Facts data={data} /> : <ListSkeleton rows={4} />}
          </section>
          <section aria-labelledby="faults">
            <h2 id="faults" className="mb-3 text-base font-semibold">Pannes les plus fréquentes</h2>
            {data ? <TopFaults faults={data.top_faults} /> : <ListSkeleton rows={3} />}
          </section>
        </div>
      </div>
    </>
  );
}
