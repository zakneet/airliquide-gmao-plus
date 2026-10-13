from rest_framework.permissions import BasePermission

from .models import User


class IsResponsableSAV(BasePermission):
    """Réservé au Responsable SAV (administration, rapports)."""

    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and u.role == User.Role.RESPONSABLE_SAV)
