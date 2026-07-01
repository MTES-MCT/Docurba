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
        models.signals.post_migrate.connect(create_topics, sender=self)
        if settings.ENVIRONMENT != "test":
            models.signals.post_migrate.connect(create_event_types, sender=self)


def create_topics(*args: list[str, Any], **kwargs: dict[str, Any]) -> None:  # noqa: ARG001
    from docurba.core.models import Topic  # noqa: PLC0415

    if Topic._meta.db_table in connection.introspection.table_names():  # noqa: SLF001
        json_path = pathlib.Path(settings.APPS_DIR) / "core/data/create_topics.json"
        with json_path.open("rb") as fp:
            admin_crits_spec = json.load(fp)
        with transaction.atomic():
            for spec in admin_crits_spec:
                Topic.objects.update_or_create(
                    pk=spec["pk"],
                    defaults=spec["fields"],
                )


def create_event_types(*args: list[str, Any], **kwargs: dict[str, Any]) -> None:  # noqa: ARG001
    from docurba.core.models import EventType  # noqa: PLC0415

    if EventType._meta.db_table in connection.introspection.table_names():  # noqa: SLF001
        json_path = (
            pathlib.Path(settings.APPS_DIR) / "core/data/create_event_types.json"
        )
        with json_path.open("rb") as fp:
            admin_crits_spec = json.load(fp)
        with transaction.atomic():
            for spec in admin_crits_spec:
                EventType.objects.update_or_create(
                    pk=spec["pk"],
                    defaults=spec["fields"],
                )
