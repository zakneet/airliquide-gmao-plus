import csv

from django.http import HttpResponse
from rest_framework.views import APIView

from accounts.permissions import IsResponsableSAV
from maintenance.models import DossierSAV


def _safe(value):
    """Neutralise l'injection de formules dans les tableurs."""
    s = '' if value is None else str(value)
    return "'" + s if s[:1] in ('=', '+', '-', '@') else s


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
        resp = HttpResponse(content_type='text/csv; charset=utf-8')
        resp['Content-Disposition'] = 'attachment; filename="dossiers_sav.csv"'
        resp.write('﻿')
        w = csv.writer(resp, delimiter=';')
        w.writerow(['Référence', 'Code interne', 'N° série', 'Type', 'Modèle', 'Statut',
                    'Risque biologique', 'Reçu le'])
        for d in qs:
            w.writerow([_safe(x) for x in (
                d.reference, d.device.internal_code, d.device.serial_number,
                d.device.device_type.name, d.device.model or '', d.get_status_display(),
                'Oui' if d.biohazard else 'Non', d.received_at.strftime('%d/%m/%Y %H:%M'))])
        return resp
