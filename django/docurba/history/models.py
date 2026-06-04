from pghistory import create_event_model
from pghistory import models as phistory_models

from docurba.core import models as core_models


class Change(phistory_models.Events):
    class Meta:
        verbose_name = "Changement"
        verbose_name_plural = "Changements"
        proxy = True


EventSnapshot = create_event_model(
    core_models.Event,
    model_name="EventSnapshot",
    abstract=False,
    app_label="history",
    fields=[
        "procedure",
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
