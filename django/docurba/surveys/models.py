from django.contrib.postgres.fields import ArrayField
from django.db import models


class ProcedureSurvey(models.Model):
    procedure = models.ForeignKey(
        "core.Procedure",
        on_delete=models.CASCADE,
        related_name="surveys_answers",
        verbose_name="procédure",
    )
    survey = models.ForeignKey(
        "surveys.Survey",
        on_delete=models.RESTRICT,
        related_name="procedures_through",
        verbose_name="enquête",
    )
    # null value is allowed because this is the way it was handled on Nuxt side.
    # When the API will be in Django, we should remove the null=True.
    # blank=true is required so that objects can be updated in the Django admin
    # without a respondant.
    respondant = models.ForeignKey(
        "users.Profile",
        on_delete=models.RESTRICT,
        related_name="surveys_answers",
        null=True,
        blank=True,
        verbose_name="répondant",
    )
    created_at = models.DateTimeField("créé le", auto_now_add=True)
    responded_at = models.DateTimeField("répondu le", null=True)

    # Despite its name, it's a SIREN or an INSEE.
    collectivite_code = models.ForeignKey(
        "core.Collectivite",
        models.DO_NOTHING,
        verbose_name="collectivité",
        to_field="code_insee_unique",
    )
    # A collectivité can belong to multiple departements.
    # Quick fix waiting for the global administrative refactor.
    departements = ArrayField(
        verbose_name="Départements de la collectivité porteuse",
        # Charfield pour permettre aux départements ne contenant qu'un chiffre de commencer par un zéro.
        base_field=models.CharField(max_length=20, blank=True),
        blank=True,
        null=True,
    )
    is_validated = models.BooleanField("est validée", null=True, db_default=False)

    class Meta:
        verbose_name = "validation"
        unique_together = ("procedure", "survey")

    def __str__(self) -> str:
        return f"{self.procedure.name}"


class Survey(models.Model):
    name = models.CharField(verbose_name="nom unique", unique=True)
    procedures = models.ManyToManyField(
        "core.Procedure",
        through="surveys.ProcedureSurvey",
        related_name="surveys",
        verbose_name="procédures",
    )
    created_at = models.DateTimeField("créée le", auto_now_add=True)

    class Meta:
        verbose_name = "enquête"

    def __str__(self) -> str:
        return self.name
