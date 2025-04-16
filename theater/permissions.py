# External imports
from rest_framework.permissions import IsAuthenticated

# App imports
from user.models import UserTypes


class AdminPermission(IsAuthenticated):
    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        if request.method not in ["POST", "PUT", "DELETE"]:
            return True

        if user.user_type in [UserTypes.MANAGER, UserTypes.OWNER]:
            return True
        return False
