from rest_framework.permissions import BasePermission

from ..models import CustomUser


class IsAdminRole(BasePermission):
    message = "Admin access is required."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == CustomUser.Role.ADMIN
            and request.user.is_staff
        )