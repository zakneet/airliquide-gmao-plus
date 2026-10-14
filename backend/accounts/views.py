from django.conf import settings
from rest_framework import viewsets
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .permissions import IsResponsableSAV
from .serializers import UserSerializer

REFRESH_COOKIE = 'refresh_token'
COOKIE_PATH = '/api/auth/'


def _set_refresh_cookie(response, token):
    response.set_cookie(
        REFRESH_COOKIE, token,
        max_age=int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()),
        httponly=True, secure=not settings.DEBUG, samesite='Lax', path=COOKIE_PATH,
    )


class LoginView(TokenObtainPairView):
    """Retourne l'access token ; le refresh token est placé dans un cookie HttpOnly."""

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            _set_refresh_cookie(response, response.data.pop('refresh'))
            response.data = {'access': response.data['access']}
        return response


class RefreshView(APIView):
    """Renouvelle l'access token à partir du cookie HttpOnly."""

    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'refresh'

    def post(self, request):
        token = request.COOKIES.get(REFRESH_COOKIE)
        if not token:
            return Response({'detail': 'Session absente.'}, status=401)
        s = TokenRefreshSerializer(data={'refresh': token})
        try:
            s.is_valid(raise_exception=True)
        except (TokenError, InvalidToken):
            r = Response({'detail': 'Session expirée.'}, status=401)
            r.delete_cookie(REFRESH_COOKIE, path=COOKIE_PATH)
            return r
        return Response({'access': s.validated_data['access']})


class LogoutView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        r = Response(status=204)
        r.delete_cookie(REFRESH_COOKIE, path=COOKIE_PATH)
        return r


class MeView(RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class UserViewSet(viewsets.ModelViewSet):
    """Administration des utilisateurs (Responsable SAV uniquement)."""

    queryset = User.objects.order_by('last_name', 'email')
    serializer_class = UserSerializer
    permission_classes = [IsResponsableSAV]
