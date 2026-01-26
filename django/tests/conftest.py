import pytest
from django.apps import apps
from django.db import connection

from users.models import User


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker, django_db_createdb):  # noqa: ANN001, ANN201, ARG001
    """
    Permet de créer les modèles non managés, sauf les views.

    Les views seront créées par les migrations.

    Adapté de https://stackoverflow.com/a/61607753/4554587
    """
    if not django_db_createdb:
        yield
        return

    with django_db_blocker.unblock():
        unmanaged_models_except_views = [
            model
            for model in apps.get_models()
            if not model._meta.managed and not model._meta.db_table.startswith("view_")  # noqa: SLF001
        ]

        # La table `users` est dans le schéma `auth` qui n'est pas listée dans connection.instrospection.
        # Traitons-la différemment des autres modèles.
        # Voir users/test_models.py
        with connection.schema_editor() as schema_editor:
            schema_editor.execute("CREATE SCHEMA auth;")
            schema_editor.create_model(User)
        unmanaged_models_except_views = [
            model for model in unmanaged_models_except_views if model is not User
        ]

        for model in unmanaged_models_except_views:
            with connection.schema_editor() as schema_editor:
                schema_editor.create_model(model)

                if model._meta.db_table not in connection.introspection.table_names():  # noqa: SLF001
                    msg = f"Table `{model._meta.db_table}` is missing in test database."  # noqa: SLF001
                    raise ValueError(msg)

        yield
