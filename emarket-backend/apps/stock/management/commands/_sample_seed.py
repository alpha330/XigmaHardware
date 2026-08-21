from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.stock.sample_data.seeder import SampleDataDependencyError


def format_stats(label, stats):
    return (
        f"{label}: total={stats.total}, created={stats.created}, "
        f"updated={stats.updated}, unchanged={stats.unchanged}"
    )


class BaseSampleSeedCommand(BaseCommand):
    seed_function = None
    result_label = "records"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate and display the result without committing database changes.",
        )

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                stats = self.seed_function()
                if options["dry_run"]:
                    transaction.set_rollback(True)
        except SampleDataDependencyError as exc:
            raise CommandError(str(exc)) from exc

        prefix = "DRY RUN - " if options["dry_run"] else ""
        self.stdout.write(
            self.style.SUCCESS(prefix + format_stats(self.result_label, stats))
        )
