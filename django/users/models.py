from django.contrib.postgres.fields import ArrayField
from django.db import models

from core.models import Collectivite
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

    # Il n'y a pas de clé primaire déclarée dans la base de données mais Django en nécessite une.
    # Déclarons qu'il s'agit de la colonne user_id en solution de contournement.
    # Nous pourrons ajouter une colonne id plus tard.
    user = models.OneToOneField(
        User, verbose_name="Utilisateur", on_delete=models.CASCADE, primary_key=True
    )
    created_at = models.DateTimeField(
        verbose_name="Date de création", auto_now_add=True
    )
    firstname = models.CharField(verbose_name="Prénom", blank="True")
    lastname = models.CharField(verbose_name="Nom", blank="True")
    email = models.EmailField(verbose_name="Email", blank=True)
    poste = models.CharField(
        verbose_name="Poste", choices=users_enums.PosteType, blank=True
    )
    other_poste = ArrayField(
        verbose_name="Role(s)",
        base_field=models.CharField(choices=users_enums.RoleType, blank=True),
        size=10,
        blank=True,
    )
    # Ce devrait être une clé étrangère pointant vers la table departements
    # mais ce n'est actuellement pas le cas en base et dans Nuxt.
    departement = models.CharField(verbose_name="Département", blank=True)
    # PPA sides have rights depending on their departments. This is an ugly and quick fix
    # to link users to several departments (and not only one).
    # It should be refactored!
    departements = ArrayField(
        verbose_name="Départements",
        # CharField to allow departments starting with a zero. Otherwise, zero is erased.
        base_field=models.CharField(max_length=3, blank=True),
        size=50,
        blank=True,
        null=True,
    )
    collectivite = models.ForeignKey(
        Collectivite,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    tel = models.CharField(verbose_name="Téléphone", blank=True)
    verified = models.BooleanField(verbose_name="Vérifié", default=False)
    # La valeur `blank` ne devrait pas être autorisée car un utilisateur devrait toujours
    # avoir un `side` mais c'est le cas aujourd'hui en base.
    side = models.CharField(
        verbose_name="Side", choices=users_enums.ProfileSideType, blank=True
    )
    # Ce devrait être une clé étrangère pointant vers la table regions
    # mais ce n'est actuellement pas le cas en base et dans Nuxt.
    region = models.CharField(
        verbose_name="Région",
        blank=True,
        db_comment="Si l'utilisateur est une DREAL, son scope est une région. Cette peut être vide si c'est un autre poste que DREAL.",
    )
    # La faute d'orthographe est en base.
    no_signup = models.BooleanField(
        verbose_name="Dépôt d'actes (no_signup)",
        default=False,
        db_comment="Si l'utilisateur passe par un depot d'acte, il est authrosié de mettre uniquement son email. Dans ce cas l'utilisateur n'a pas de compte Docurba, et no_signup sera à TRUE. ",
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
