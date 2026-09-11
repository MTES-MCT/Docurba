from django.conf import settings
from django.db import models


class ManagerWithFetchMode(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().fetch_mode(settings.DEFAULT_FETCH_MODE)
