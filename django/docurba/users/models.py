import secrets
import string

from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.postgres.fields import ArrayField
from django.db import connection, models, transaction
from django.db.models.functions import Now

from docurba.users import enums as users_enums


class SupabaseUser(models.Model):
    """L'authentification est gérée par la fonctionnalité SSO de Supabase.

    Le schéma de cette table est géré par Supabase. Seules les colonnes intéressantes sont
    référencées ici.
    Un jour, nous pourrons utiliser le User model de Django. Pour l'instant, documentons l'existant.
    """

    id = models.UUIDField(primary_key=True)
    email = models.EmailField(verbose_name="Email", blank=True)
    last_sign_in_at = models.DateTimeField(
        verbose_name="Date de dernière connexion", db_default=Now(), editable=False
    )
    encrypted_password = models.CharField()

    class Meta:
        managed = False
        db_table = '"auth"."users"'
        verbose_name = "utilisateur supabase"
        verbose_name_plural = "utilisateurs supabase"

    def __str__(self) -> str:
        return self.email

    @classmethod
    def _random_password(cls) -> str:
        # https://docs.python.org/3/library/secrets.html#recipes-and-best-practices
        alphabet = string.ascii_letters + string.digits
        length = 20
        min_digits = 3
        while True:
            password = "".join(secrets.choice(alphabet) for _ in range(length))
            if (
                any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and sum(c.isdigit() for c in password) >= min_digits
            ):
                break
        return password

    def update_password(self, password: str | None = None) -> str:
        """Update user password handled by Supabase.

        Passwords are crypted by Supabase at the database level.
        Their client does not allow to update users' password without
        them logging in first.
        https://supabase.com/docs/reference/python/auth-resetpasswordforemail
        """
        if not password:
            password = self._random_password()

        with transaction.atomic(), connection.cursor() as cursor:
            # https://github.com/orgs/supabase/discussions/5043
            cursor.execute(
                """
                UPDATE auth.users
                SET encrypted_password = crypt(%s, gen_salt('bf'))
                WHERE id = %s;
            """,
                [password, self.id],
            )
        return password


class Session(models.Model):
    """L'authentification est gérée par la fonctionnalité SSO de Supabase.

    Le schéma de cette table est géré par Supabase. Seules les colonnes intéressantes sont
    référencées ici.
    """

    id = models.UUIDField(primary_key=True)
    user = models.ForeignKey(
        SupabaseUser,
        models.CASCADE,
    )

    class Meta:
        managed = False
        db_table = '"auth"."sessions"'

    def __str__(self) -> str:
        return self.id


class Profile(models.Model):
    """La table `users` étant gérée par Supabase, les informations supplémentaires concernant l'utilisateur sont conservées ici."""

    user = models.OneToOneField(
        SupabaseUser,
        verbose_name="Utilisateur",
        on_delete=models.CASCADE,
        primary_key=True,
    )
    created_at = models.DateTimeField(
        verbose_name="Date de création", db_default=Now(), editable=False
    )
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
        help_text="<br>".join(users_enums.RoleType.values),
    )
    departement = models.ForeignKey(
        "core.Departement",
        models.DO_NOTHING,
        db_column="departement",
        db_constraint=False,
        null=True,
        blank=True,
        to_field="code_insee",
    )
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
    collectivite = models.ForeignKey(
        "core.Collectivite",
        models.DO_NOTHING,
        db_constraint=False,
        null=True,
        blank=True,
        to_field="code_insee_unique",
    )
    tel = models.CharField(verbose_name="Téléphone", blank=True, null=True)  # noqa: DJ001
    verified = models.BooleanField(verbose_name="Vérifié", default=False)
    # La valeur `blank` ne devrait pas être autorisée car un utilisateur devrait toujours
    # avoir un `side` mais c'est le cas aujourd'hui en base.
    side = models.CharField(  # noqa: DJ001
        verbose_name="Side", choices=users_enums.ProfileSideType, null=True
    )
    region = models.ForeignKey(
        "core.region",
        models.DO_NOTHING,
        db_column="region",
        db_constraint=False,
        null=True,
        blank=True,
        to_field="code_insee",
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
        verbose_name="Super Admin",
        default=False,
        help_text="Donne tous les droits",
        db_comment="super admin bypass",
    )
    is_staff = models.BooleanField(
        verbose_name="Staff", default=False, help_text="Cache le compte"
    )

    class Meta:
        # Table created by a pre_migrate signal in apps.py.
        managed = False
        db_table = "profiles"
        verbose_name = "profil"

    def __str__(self) -> str:
        return f"{self.firstname} {self.lastname}"


class DjangoUserManager(UserManager):
    pass


class User(AbstractUser):
    objects = DjangoUserManager()

    class Meta:
        db_table = "auth_user"
        verbose_name = "utilisateur django"
        verbose_name_plural = "utilisateurs django"
