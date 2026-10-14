"use client";
import Link from "next/link";
import { useSearchParams, useRouter } from "next/navigation";
import { Suspense } from "react";
import { api } from "@/lib/api";
import { Card, ErrorMsg, fmt, Select, StatusBadge, useLoad } from "@/components/kit";
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
        <h1 className="text-2xl font-semibold">Dossiers SAV</h1>
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
        {data?.length === 0 && <p className="text-sm text-muted-foreground">Aucun dossier.</p>}
        <ul className="divide-y divide-border">
          {data?.map((d) => (
            <li key={d.id}>
              <Link href={`/dossiers/${d.id}`} className="flex flex-wrap items-center justify-between gap-2 py-3 hover:bg-muted">
                <div>
                  <p className="font-medium"><span>{d.reference}</span> · <span className="ident">{d.device.serial_number}</span></p>
                  <p className="text-sm text-muted-foreground">
                    {d.device.type_name}{d.biohazard && <span className="ml-2 font-medium text-danger">Risque biologique</span>}
                  </p>
                </div>
                <div className="text-right">
                  <StatusBadge status={d.status} />
                  <p className="mt-1 text-xs text-muted-foreground">{fmt(d.received_at)}</p>
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
