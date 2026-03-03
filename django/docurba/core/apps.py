from typing import Any

from django.apps import AppConfig
from django.conf import settings
from django.db import connection, models


class CoreAppConfig(AppConfig):
    name = "docurba.core"
    verbose_name = "Cœur"

    def ready(self) -> None:
        super().ready()
        models.signals.pre_migrate.connect(create_unmanaged_tables, sender=self)


def create_unmanaged_tables(*args: list[str, Any], **kwargs: dict[str, Any]) -> None:  # noqa: ARG001
    if not settings.CREATE_UNMANAGED_TABLES:
        return

    from docurba.core.models import (  # noqa: PLC0415
        CommuneProcedure,
        Event,
        Procedure,
    )

    unmanaged_core_models = [Procedure, CommuneProcedure, Event]

    for model in unmanaged_core_models:
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(model)
