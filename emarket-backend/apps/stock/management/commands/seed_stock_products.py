from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.stock.management.commands._sample_seed import format_stats
from apps.stock.sample_data.seeder import SampleDataDependencyError, seed_products


class Command(BaseCommand):
    help = "Create or update recent-generation sample stock products and series."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate and display the result without committing database changes.",
        )

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                product_stats, series_stats = seed_products()
                if options["dry_run"]:
                    transaction.set_rollback(True)
        except SampleDataDependencyError as exc:
            raise CommandError(str(exc)) from exc

        prefix = "DRY RUN - " if options["dry_run"] else ""
        self.stdout.write(
            self.style.SUCCESS(prefix + format_stats("series", series_stats))
        )
        self.stdout.write(
            self.style.SUCCESS(prefix + format_stats("products", product_stats))
        )
