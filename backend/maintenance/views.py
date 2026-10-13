from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import services
from .models import DossierSAV
from .serializers import DossierSerializer, ReceptionSerializer, TransitionSerializer


class DossierViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = DossierSerializer

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
        s = ReceptionSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        dossier = services.receive_device(user=request.user, **s.validated_data)
        return Response(DossierSerializer(dossier).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def transition(self, request, pk=None):
        s = TransitionSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        dossier = services.change_status(self.get_object(), s.validated_data['to_status'],
                                         request.user, s.validated_data['comment'])
        return Response(DossierSerializer(dossier).data)
