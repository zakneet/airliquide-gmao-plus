import csv

from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsResponsableSAV
from maintenance.models import DossierSAV


def _safe(value):
    """Neutralise l'injection de formules dans les tableurs."""
    s = '' if value is None else str(value)
    return "'" + s if s[:1] in ('=', '+', '-', '@') else s


def _csv_response(filename):
    resp = HttpResponse(content_type='text/csv; charset=utf-8')
    resp['Content-Disposition'] = f'attachment; filename="{filename}"'
    resp.write('﻿')
    return resp


class DossiersCsvView(APIView):
    """Export CSV des dossiers SAV (Responsable SAV). Filtres : status, date_from, date_to."""

    permission_classes = [IsResponsableSAV]

    def get(self, request):
        qs = DossierSAV.objects.select_related('device__device_type', 'device__model__brand')
        p = request.query_params
        if p.get('status'):
            qs = qs.filter(status=p['status'])
        if p.get('date_from'):
            qs = qs.filter(received_at__date__gte=p['date_from'])
        if p.get('date_to'):
            qs = qs.filter(received_at__date__lte=p['date_to'])
        resp = _csv_response('dossiers_sav.csv')
        w = csv.writer(resp, delimiter=';')
        w.writerow(['Référence', 'Code interne', 'N° série', 'Type', 'Modèle', 'Statut',
                    'Risque biologique', 'Reçu le'])
        for d in qs:
            w.writerow([_safe(x) for x in (
                d.reference, d.device.internal_code, d.device.serial_number,
                d.device.device_type.name, d.device.model or '', d.get_status_display(),
                'Oui' if d.biohazard else 'Non', d.received_at.strftime('%d/%m/%Y %H:%M'))])
        return resp


# --- Journal de maintenance : équivalent numérique du registre papier ------------------------
# Colonnes : Année, Mois, Équip./type, N° série, C.H, Pureté, Débit/pression, Alarme sonore,
# Pannes, Doc de sortie PR, Technicien, Date sortie.

JOURNAL_COLUMNS = ['Année', 'Mois', 'Équip./type', 'N° série', 'C.H', 'Pureté (%)', 'Débit / pression',
                   'Alarme sonore', 'Pannes', 'Doc de sortie PR', 'Technicien', 'Date sortie']


def _alarm_label(v):
    return '' if v is None else ('OK' if v else 'Non conforme')


def _journal_rows(params):
    qs = (DossierSAV.objects
          .select_related('device__device_type', 'device__model__brand', 'repair__technician',
                          'disinfection__technician', 'diagnosis', 'delivery')
          .prefetch_related('diagnosis__faults__fault', 'quality_controls')
          .order_by('-received_at', '-id'))
    if params.get('year'):
        qs = qs.filter(received_at__year=params['year'])
    if params.get('month'):
        qs = qs.filter(received_at__month=params['month'])
    if params.get('device_type'):
        qs = qs.filter(device__device_type_id=params['device_type'])
    q = params.get('search', '').strip()
    if q:
        qs = qs.filter(device__serial_number__icontains=q)
    rows = []
    for d in qs:
        qc = d.quality_controls.all()
        last_qc = qc[len(qc) - 1] if qc else None
        faults = ([f.fault.name for f in d.diagnosis.faults.all()] if hasattr(d, 'diagnosis') else [])
        repair = getattr(d, 'repair', None)
        tech = repair.technician if repair else getattr(getattr(d, 'disinfection', None), 'technician', None)
        delivery = getattr(d, 'delivery', None)
        rows.append({
            'dossier_id': d.id,
            'reference': d.reference,
            'year': d.received_at.year,
            'month': d.received_at.month,
            'equipment': ' · '.join(x for x in (d.device.device_type.name,
                                                str(d.device.model) if d.device.model else '') if x),
            'serial_number': d.device.serial_number,
            'hour_counter': str(d.hour_counter) if d.hour_counter is not None else None,
            'purity': str(last_qc.purity) if last_qc and last_qc.purity is not None else None,
            'flow_pressure': last_qc.flow_pressure if last_qc else '',
            'audible_alarm_ok': last_qc.audible_alarm_ok if last_qc else None,
            'faults': faults,
            'parts_exit_document': repair.parts_exit_document if repair else '',
            'technician': (tech.get_full_name() or tech.email) if tech else '',
            'exit_date': delivery.at.date().isoformat() if delivery else None,
            'status': d.status,
        })
    return rows


class JournalView(APIView):
    """Journal de maintenance (lecture pour tout utilisateur connecté). Filtres : year, month, device_type, search."""

    def get(self, request):
        return Response(_journal_rows(request.query_params))


class JournalCsvView(APIView):
    def get(self, request):
        resp = _csv_response('journal_maintenance.csv')
        w = csv.writer(resp, delimiter=';')
        w.writerow(JOURNAL_COLUMNS)
        for r in _journal_rows(request.query_params):
            w.writerow([_safe(x) for x in (
                r['year'], f"{r['month']:02d}", r['equipment'], r['serial_number'],
                r['hour_counter'] or '', r['purity'] or '', r['flow_pressure'],
                _alarm_label(r['audible_alarm_ok']), ' + '.join(r['faults']),
                r['parts_exit_document'], r['technician'],
                r['exit_date'][8:] + '/' + r['exit_date'][5:7] + '/' + r['exit_date'][:4] if r['exit_date'] else '')])
        return resp
