"use client";
import Link from "next/link";
import { useState } from "react";
import { api } from "@/lib/api";
import { Card, ErrorMsg, Input, useLoad } from "@/components/ui";
import type { Device } from "@/lib/types";

export default function DevicesPage() {
  const [q, setQ] = useState("");
  const { data, error } = useLoad(() => api<Device[]>(`/devices/?search=${encodeURIComponent(q)}`), [q]);
  return (
    <>
      <h1 className="text-xl font-bold text-slate-900">Appareils</h1>
      <Input aria-label="Rechercher un appareil" placeholder="Numéro de série ou code interne" value={q}
        onChange={(e) => setQ(e.target.value)} />
      <ErrorMsg error={error} />
      <Card>
        {data?.length === 0 && <p className="text-sm text-slate-500">Aucun appareil.</p>}
        <ul className="divide-y divide-slate-100">
          {data?.map((d) => (
            <li key={d.id}>
              <Link href={`/devices/${d.id}`} className="block py-3 hover:bg-slate-50">
                <p className="font-medium text-slate-900">{d.internal_code} · {d.serial_number}</p>
                <p className="text-sm text-slate-600">{d.type_name}{d.model_name ? ` · ${d.model_name}` : ""}</p>
              </Link>
            </li>
          ))}
        </ul>
      </Card>
    </>
  );
}
