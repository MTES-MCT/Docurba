from django.http import HttpRequest
from rest_framework.permissions import IsAuthenticated


class IsVerified(IsAuthenticated):
    """Allows access only to verified users."""

    def has_permission(self, request: HttpRequest, view) -> bool:  # noqa: ANN001
        has_permission = super().has_permission(request, view)
        return bool(has_permission and request.user.profile.verified)
