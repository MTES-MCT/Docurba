from django.core.management.base import BaseCommand

from docurba.core.models import Event, Procedure, Project, ProjectSharing
from docurba.users.models import Profile


class Command(BaseCommand):
    help = "Transfer object ownership from one profile to another profile"

    def add_arguments(self, parser: str) -> None:
        parser.add_argument(
            "source_email",
            help="Email of the current owner",
        )
        parser.add_argument(
            "destination_email",
            help="Email of the new owner",
        )
        parser.add_argument(
            "--wet-run",
            dest="wet_run",
            action="store_true",
            help="Persists changes in database",
        )

    def handle(  # noqa: C901, PLR0912
        self,
        *args: list,  # noqa: ARG002
        source_email: str,
        destination_email: str,
        wet_run: bool,
        **options: dict,  # noqa: ARG002
    ) -> None:
        source = Profile.objects.get(email=source_email)
        destination = Profile.objects.get(email=destination_email)

        self.stdout.write(f"Previous owner : {source.email} ({source.user_id})")
        self.stdout.write(f"New owner : {destination.email} ({destination.user_id})")

        source_id = source.user_id
        destination_id = destination.user_id

        # Project.owner_id
        self.stdout.write("Liste des Project modifiés sur le champ owner_id :")
        queryset = Project.objects.filter(owner_id=source_id)
        for pk in queryset.values_list("pk", flat=True):
            self.stdout.write(f"{pk}")
        if wet_run:
            queryset.update(owner_id=destination_id)

        # ProjectSharing.shared_by
        self.stdout.write("Liste des ProjectSharing modifiés sur le champ shared_by :")
        queryset = ProjectSharing.objects.filter(shared_by=source_id)
        for pk in queryset.values_list("pk", flat=True):
            self.stdout.write(f"{pk}")
        if wet_run:
            queryset.update(shared_by=destination_id)

        # ProjectSharing.user_email
        self.stdout.write("Liste des ProjectSharing modifiés sur le champ user_email :")
        queryset = ProjectSharing.objects.filter(user_email=source_email)
        for pk in queryset.values_list("pk", flat=True):
            self.stdout.write(f"{pk}")
        if wet_run:
            queryset.update(user_email=destination_email)

        # Procedure.owner_id
        self.stdout.write("Liste des Procedure modifiés sur le champ owner_id :")
        queryset = Procedure.objects.filter(owner_id=source_id)
        for pk in queryset.values_list("pk", flat=True):
            self.stdout.write(f"{pk}")
        if wet_run:
            queryset.update(owner_id=destination_id)

        # Procedure.last_updated_by
        self.stdout.write("Liste des Procedure modifiés sur le champ last_updated_by :")
        queryset = Procedure.objects.filter(last_updated_by=source_id)
        for pk in queryset.values_list("pk", flat=True):
            self.stdout.write(f"{pk}")
        if wet_run:
            queryset.update(last_updated_by=destination_id)

        # Event.profile_id
        self.stdout.write("Liste des Event modifiés sur le champ profile_id :")
        queryset = Event.objects.filter(profile_id=source_id)
        for pk in queryset.values_list("pk", flat=True):
            self.stdout.write(f"{pk}")
        if wet_run:
            queryset.update(profile_id=destination_id)

        # Event.archived_by
        self.stdout.write("Liste des Event modifiés sur le champ archived_by :")
        queryset = Event.objects.filter(archived_by=source_id)
        for pk in queryset.values_list("pk", flat=True):
            self.stdout.write(f"{pk}")
        if wet_run:
            queryset.update(archived_by=destination_id)
