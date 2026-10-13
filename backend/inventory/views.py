from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.permissions import IsResponsableOrReadOnly
from maintenance.models import StatusHistory
from maintenance.serializers import DossierSerializer, StatusHistorySerializer

from .models import Brand, Device, DeviceModel, DeviceType
from .serializers import (BrandSerializer, DeviceModelSerializer, DeviceSerializer,
                          DeviceTypeSerializer)


class DeviceTypeViewSet(viewsets.ModelViewSet):
    queryset = DeviceType.objects.order_by('name')
    serializer_class = DeviceTypeSerializer
    permission_classes = [IsResponsableOrReadOnly]


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.order_by('name')
    serializer_class = BrandSerializer
    permission_classes = [IsResponsableOrReadOnly]


class DeviceModelViewSet(viewsets.ModelViewSet):
    queryset = DeviceModel.objects.select_related('brand', 'device_type').order_by('brand__name', 'name')
    serializer_class = DeviceModelSerializer
    permission_classes = [IsResponsableOrReadOnly]


class DeviceViewSet(viewsets.ReadOnlyModelViewSet):
    """Appareils : création uniquement via la réception SAV."""

    serializer_class = DeviceSerializer

    def get_queryset(self):
        qs = Device.objects.select_related('device_type', 'model__brand').order_by('-created_at')
        q = self.request.query_params.get('search', '').strip()
        if q:
            qs = qs.filter(Q(serial_number__icontains=q) | Q(internal_code__icontains=q))
        return qs

    @action(detail=True, methods=['get'], url_path='life-sheet')
    def life_sheet(self, request, pk=None):
        """Fiche de vie : appareil, tous ses dossiers et chronologie complète."""
        device = self.get_object()
        dossiers = device.dossiers.select_related('device__device_type', 'device__model__brand')
        timeline = StatusHistory.objects.filter(dossier__device=device).select_related('user')
        return Response({
            'device': DeviceSerializer(device).data,
            'dossiers': DossierSerializer(dossiers, many=True).data,
            'timeline': StatusHistorySerializer(timeline, many=True).data,
        })
