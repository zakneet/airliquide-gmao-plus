from django.db.models import Q
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from accounts.permissions import IsResponsableOrReadOnly

from . import services
from . import serializers as ser
from .models import DossierSAV, Fault, Part, ReturnDeclaration, StockMovement


def _detail(dossier):
    dossier = DossierSAV.objects.select_related('device__device_type', 'device__model__brand').get(
        pk=dossier.pk)
    return Response(ser.DossierDetailSerializer(dossier).data)


class FaultViewSet(viewsets.ModelViewSet):
    serializer_class = ser.FaultSerializer
    permission_classes = [IsResponsableOrReadOnly]

    def get_queryset(self):
        qs = Fault.objects.order_by('device_type__name', 'name')
        t = self.request.query_params.get('device_type')
        return qs.filter(device_type_id=t) if t else qs


class PartViewSet(viewsets.ModelViewSet):
    queryset = Part.objects.order_by('reference')
    serializer_class = ser.PartSerializer
    permission_classes = [IsResponsableOrReadOnly]


class ReturnDeclarationViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                               mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Questionnaire de retour, rempli avant l'arrivée de l'appareil."""

    serializer_class = ser.ReturnDeclarationSerializer

    def get_queryset(self):
        qs = ReturnDeclaration.objects.select_related('declared_by', 'dossier')
        p = self.request.query_params
        if p.get('pending') == '1':
            qs = qs.filter(dossier__isnull=True)
        q = p.get('search', '').strip()
        if q:
            qs = qs.filter(Q(return_id__icontains=q) | Q(serial_number__icontains=q))
        return qs

    def perform_create(self, serializer):
        serializer.save(declared_by=self.request.user)


class StockMovementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StockMovement.objects.select_related('device', 'dossier').order_by('-at')
    serializer_class = ser.StockMovementSerializer


class DossierViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    def get_serializer_class(self):
        return ser.DossierDetailSerializer if self.action == 'retrieve' else ser.DossierSerializer

    def get_queryset(self):
        qs = DossierSAV.objects.select_related('device__device_type', 'device__model__brand')
        p = self.request.query_params
        if p.get('status'):
            qs = qs.filter(status=p['status'])
        if p.get('device'):
            qs = qs.filter(device_id=p['device'])
        return qs

    @action(detail=False, methods=['post'])
    def reception(self, request):
        s = ser.ReceptionSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        dossier = services.receive_device(user=request.user, **s.validated_data)
        return Response(ser.DossierSerializer(dossier).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def transition(self, request, pk=None):
        s = ser.TransitionSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = services.change_status(self.get_object(), s.validated_data['to_status'],
                                   request.user, s.validated_data['comment'])
        return _detail(d)

    def _step(self, request, input_cls, fn):
        s = input_cls(data=request.data)
        s.is_valid(raise_exception=True)
        return _detail(fn(self.get_object(), request.user, **s.validated_data))

    @action(detail=True, methods=['post'])
    def disinfection(self, request, pk=None):
        return self._step(request, ser.DisinfectionInput, services.record_disinfection)

    @action(detail=True, methods=['post'])
    def diagnosis(self, request, pk=None):
        return self._step(request, ser.DiagnosisInput, services.record_diagnosis)

    @action(detail=True, methods=['post'])
    def repair(self, request, pk=None):
        return self._step(request, ser.RepairInput, services.record_repair)

    @action(detail=True, methods=['post'], url_path='quality-control')
    def quality_control(self, request, pk=None):
        return self._step(request, ser.QualityControlInput, services.record_quality_control)

    @action(detail=True, methods=['post'], url_path='stock-entry')
    def stock_entry(self, request, pk=None):
        return self._step(request, ser.StockInput, services.enter_stock)

    @action(detail=True, methods=['post'])
    def delivery(self, request, pk=None):
        return self._step(request, ser.DeliveryInput, services.deliver)

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser, JSONParser])
    def photos(self, request, pk=None):
        dossier = self.get_object()
        s = ser.PhotoSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        s.save(dossier=dossier, uploaded_by=request.user)
        return Response(s.data, status=status.HTTP_201_CREATED)
