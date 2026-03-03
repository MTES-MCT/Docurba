from typing import Any

from django.apps import AppConfig
from django.conf import settings
from django.db import connection, models


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "docurba.users"
    verbose_name = "Utilisateurs"

    def ready(self) -> None:
        super().ready()
        models.signals.pre_migrate.connect(create_unmanaged_tables, sender=self)


def create_unmanaged_tables(*args: list[str, Any], **kwargs: dict[str, Any]) -> None:  # noqa: ARG001
    if not settings.CREATE_UNMANAGED_TABLES:
        return

    from docurba.users.models import Profile, User  # noqa: PLC0415

    unmanaged_user_models = [User, Profile]

    with connection.schema_editor() as schema_editor:
        schema_editor.execute("CREATE SCHEMA auth;")

    for model in unmanaged_user_models:
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(model)
