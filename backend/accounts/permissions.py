from rest_framework.permissions import BasePermission

from .models import User


class IsResponsableSAV(BasePermission):
    """Réservé au Responsable SAV (administration, rapports)."""

    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and u.role == User.Role.RESPONSABLE_SAV)


class IsResponsableOrReadOnly(BasePermission):
    """Lecture pour tout utilisateur connecte, ecriture pour le Responsable SAV."""

    def has_permission(self, request, view):
        u = request.user
        if not (u and u.is_authenticated):
            return False
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return u.role == User.Role.RESPONSABLE_SAV
