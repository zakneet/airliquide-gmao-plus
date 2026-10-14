"use client";
import Link from "next/link";
import { ArrowRight, ShieldAlert } from "lucide-react";
import { api } from "@/lib/api";
import { age, Card, EmptyState, ErrorMsg, PageTitle, StatusBadge, useLoad } from "@/components/kit";
import { NEXT_STEP, STATUSES, type DashboardData, type Dossier } from "@/lib/types";

function Kpi({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <p className="text-sm text-muted-foreground">{label}</p>
      <p className="mt-1 text-3xl font-semibold tabular-nums">{value}</p>
    </div>
  );
}

export default function DashboardPage() {
  const stats = useLoad(() => api<DashboardData>("/dashboard/"));
  const dossiers = useLoad(() => api<Dossier[]>("/dossiers/"));
  const data = stats.data;

  // Dossiers à traiter : les plus anciens d'abord (priorité atelier).
  const queue = (dossiers.data ?? [])
    .filter((d) => d.status !== "LIVRE")
    .sort((a, b) => +new Date(a.received_at) - +new Date(b.received_at))
    .slice(0, 8);

  return (
    <>
      <PageTitle sub="Ce qui attend un traitement, du plus ancien au plus récent.">Tableau de bord</PageTitle>
      <ErrorMsg error={stats.error ?? dossiers.error} />

      <Card
        title={`À traiter (${data?.open_dossiers ?? "…"})`}
        action={<Link href="/dossiers" className="text-sm font-medium text-primary hover:underline">Voir tous les dossiers</Link>}
      >
        {dossiers.data && queue.length === 0 && <EmptyState>Aucun dossier ouvert.</EmptyState>}
        <ul className="divide-y divide-border">
          {queue.map((d) => (
            <li key={d.id}>
              <Link href={`/dossiers/${d.id}`}
                className="-mx-2 flex min-h-14 flex-wrap items-center justify-between gap-x-4 gap-y-1 rounded-md px-2 py-2.5 hover:bg-muted">
                <div className="min-w-0">
                  <p className="flex items-center gap-2">
                    <span className="ident font-medium">{d.device.serial_number}</span>
                    {d.biohazard && (
                      <span className="inline-flex items-center gap-1 text-xs font-medium text-danger">
                        <ShieldAlert className="size-3.5" aria-hidden />Risque biologique
                      </span>
                    )}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {d.device.type_name} · reçu il y a {age(d.received_at)}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <StatusBadge status={d.status} />
                  <span className="hidden items-center gap-1 text-sm text-primary sm:inline-flex">
                    {NEXT_STEP[d.status]}<ArrowRight className="size-4" aria-hidden />
                  </span>
                </div>
              </Link>
            </li>
          ))}
        </ul>
      </Card>

      {data && (
        <>
          <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
            <Kpi label="Dossiers ouverts" value={data.open_dossiers} />
            <Kpi label="En stock livrable" value={data.in_stock} />
            <Kpi label="Risque biologique ouverts" value={data.biohazard_open} />
            <Kpi label="Réparation moyenne" value={data.avg_repair_minutes === null ? "–" : `${data.avg_repair_minutes} min`} />
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            <Card title="Répartition par étape">
              <ul className="divide-y divide-border">
                {STATUSES.map((s) => (
                  <li key={s.value}>
                    <Link href={`/dossiers?status=${s.value}`}
                      className="-mx-2 flex min-h-11 items-center justify-between rounded-md px-2 hover:bg-muted">
                      <StatusBadge status={s.value} />
                      <span className="font-semibold tabular-nums">{data.by_status[s.value]}</span>
                    </Link>
                  </li>
                ))}
              </ul>
            </Card>
            <div className="space-y-4">
              <Card title="Pannes les plus fréquentes">
                {data.top_faults.length === 0 ? <EmptyState>Aucun diagnostic enregistré.</EmptyState> : (
                  <ul className="divide-y divide-border text-sm">
                    {data.top_faults.map((f) => (
                      <li key={f.name} className="flex justify-between py-2">
                        <span>{f.name}</span><span className="font-medium tabular-nums">{f.count}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </Card>
              <Card title="Contrôle qualité">
                <p className="text-sm">
                  <span className="tabular-nums">{data.qc_total}</span> contrôle(s) · non-conformité :{" "}
                  <strong className="tabular-nums">{data.qc_failure_rate === null ? "–" : `${data.qc_failure_rate} %`}</strong>
                </p>
              </Card>
            </div>
          </div>
        </>
      )}
    </>
  );
}
