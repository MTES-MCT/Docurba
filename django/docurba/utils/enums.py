from django.db import models


class DocurbaEnvironment(models.TextChoices):
    PROD = "PROD", "production"
    DEMO = "DEMO", "démo"
    REVIEW_APP = "REVIEW-APP", "recette jetable"
    TEST = "TEST", "test"
    DEV = "DEV", "dev"
