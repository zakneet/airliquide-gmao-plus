from django.db.models import Avg, Count, F
from rest_framework.response import Response
from rest_framework.views import APIView

from maintenance.models import (DetectedFault, DossierSAV, QualityControl, Repair)


class DashboardView(APIView):
    """Indicateurs SAV pour le tableau de bord."""

    def get(self, request):
        by_status = {s.value: 0 for s in DossierSAV.Status}
        for row in DossierSAV.objects.values('status').annotate(n=Count('id')):
            by_status[row['status']] = row['n']
        durations = Repair.objects.annotate(d=F('ended_at') - F('started_at')).aggregate(avg=Avg('d'))
        avg = durations['avg']
        qc_total = QualityControl.objects.count()
        qc_fail = QualityControl.objects.filter(result=QualityControl.Result.NON_CONFORME).count()
        top_faults = (DetectedFault.objects.values(name=F('fault__name'))
                      .annotate(count=Count('id')).order_by('-count')[:5])
        return Response({
            'by_status': by_status,
            'open_dossiers': sum(n for s, n in by_status.items() if s != 'LIVRE'),
            'in_stock': by_status['EN_STOCK'],
            'biohazard_open': DossierSAV.objects.exclude(status='LIVRE').filter(biohazard=True).count(),
            'avg_repair_minutes': round(avg.total_seconds() / 60) if avg else None,
            'qc_total': qc_total,
            'qc_failure_rate': round(100 * qc_fail / qc_total, 1) if qc_total else None,
            'top_faults': list(top_faults),
        })
