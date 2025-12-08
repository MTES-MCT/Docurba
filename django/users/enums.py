from django.db import models


class ProfileSideType(models.TextChoices):
    ETAT = "etat", "État"
    COLLECTIVITE = "collectivite", "Collectivité"
    PPA = "ppa", "PPA"


class PosteType(models.TextChoices):
    # Postes État
    # https://github.com/MTES-MCT/Docurba/blob/2050c8dc046f9c8414ebe9aaf72a3f3cdbc623d2/nuxt/plugins/utils.js#L58
    DDT = "ddt", "DDT(M)/DEAL"
    DREAL = "dreal", "DREAL"

    # Postes PPA
    REGION = "region", "Région"

    # Postes Collectivités
    BE = "be", "Bureau d'études"
    ELU = "elu", "Collectivité, Élu·e"
    EMPLOYE_MAIRIE = "employe_mairie", "Collectivité, Technicien·ne ou employé·e"
    AGENCE_URBA = "agence_urba", "Agence d'urbanisme"
    AUTRE = "autre", "Autre"


class RoleType(models.TextChoices):
    # Nuxt :
    # Côté collectivité, c'est un InputField qui ne valide pas l'input.
    # A contrario, côté État, c'est un TextChoices avec un menu déroulant. U_U
    # https://github.com/MTES-MCT/Docurba/blob/2050c8dc046f9c8414ebe9aaf72a3f3cdbc623d2/nuxt/plugins/utils.js#L62
    # Cela étant, il semblerait que les utilisateurs n'aient pas été très inspirés car seules 33
    # valeurs différentes figurent en base (en excluant les comptes tests), dont des "PPA".
    # Rôles état
    CHEF_UNITE = "chef_unite", "Chef·fe d'unité/de bureau/de service et adjoint·e"
    REDACTEUR_PAC = "redacteur_pac", "Rédacteur·ice de PAC"
    SUIVI_PROCEDURES = (
        "suivi_procedures",
        "Chargé·e de l'accompagnement des collectivités",
    )
    REFERENT_SUDOCUH = "referent_sudocuh", "Référent·e Sudocuh"
