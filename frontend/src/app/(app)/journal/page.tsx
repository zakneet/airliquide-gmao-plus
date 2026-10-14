"use client";
import Link from "next/link";
import { useState } from "react";
import { Download, Printer } from "lucide-react";
import { api, downloadCsv } from "@/lib/api";
import { Button, Card, EmptyState, ErrorMsg, Field, Input, PageTitle, Select, useLoad } from "@/components/kit";
import type { JournalRow, Option } from "@/lib/types";

const MONTHS = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"];
const thisYear = new Date().getFullYear();

function dmy(iso: string | null) {
  return iso ? `${iso.slice(8, 10)}/${iso.slice(5, 7)}/${iso.slice(0, 4)}` : "";
}

export default function JournalPage() {
  const [year, setYear] = useState(String(thisYear));
  const [month, setMonth] = useState("");
  const [typeId, setTypeId] = useState("");
  const [search, setSearch] = useState("");
  const [error, setError] = useState<string | null>(null);

  const q = new URLSearchParams();
  if (year) q.set("year", year);
  if (month) q.set("month", month);
  if (typeId) q.set("device_type", typeId);
  if (search.trim()) q.set("search", search.trim());

  const types = useLoad(() => api<Option[]>("/device-types/"));
  const rows = useLoad(() => api<JournalRow[]>(`/journal/?${q}`), [year, month, typeId, search]);

  async function exportCsv() {
    try {
      setError(null);
      await downloadCsv(`/reports/journal.csv?${q}`, "journal_maintenance.csv");
    } catch (e) {
      setError((e as Error).message);
    }
  }

  return (
    <>
      <div className="flex flex-wrap items-start justify-between gap-3 print:hidden">
        <PageTitle sub="Registre des équipements O₂, VNI, CPAP et respirateurs : une ligne par retour SAV.">
          Journal de maintenance
        </PageTitle>
        <div className="flex gap-2">
          <Button variant="ghost" onClick={() => window.print()}><Printer className="mr-2 size-4" aria-hidden />Imprimer</Button>
          <Button variant="ghost" onClick={exportCsv}><Download className="mr-2 size-4" aria-hidden />Export CSV</Button>
        </div>
      </div>

      <Card className="print:hidden">
        <div className="grid gap-3 sm:grid-cols-4">
          <Field label="Année"><Input type="number" value={year} onChange={(e) => setYear(e.target.value)} /></Field>
          <Field label="Mois">
            <Select value={month} onChange={(e) => setMonth(e.target.value)}>
              <option value="">Tous</option>
              {MONTHS.map((m, i) => <option key={m} value={i + 1}>{m}</option>)}
            </Select>
          </Field>
          <Field label="Type d'équipement">
            <Select value={typeId} onChange={(e) => setTypeId(e.target.value)}>
              <option value="">Tous</option>
              {types.data?.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
            </Select>
          </Field>
          <Field label="N° de série"><Input value={search} onChange={(e) => setSearch(e.target.value)} className="ident" /></Field>
        </div>
      </Card>

      <ErrorMsg error={error ?? rows.error} />

      <div className="hidden print:block">
        <h1 className="text-lg font-semibold">Journal de maintenance des équipements O₂, VNI, CPAP et respirateurs</h1>
        <p className="text-xs">AirLiquide GMAO+ · édité le {new Date().toLocaleDateString("fr-FR")}</p>
      </div>

      <div className="overflow-x-auto rounded-lg border border-border bg-card">
        <table className="w-full min-w-[1000px] border-collapse text-sm">
          <thead>
            <tr className="border-b border-border bg-muted text-left">
              {["Année", "Mois", "Équip. / type", "N° série", "C.H", "Pureté", "Débit / pression", "Alarme sonore", "Pannes",
                "Doc sortie PR", "Technicien", "Date sortie"].map((h) => (
                <th key={h} scope="col" className="px-3 py-2.5 text-xs font-semibold">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.data?.map((r) => (
              <tr key={r.dossier_id} className="border-b border-border last:border-0 hover:bg-muted/60">
                <td className="px-3 py-2.5 tabular-nums">{r.year}</td>
                <td className="px-3 py-2.5 tabular-nums">{String(r.month).padStart(2, "0")}</td>
                <td className="px-3 py-2.5">{r.equipment}</td>
                <td className="px-3 py-2.5">
                  <Link href={`/dossiers/${r.dossier_id}`} className="ident font-medium text-link hover:underline">
                    {r.serial_number}
                  </Link>
                </td>
                <td className="ident px-3 py-2.5">{r.hour_counter ?? ""}</td>
                <td className="ident px-3 py-2.5">{r.purity ? `${r.purity} %` : ""}</td>
                <td className="px-3 py-2.5">{r.flow_pressure}</td>
                <td className="px-3 py-2.5">{r.audible_alarm_ok === null ? "" : r.audible_alarm_ok ? "OK" : "Non conforme"}</td>
                <td className="px-3 py-2.5">{r.faults.join(" + ")}</td>
                <td className="ident px-3 py-2.5">{r.parts_exit_document}</td>
                <td className="px-3 py-2.5">{r.technician}</td>
                <td className="px-3 py-2.5 tabular-nums">{dmy(r.exit_date)}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {rows.data?.length === 0 && <div className="p-4"><EmptyState>Aucune ligne pour ces filtres.</EmptyState></div>}
      </div>
    </>
  );
}
