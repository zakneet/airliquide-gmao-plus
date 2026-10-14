"use client";
import Link from "next/link";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import { Card, ErrorMsg, fmt, StatusBadge, useLoad } from "@/components/ui";
import type { LifeSheet } from "@/lib/types";

export default function LifeSheetPage() {
  const { id } = useParams<{ id: string }>();
  const { data, error } = useLoad(() => api<LifeSheet>(`/devices/${id}/life-sheet/`), [id]);
  if (error) return <ErrorMsg error={error} />;
  if (!data) return <p className="text-slate-600">Chargement…</p>;
  const { device, dossiers, timeline } = data;
  return (
    <>
      <div>
        <h1 className="text-xl font-bold text-slate-900">Fiche de vie · {device.internal_code}</h1>
        <p className="text-sm text-slate-600">
          N° série {device.serial_number} · {device.type_name}{device.model_name ? ` · ${device.model_name}` : ""}
        </p>
      </div>
      <Card title={`Retours SAV (${dossiers.length})`}>
        <ul className="divide-y divide-slate-100">
          {dossiers.map((d) => (
            <li key={d.id}>
              <Link href={`/dossiers/${d.id}`} className="flex items-center justify-between py-3 hover:bg-slate-50">
                <span className="font-medium">{d.reference}</span>
                <span className="flex items-center gap-3">
                  <span className="text-xs text-slate-500">{fmt(d.received_at)}</span>
                  <StatusBadge status={d.status} />
                </span>
              </Link>
            </li>
          ))}
        </ul>
      </Card>
      <Card title="Historique chronologique">
        <ol className="space-y-2 border-l-2 border-slate-200 pl-4 text-sm">
          {[...timeline].reverse().map((h) => (
            <li key={h.id}>
              <p className="text-xs text-slate-500">{fmt(h.at)} · {h.user_name || "—"}</p>
              <p className="text-slate-800">{h.comment || `${h.from_status} → ${h.to_status}`}</p>
            </li>
          ))}
        </ol>
      </Card>
    </>
  );
}
