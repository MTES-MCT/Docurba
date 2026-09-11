import logging
from urllib.request import Request

import supabase_auth.errors as supabase_errors
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import models
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from sendgrid_backend.mail import HTTPError

from docurba.core.models import Collectivite, Commune, EventType
from docurba.users.models import Profile
from docurba.utils.api.views import PublicAPIView
from docurba.www.internal_api import filters as custom_filters
from docurba.www.internal_api.serializers import (
    CollectiviteSerializer,
    CommuneSerializer,
    EventTypeSerializer,
)

logger = logging.getLogger(__name__)


class CollectiviteViewSet(PublicAPIView, viewsets.ReadOnlyModelViewSet):
    """Collectivités en base."""

    serializer_class = CollectiviteSerializer
    filterset_class = custom_filters.CollectiviteFilter
    lookup_field = "code_insee_unique"

    def get_serializer_context(self) -> dict:
        context = super().get_serializer_context()
        if "avec_membres_niveaux_inferieurs" in self.request.query_params:
            context["with_flat_members"] = True

        if "avec_groupements_niveaux_superieurs" in self.request.query_params:
            context["with_flat_groups"] = True

        if "avec_groupements" in self.request.query_params:
            context["with_groups"] = True

        if "avec_membres" in self.request.query_params:
            context["with_members"] = True

        return context

    def get_queryset(self):  # noqa: ANN201
        qs = Collectivite.objects.select_related(
            "departement", "departement__region", "commune__intercommunalite"
        ).order_by("siren", "code_insee")
        if "with_flat_members" in self.get_serializer_context():
            qs = qs.prefetch_related(
                models.Prefetch(
                    "flat_members",
                    queryset=qs,
                )
            )
        if "with_flat_groups" in self.get_serializer_context():
            qs = qs.prefetch_related(
                models.Prefetch(
                    "flat_groups",
                    queryset=qs,
                )
            )
        if "with_groups" in self.get_serializer_context():
            qs = qs.prefetch_related(
                models.Prefetch(
                    "adhesions",
                    queryset=qs,
                )
            )
        if "with_members" in self.get_serializer_context():
            qs = qs.prefetch_related(
                models.Prefetch(
                    "collectivites_adherentes",
                    queryset=qs,
                )
            )
        return qs.all()


class CommuneViewSet(PublicAPIView, viewsets.ReadOnlyModelViewSet):
    """Communes en base."""

    queryset = (
        Commune.objects.select_related(
            "departement",
            "departement__region",
            "intercommunalite",
        )
        .order_by("code_insee")
        .all()
    )
    serializer_class = CommuneSerializer
    filterset_class = custom_filters.CommuneFilter


# NOTE(cms): this should not be public. Make it private.
class EventTypeViewSet(PublicAPIView, viewsets.ReadOnlyModelViewSet):
    queryset = EventType.active_objects.all()
    serializer_class = EventTypeSerializer
    filterset_class = custom_filters.EventTypeFilter


class UserMustUpdatePasswordView(PublicAPIView, generics.GenericAPIView):
    def get(self, request: Request, *args, **kwargs) -> Response:  # noqa: ANN002, ANN003, ARG002
        must_update_password = (
            "email" in request.GET
            and Profile.objects.filter(
                email=request.GET.get("email"), must_update_password=True
            ).exists()
        )
        return Response({"must_update_password": must_update_password})


class UserPassword(generics.GenericAPIView):
    def post(self, request: Request, *args, **kwargs) -> Response:  # noqa: ANN002, ANN003, ARG002
        if "password" not in request.data:
            return Response(
                {"errors": ["Il n'y a pas de mot de passe."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        password = request.data.get("password")
        try:
            validate_password(password=password)
        except ValidationError as errors:
            return Response(
                {"errors": list(errors)}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            request.user.supabase_client.auth.update_user({"password": password})
        except (
            supabase_errors.AuthApiError,
            supabase_errors.AuthError,
            supabase_errors.AuthSessionMissingError,
            supabase_errors.AuthUnknownError,
            supabase_errors.AuthWeakPasswordError,
        ):
            logger.exception("Supabase error")
            return Response(
                {"errors": ["Merci d'essayer un autre mot de passe."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        profile = request.user.profile
        if profile and profile.must_update_password:
            profile.must_update_password = False
            profile.save()

        if profile:
            try:
                profile.update_password_email().send()
            except HTTPError:
                logger.exception("Sendgrid error")

        return Response(
            {"message": "Mot de passe mis à jour."}, status=status.HTTP_201_CREATED
        )
