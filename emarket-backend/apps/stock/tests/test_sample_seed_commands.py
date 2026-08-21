from io import StringIO

from django.core.management import CommandError, call_command
from django.test import TestCase

from apps.stock.enums import MarketListingStatus
from apps.stock.models import Brand, BrandSeries, Product, ProductCategory
from apps.stock.sample_data import BRANDS, PRODUCTS


def category_count(nodes):
    return sum(1 + category_count(node.get("children", ())) for node in nodes)


class StockSampleSeedCommandTests(TestCase):
    def test_full_seed_is_complete_and_idempotent(self):
        from apps.stock.sample_data import CATEGORY_TREE

        first_output = StringIO()
        call_command("seed_stock_sample", stdout=first_output)

        expected_series = {
            (record["brand"], record["series_slug"]) for record in PRODUCTS
        }
        self.assertEqual(ProductCategory.objects.count(), category_count(CATEGORY_TREE))
        self.assertEqual(Brand.objects.count(), len(BRANDS))
        self.assertEqual(Product.objects.count(), len(PRODUCTS))
        self.assertEqual(BrandSeries.objects.count(), len(expected_series))
        self.assertEqual(
            set(
                ProductCategory.objects.filter(parent__isnull=True).values_list(
                    "slug", flat=True
                )
            ),
            {"data-center", "office-enterprise", "home", "workstation"},
        )
        self.assertFalse(Product.objects.filter(is_market_visible=True).exists())
        self.assertFalse(
            Product.objects.exclude(market_status=MarketListingStatus.DRAFT).exists()
        )
        self.assertFalse(Product.objects.exclude(market_quantity=0).exists())
        self.assertFalse(
            Product.objects.exclude(additional_specs__sample_data=True).exists()
        )

        ids_before = dict(Product.objects.values_list("sku", "id"))
        second_output = StringIO()
        call_command("seed_stock_sample", stdout=second_output)

        self.assertEqual(dict(Product.objects.values_list("sku", "id")), ids_before)
        self.assertEqual(ProductCategory.objects.count(), category_count(CATEGORY_TREE))
        self.assertEqual(Brand.objects.count(), len(BRANDS))
        self.assertEqual(Product.objects.count(), len(PRODUCTS))
        self.assertIn(f"products: total={len(PRODUCTS)}", second_output.getvalue())
        self.assertIn(f"unchanged={len(PRODUCTS)}", second_output.getvalue())

    def test_dry_run_rolls_back_everything(self):
        output = StringIO()
        call_command("seed_stock_sample", "--dry-run", stdout=output)

        self.assertEqual(ProductCategory.objects.count(), 0)
        self.assertEqual(Brand.objects.count(), 0)
        self.assertEqual(BrandSeries.objects.count(), 0)
        self.assertEqual(Product.objects.count(), 0)
        self.assertIn("DRY RUN", output.getvalue())

    def test_product_seed_reports_missing_prerequisites(self):
        with self.assertRaisesMessage(CommandError, "Run seed_stock_categories"):
            call_command("seed_stock_products")

    def test_individual_commands_can_be_composed(self):
        call_command("seed_stock_categories", stdout=StringIO())
        call_command("seed_stock_brands", stdout=StringIO())
        call_command("seed_stock_products", stdout=StringIO())

        self.assertEqual(Product.objects.count(), len(PRODUCTS))
