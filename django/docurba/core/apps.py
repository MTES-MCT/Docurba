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


def create_topics(*args: list[str, Any], **kwargs: dict[str, Any]) -> None:  # noqa: ARG001
    from docurba.core.models import Topic  # noqa: PLC0415

    if Topic._meta.db_table in connection.introspection.table_names():  # noqa: SLF001
        json_path = pathlib.Path(settings.APPS_DIR) / "core/data/topics.json"
        with json_path.open("rb") as fp:
            topics = json.load(fp)
        with transaction.atomic():
            for topic in topics:
                Topic.objects.update_or_create(
                    pk=topic["pk"],
                    defaults=topic["fields"],
                )
