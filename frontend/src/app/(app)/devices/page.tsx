"use client";
import Link from "next/link";
import { useState } from "react";
import { api } from "@/lib/api";
import { Card, ErrorMsg, Input, useLoad } from "@/components/kit";
import type { Device } from "@/lib/types";

export default function DevicesPage() {
  const [q, setQ] = useState("");
  const { data, error } = useLoad(() => api<Device[]>(`/devices/?search=${encodeURIComponent(q)}`), [q]);
  return (
    <>
      <h1 className="text-2xl font-semibold">Appareils</h1>
      <Input aria-label="Rechercher un appareil" placeholder="Numéro de série ou code interne" value={q}
        onChange={(e) => setQ(e.target.value)} />
      <ErrorMsg error={error} />
      <Card>
        {data?.length === 0 && <p className="text-sm text-muted-foreground">Aucun appareil.</p>}
        <ul className="divide-y divide-border">
          {data?.map((d) => (
            <li key={d.id}>
              <Link href={`/devices/${d.id}`} className="block py-3 hover:bg-muted">
                <p className="ident font-medium">{d.internal_code} · {d.serial_number}</p>
                <p className="text-sm text-muted-foreground">{d.type_name}{d.model_name ? ` · ${d.model_name}` : ""}</p>
              </Link>
            </li>
          ))}
        </ul>
      </Card>
    </>
  );
}
