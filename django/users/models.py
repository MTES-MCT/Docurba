from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.functions import Now

from users import enums as users_enums


class User(models.Model):
    """L'authentification est gérée par la fonctionnalité SSO de Supabase.

    Le schéma de cette table est géré par Supabase. Seules les colonnes intéressantes sont
    référencées ici.
    Un jour, nous pourrons utiliser le User model de Django. Pour l'instant, documentons l'existant.
    """

    id = models.UUIDField(primary_key=True)
    email = models.EmailField(verbose_name="Email", blank=True)

    class Meta:
        managed = False
        db_table = '"auth"."users"'
        verbose_name = "utilisateur"

    def __str__(self) -> str:
        return self.email


class Profile(models.Model):
    """La table `users` étant gérée par Supabase, les informations supplémentaires concernant l'utilisateur sont conservées ici."""

    user = models.OneToOneField(
        User, verbose_name="Utilisateur", on_delete=models.CASCADE, primary_key=True
    )
    created_at = models.DateTimeField(verbose_name="Date de création", db_default=Now())
    # La plupart des CharField peuvent avoir une valeur nulle ou "" en base car
    # il n'y a pas de restriction. Il faudrait changer ce comportement.
    # Pour l'instant, documentons.
    firstname = models.CharField(verbose_name="Prénom", blank=True, null=True)  # noqa: DJ001
    lastname = models.CharField(verbose_name="Nom", blank=True, null=True)  # noqa: DJ001
    email = models.EmailField(verbose_name="Email", blank=True, null=True)  # noqa: DJ001
    poste = models.CharField(  # noqa: DJ001
        verbose_name="Poste",
        choices=users_enums.PosteType,
        blank=True,
        null=True,
    )
    other_poste = ArrayField(
        verbose_name="Role(s)",
        base_field=models.CharField(choices=users_enums.RoleType, blank=True),
        blank=True,
        null=True,
    )
    # Ce devrait être une clé étrangère pointant vers la table departements
    # mais ce n'est actuellement pas le cas en base et dans Nuxt.
    departement = models.CharField(verbose_name="Département", blank=True, null=True)  # noqa: DJ001
    # Les utilisateurs side PPA peuvent voir les départements listés dans cette colonne.
    # Il s'agit d'une rustine temportaire pour relier les utilisateurs à plusieurs départements
    # (et non un seul comme c'est le cas actuellement avec la colonne `departement`).
    departements = ArrayField(
        verbose_name="Départements",
        # Charfield pour permettre aux départements ne contenant qu'un chiffre de commencer par un zéro.
        base_field=models.CharField(max_length=3, blank=True),
        blank=True,
        null=True,
    )
    # Ce devrait être une clé étrangère pointant vers Collectivite mais la colonne collectivite_id
    # ne conserve pas la clé primaire déclarée pour le modèle (i.e. au format f"{code_insee}_{type}")
    # mais seulement le "code_insee".
    collectivite_id = models.CharField(  # noqa: DJ001
        verbose_name="Code Collectivité", blank=True, null=True
    )
    tel = models.CharField(verbose_name="Téléphone", blank=True, null=True)  # noqa: DJ001
    verified = models.BooleanField(verbose_name="Vérifié", default=False)
    # La valeur `blank` ne devrait pas être autorisée car un utilisateur devrait toujours
    # avoir un `side` mais c'est le cas aujourd'hui en base.
    side = models.CharField(  # noqa: DJ001
        verbose_name="Side", choices=users_enums.ProfileSideType, blank=True, null=True
    )
    # Ce devrait être une clé étrangère pointant vers la table regions
    # mais ce n'est actuellement pas le cas en base et dans Nuxt.
    region = models.CharField(  # noqa: DJ001
        verbose_name="Région",
        blank=True,
        null=True,
        db_comment="Si l'utilisateur est une DREAL ou une PPA : région de son périmètre. La colonne peut être remplie pour les autres types.",
    )
    no_signup = models.BooleanField(
        verbose_name="Dépôt d'actes (no_signup)",
        default=False,
        db_comment="Si l'utilisateur passe par un depot d'acte, il est autorisé à mettre uniquement son email. Dans ce cas l'utilisateur n'a pas de compte Docurba, et no_signup sera à TRUE.",
    )
    successfully_logged_once = models.BooleanField(
        verbose_name="S'est déjà connecté", default=False
    )
    optin = models.BooleanField(
        verbose_name="Est inscrit à l'infolettre", default=False
    )
    updated_pipedrive = models.BooleanField(
        verbose_name="Est mis à jour sur Pipedrive",
        default=False,
    )
    is_admin = models.BooleanField(
        verbose_name="Est admin (is_admin)",
        default=False,
        db_comment="super admin bypass",
    )
    is_staff = models.BooleanField(verbose_name="Est membre (is_staff)", default=False)

    class Meta:
        managed = False
        db_table = "profiles"
        verbose_name = "profil"

    def __str__(self) -> str:
        return f"{self.firstname} {self.lastname}"
