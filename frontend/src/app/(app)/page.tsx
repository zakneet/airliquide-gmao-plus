"use client";
import Link from "next/link";
import { api } from "@/lib/api";
import { Card, ErrorMsg, StatusBadge, useLoad } from "@/components/ui";
import { STATUSES, type DashboardData } from "@/lib/types";

function Kpi({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <p className="text-sm text-slate-600">{label}</p>
      <p className="mt-1 text-2xl font-semibold text-slate-900">{value}</p>
    </div>
  );
}

export default function DashboardPage() {
  const { data, error } = useLoad(() => api<DashboardData>("/dashboard/"));
  return (
    <>
      <h1 className="text-xl font-bold text-slate-900">Tableau de bord SAV</h1>
      <ErrorMsg error={error} />
      {data && (
        <>
          <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
            <Kpi label="Dossiers ouverts" value={data.open_dossiers} />
            <Kpi label="En stock livrable" value={data.in_stock} />
            <Kpi label="Risque biologique (ouverts)" value={data.biohazard_open} />
            <Kpi label="Durée moyenne de réparation" value={data.avg_repair_minutes === null ? "–" : `${data.avg_repair_minutes} min`} />
          </div>
          <Card title="Répartition par étape">
            <ul className="grid gap-2 sm:grid-cols-2">
              {STATUSES.map((s) => (
                <li key={s.value}>
                  <Link href={`/dossiers?status=${s.value}`} className="flex items-center justify-between rounded-md border border-slate-200 px-3 py-2 hover:bg-slate-50">
                    <StatusBadge status={s.value} />
                    <span className="font-semibold">{data.by_status[s.value]}</span>
                  </Link>
                </li>
              ))}
            </ul>
          </Card>
          <div className="grid gap-4 md:grid-cols-2">
            <Card title="Pannes les plus fréquentes">
              {data.top_faults.length === 0 ? <p className="text-sm text-slate-500">Aucune donnée.</p> : (
                <ul className="space-y-1 text-sm">
                  {data.top_faults.map((f) => (
                    <li key={f.name} className="flex justify-between"><span>{f.name}</span><span className="font-medium">{f.count}</span></li>
                  ))}
                </ul>
              )}
            </Card>
            <Card title="Contrôle qualité">
              <p className="text-sm text-slate-700">
                {data.qc_total} contrôle(s) · taux de non-conformité :{" "}
                <strong>{data.qc_failure_rate === null ? "–" : `${data.qc_failure_rate} %`}</strong>
              </p>
            </Card>
          </div>
        </>
      )}
    </>
  );
}
