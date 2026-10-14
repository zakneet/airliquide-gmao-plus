"use client";
import Link from "next/link";
import { useSearchParams, useRouter } from "next/navigation";
import { Suspense } from "react";
import { api } from "@/lib/api";
import { Card, ErrorMsg, fmt, Select, StatusBadge, useLoad } from "@/components/ui";
import { STATUSES, type Dossier } from "@/lib/types";

function List() {
  const params = useSearchParams();
  const router = useRouter();
  const status = params.get("status") ?? "";
  const { data, error } = useLoad(
    () => api<Dossier[]>(`/dossiers/${status ? `?status=${status}` : ""}`), [status]);

  return (
    <>
      <div className="flex items-center justify-between gap-3">
        <h1 className="text-xl font-bold text-slate-900">Dossiers SAV</h1>
        <div className="w-52">
          <Select aria-label="Filtrer par statut" value={status}
            onChange={(e) => router.replace(e.target.value ? `/dossiers?status=${e.target.value}` : "/dossiers")}>
            <option value="">Tous les statuts</option>
            {STATUSES.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
          </Select>
        </div>
      </div>
      <ErrorMsg error={error} />
      <Card>
        {data?.length === 0 && <p className="text-sm text-slate-500">Aucun dossier.</p>}
        <ul className="divide-y divide-slate-100">
          {data?.map((d) => (
            <li key={d.id}>
              <Link href={`/dossiers/${d.id}`} className="flex flex-wrap items-center justify-between gap-2 py-3 hover:bg-slate-50">
                <div>
                  <p className="font-medium text-slate-900">{d.reference} · {d.device.serial_number}</p>
                  <p className="text-sm text-slate-600">
                    {d.device.type_name}{d.biohazard && <span className="ml-2 font-medium text-red-700">Risque biologique</span>}
                  </p>
                </div>
                <div className="text-right">
                  <StatusBadge status={d.status} />
                  <p className="mt-1 text-xs text-slate-500">{fmt(d.received_at)}</p>
                </div>
              </Link>
            </li>
          ))}
        </ul>
      </Card>
    </>
  );
}

export default function DossiersPage() {
  return <Suspense><List /></Suspense>;
}
