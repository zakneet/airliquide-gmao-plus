"use client";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import { ShieldAlert } from "lucide-react";
import { api } from "@/lib/api";
import { age, EmptyState, ErrorMsg, fmt, Input, PageTitle, Select, StatusBadge, useLoad } from "@/components/kit";
import { NEXT_STEP, STATUSES, type Dossier } from "@/lib/types";

function List() {
  const params = useSearchParams();
  const router = useRouter();
  const status = params.get("status") ?? "";
  const [search, setSearch] = useState("");
  const { data, error } = useLoad(
    () => api<Dossier[]>(`/dossiers/${status ? `?status=${status}` : ""}`), [status]);

  const term = search.trim();
  const rows = (data ?? []).filter((d) =>
    !term ||
    d.device.serial_number.includes(term.replace(/\s+/g, "").toUpperCase()) ||
    d.reference.toLowerCase().includes(term.toLowerCase()));

  return (
    <>
      <PageTitle sub={`${rows.length} dossier(s)`}>Dossiers SAV</PageTitle>
      <div className="flex flex-col gap-3 sm:flex-row">
        <Input aria-label="Rechercher" placeholder="N° de série ou référence" value={search}
          onChange={(e) => setSearch(e.target.value)} className="ident sm:max-w-xs" />
        <Select aria-label="Filtrer par statut" value={status} className="sm:max-w-56"
          onChange={(e) => router.replace(e.target.value ? `/dossiers?status=${e.target.value}` : "/dossiers")}>
          <option value="">Tous les statuts</option>
          {STATUSES.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
        </Select>
      </div>
      <ErrorMsg error={error} />

      <div className="overflow-x-auto rounded-lg border border-border bg-card">
        <table className="w-full min-w-[720px] border-collapse text-sm">
          <thead>
            <tr className="border-b border-border bg-muted text-left text-xs font-semibold">
              <th scope="col" className="px-4 py-2.5">N° de série</th>
              <th scope="col" className="px-4 py-2.5">Dossier</th>
              <th scope="col" className="px-4 py-2.5">Type</th>
              <th scope="col" className="px-4 py-2.5">Statut</th>
              <th scope="col" className="px-4 py-2.5">Prochaine étape</th>
              <th scope="col" className="px-4 py-2.5">Reçu</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((d) => (
              <tr key={d.id} className="border-b border-border last:border-0 hover:bg-muted/60">
                <td className="px-4 py-3">
                  <Link href={`/dossiers/${d.id}`} className="ident font-medium text-primary hover:underline">
                    {d.device.serial_number}
                  </Link>
                  {d.biohazard && (
                    <span className="ml-2 inline-flex items-center gap-1 text-xs font-medium text-danger">
                      <ShieldAlert className="size-3.5" aria-hidden />Risque bio.
                    </span>
                  )}
                </td>
                <td className="ident px-4 py-3 text-muted-foreground">{d.reference}</td>
                <td className="px-4 py-3">{d.device.type_name}</td>
                <td className="px-4 py-3"><StatusBadge status={d.status} /></td>
                <td className="px-4 py-3 text-muted-foreground">{NEXT_STEP[d.status]}</td>
                <td className="px-4 py-3 text-muted-foreground" title={fmt(d.received_at)}>il y a {age(d.received_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {data && rows.length === 0 && <div className="p-4"><EmptyState>Aucun dossier.</EmptyState></div>}
      </div>
    </>
  );
}

export default function DossiersPage() {
  return <Suspense><List /></Suspense>;
}
