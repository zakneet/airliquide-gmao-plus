from rest_framework import viewsets
from rest_framework.generics import RetrieveAPIView

from .models import User
from .permissions import IsResponsableSAV
from .serializers import UserSerializer


class MeView(RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class UserViewSet(viewsets.ModelViewSet):
    """Administration des utilisateurs (Responsable SAV uniquement)."""

    queryset = User.objects.order_by('last_name', 'email')
    serializer_class = UserSerializer
    permission_classes = [IsResponsableSAV]
