from pghistory import ObjForeignKey, create_event_model
from pghistory import models as pghistory_models

from docurba.core import models as core_models


class Change(pghistory_models.Events):
    class Meta:
        verbose_name = "Changement"
        verbose_name_plural = "Changements"
        proxy = True


EventSnapshot = create_event_model(
    core_models.Event,
    model_name="EventSnapshot",
    abstract=False,
    app_label="history",
    obj_field=ObjForeignKey(
        related_name="snapshots",
        related_query_name="snapshots_qs",
    ),
    fields=[
        "procedure",
        "event_type",
        "type",
        "code",
        "date_evenement",
        "description",
        "profile",
        "from_sudocuh",
    ],
    meta={
        "verbose_name": "Instantané de l'évènement",
        "verbose_name_plural": "Instantanés de l'évènement",
    },
)
