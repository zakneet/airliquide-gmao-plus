"use client";
import Link from "next/link";
import { api } from "@/lib/api";
import { Card, ErrorMsg, fmt, useLoad } from "@/components/ui";
import type { Dossier } from "@/lib/types";

interface Movement { id: number; device_code: string; dossier: number; dossier_reference: string; kind: string; location: string; at: string }

export default function StockPage() {
  const stock = useLoad(() => api<Dossier[]>("/dossiers/?status=EN_STOCK"));
  const moves = useLoad(() => api<Movement[]>("/stock-movements/"));
  return (
    <>
      <h1 className="text-xl font-bold text-slate-900">Stock livrable</h1>
      <ErrorMsg error={stock.error ?? moves.error} />
      <Card title={`Appareils disponibles (${stock.data?.length ?? 0})`}>
        {stock.data?.length === 0 && <p className="text-sm text-slate-500">Aucun appareil en stock.</p>}
        <ul className="divide-y divide-slate-100">
          {stock.data?.map((d) => (
            <li key={d.id}>
              <Link href={`/dossiers/${d.id}`} className="flex justify-between py-3 text-sm hover:bg-slate-50">
                <span className="font-medium">{d.device.internal_code} · {d.device.serial_number}</span>
                <span className="text-slate-600">{d.device.type_name}</span>
              </Link>
            </li>
          ))}
        </ul>
      </Card>
      <Card title="Derniers mouvements">
        <ul className="space-y-1 text-sm">
          {moves.data?.slice(0, 30).map((m) => (
            <li key={m.id}>
              <span className="text-slate-500">{fmt(m.at)}</span> · {m.kind === "ENTREE" ? "Entrée" : "Sortie"} · {m.device_code}
              {m.location && ` · ${m.location}`}
            </li>
          ))}
        </ul>
      </Card>
    </>
  );
}
