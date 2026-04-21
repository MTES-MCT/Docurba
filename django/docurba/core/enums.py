from django.db import models


class CommuneType(models.TextChoices):
    COM = "COM", "Commune"
    COMD = "COMD", "Commune déléguée"
    UNKWN = "UNKWN", "Inconnu"
