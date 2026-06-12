from django.contrib import admin
from pghistory.admin import EventModelAdmin

from docurba.history.models import EventSnapshot


@admin.register(EventSnapshot)
class EventSnapshotAdmin(EventModelAdmin):
    list_display = (
        "pgh_obj",
        "pgh_label",
        "pgh_created_at",
        "date_evenement",
    )
    fieldsets = [  # noqa: RUF012
        (
            "Évènement",
            {
                "fields": (
                    "code",
                    "description",
                    "date_evenement",
                    "from_sudocuh",
                    "type",
                    "procedure",
                    "profile",
                ),
                "description": "Champs copiés à partir de l'évèvenement",
            },
        ),
        (
            "Historique",
            {
                "fields": (
                    "pgh_obj",
                    "pgh_created_at",
                    "pgh_context",
                ),
                "description": "Champs de l'instantané",
            },
        ),
    ]
