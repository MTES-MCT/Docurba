from django.db import models


class CommuneType(models.TextChoices):
    COM = "COM", "Commune"
    COMD = "COMD", "Commune déléguée"
    UNKWN = "UNKWN", "Inconnu"


class ProcedureType(models.TextChoices):
    # NOTE(cms): these enums are not really pythonic as they should be in upper case
    # and without space but it's the way they are stored in the database today.
    ABROGATION = "Abrogation", "Abrogation"
    ELABORATION = "Elaboration", "Elaboration"
    MISE_A_JOUR = "Mise à jour", "Mise à jour"
    MISE_EN_COMPATIBILITE = "Mise en compatibilité", "Mise en compatibilité"
    MODIFICATION = "Modification", "Modification"
    MODIFICATION_SIMPLIFIEE = "Modification simplifiée", "Modification simplifiée"
    REVISION = "Révision", "Révision"
    REVISION_MS_RA = (
        "Révision à modalité simplifiée ou Révision allégée",
        "Révision à modalité simplifiée ou Révision allégée",
    )
    REVISION_ALLEGEE = "Révision allégée (ou RMS)", "Révision allégée (ou RMS)"
    REVISION_SIMPLIFIEE = "Révision simplifiée", "Révision simplifiée"

    @classmethod
    def principal(cls: models.TextChoices) -> dict:
        enums = [cls.ABROGATION, cls.ELABORATION]
        return {member.value: member for member in cls if member in enums}

    @classmethod
    def secondary(cls: models.TextChoices) -> dict:
        enums = [
            cls.MISE_A_JOUR,
            cls.MISE_EN_COMPATIBILITE,
            cls.MODIFICATION,
            cls.MODIFICATION_SIMPLIFIEE,
            cls.REVISION,
            cls.REVISION_MS_RA,
            cls.REVISION_ALLEGEE,
            cls.REVISION_SIMPLIFIEE,
        ]
        return {member.value: member for member in cls if member in enums}


class TypeCollectivite(models.TextChoices):
    COM = "COM", "Commune"
    COMD = "COMD", "Commune déléguée"
    COMA = "COMA", "Commune associée"
    CC = "CC", "Communauté de communes"
    SMF = "SMF", "Syndicat Mixte Fermé"
    SMO = "SMO", "Syndicat Mixte Ouvert"
    METRO = "METRO", "Métropole"
    CU = "CU", "Communauté Urbaine"
    PETR = "PETR", "Pôle d'Équilibre Territorial et Rural"
    MET69 = "MET69", "Métropole de Lyon"
    SIVU = "SIVU", "Syndicat Intercommunal à Vocation Unique"
    EPT = "EPT", "Établissement Public Territorial"
    CA = "CA", "Communauté d'Agglomération"
    POLEM = "POLEM", "Pôle Métropolitain"
    SIVOM = "SIVOM", "Syndicat Intercommunal à Vocation Multiple"
