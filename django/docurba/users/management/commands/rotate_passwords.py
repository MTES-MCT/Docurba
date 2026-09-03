import logging

from django.core.management.base import BaseCommand, CommandParser

from docurba.users.models import SupabaseUser


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        super().add_arguments(parser)
        parser.add_argument(
            "--wet-run",
            action="store_true",
            default=False,
            help="Save passwords to the database.",
        )

    def handle(self, *args: list, **options: dict) -> None:  # noqa: ARG002
        logger = logging.getLogger(self.__class__.__module__)
        count = SupabaseUser.objects.count()
        logger.info("Rotating password of %s users.", count)

        if options["wet_run"]:
            for user in SupabaseUser.objects.iterator(chunk_size=100):
                user.update_password()

        logger.info("Rotation is over!")
