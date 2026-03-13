import json
import pathlib
from typing import Any

from django.apps import AppConfig
from django.conf import settings
from django.db import connection, models, transaction


class CoreAppConfig(AppConfig):
    name = "docurba.core"
    verbose_name = "Cœur"

    def ready(self) -> None:
        super().ready()
        models.signals.pre_migrate.connect(create_unmanaged_tables, sender=self)
        models.signals.post_migrate.connect(create_topics, sender=self)


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


def create_topics(*args: list[str, Any], **kwargs: dict[str, Any]) -> None:  # noqa: ARG001
    from docurba.core.models import Topic  # noqa: PLC0415

    if Topic._meta.db_table not in connection.introspection.table_names():  # noqa: SLF001
        return

    json_path = pathlib.Path(settings.APPS_DIR) / "core/data/create_topics.json"
    with json_path.open("rb") as fp:
        admin_crits_spec = json.load(fp)
    with transaction.atomic():
        for spec in admin_crits_spec:
            Topic.objects.update_or_create(
                pk=spec["pk"],
                defaults=spec["fields"],
            )
