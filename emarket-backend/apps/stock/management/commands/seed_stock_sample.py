from django.core.management.base import BaseCommand
from django.db import transaction

from apps.stock.management.commands._sample_seed import format_stats
from apps.stock.sample_data.seeder import (
    seed_brands,
    seed_categories,
    seed_products,
)


class Command(BaseCommand):
    help = "Create or update the complete Xigma stock sample catalog."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate and display the result without committing database changes.",
        )

    def handle(self, *args, **options):
        with transaction.atomic():
            category_stats = seed_categories()
            brand_stats = seed_brands()
            product_stats, series_stats = seed_products()
            if options["dry_run"]:
                transaction.set_rollback(True)

        prefix = "DRY RUN - " if options["dry_run"] else ""
        for label, stats in (
            ("categories", category_stats),
            ("brands", brand_stats),
            ("series", series_stats),
            ("products", product_stats),
        ):
            self.stdout.write(self.style.SUCCESS(prefix + format_stats(label, stats)))
