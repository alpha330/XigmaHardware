"""Idempotent persistence helpers for the stock sample catalog."""

from dataclasses import dataclass
from decimal import Decimal

from django.db import models

from apps.stock.enums import MarketListingStatus, ProductCondition
from apps.stock.models import Brand, BrandSeries, Product, ProductCategory

from .brands import BRANDS
from .categories import CATEGORY_TREE
from .products import PRODUCTS


SAMPLE_DATA_MARKER = "xigma-stock-sample-v1"


class SampleDataDependencyError(RuntimeError):
    """Raised when a seed command is missing one of its prerequisite records."""


@dataclass
class SeedStats:
    created: int = 0
    updated: int = 0
    unchanged: int = 0

    @property
    def total(self):
        return self.created + self.updated + self.unchanged

    def add(self, status):
        setattr(self, status, getattr(self, status) + 1)


def _value_for_comparison(instance, field_name):
    field = instance._meta.get_field(field_name)
    if isinstance(field, (models.ForeignKey, models.OneToOneField)):
        return getattr(instance, f"{field_name}_id")
    return getattr(instance, field_name)


def _expected_for_comparison(instance, field_name, value):
    field = instance._meta.get_field(field_name)
    if isinstance(field, (models.ForeignKey, models.OneToOneField)):
        return value.pk if value is not None else None
    return value


def _upsert(model, lookup, defaults):
    instance = model.objects.filter(**lookup).first()
    if instance is None:
        return model.objects.create(**lookup, **defaults), "created"

    changed_fields = []
    for field_name, value in defaults.items():
        current = _value_for_comparison(instance, field_name)
        expected = _expected_for_comparison(instance, field_name, value)
        if current != expected:
            setattr(instance, field_name, value)
            changed_fields.append(field_name)

    if not changed_fields:
        return instance, "unchanged"

    if any(field.name == "updated_at" for field in instance._meta.fields):
        changed_fields.append("updated_at")
    instance.save(update_fields=changed_fields)
    return instance, "updated"


def seed_categories():
    stats = SeedStats()

    def persist(nodes, parent=None, level=0):
        for sort_order, node in enumerate(nodes, start=1):
            defaults = {
                "name": node["name"],
                "category_type": node["category_type"],
                "parent": parent,
                "condition": None,
                "description": f"دسته‌بندی نمونه کاتالوگ زیگما: {node['name']}",
                "is_active": True,
                "is_featured": node.get("is_featured", False),
                "level": level,
                "sort_order": sort_order,
            }
            category, status = _upsert(
                ProductCategory,
                {"slug": node["slug"]},
                defaults,
            )
            stats.add(status)
            persist(node.get("children", ()), parent=category, level=level + 1)

    persist(CATEGORY_TREE)
    return stats


def seed_brands():
    stats = SeedStats()
    for record in BRANDS:
        defaults = {
            "name": record["name"],
            "persian_name": record["persian_name"],
            "website": record["website"],
            "country": record["country"],
            "description": f"برند نمونه حوزه سخت‌افزار و فناوری اطلاعات: {record['name']}",
            "is_active": True,
            "is_partner": False,
            "popularity_score": record["popularity_score"],
        }
        _, status = _upsert(Brand, {"slug": record["slug"]}, defaults)
        stats.add(status)
    return stats


def seed_products():
    stats = SeedStats()
    series_stats = SeedStats()
    category_slugs = {record["category"] for record in PRODUCTS}
    brand_slugs = {record["brand"] for record in PRODUCTS}

    categories = {
        item.slug: item
        for item in ProductCategory.objects.filter(slug__in=category_slugs)
    }
    brands = {item.slug: item for item in Brand.objects.filter(slug__in=brand_slugs)}

    missing_categories = sorted(category_slugs - categories.keys())
    missing_brands = sorted(brand_slugs - brands.keys())
    if missing_categories or missing_brands:
        details = []
        if missing_categories:
            details.append(f"missing categories: {', '.join(missing_categories)}")
        if missing_brands:
            details.append(f"missing brands: {', '.join(missing_brands)}")
        raise SampleDataDependencyError(
            "; ".join(details)
            + ". Run seed_stock_categories and seed_stock_brands first."
        )

    for record in PRODUCTS:
        category = categories[record["category"]]
        brand = brands[record["brand"]]
        series_defaults = {
            "name": record["series_name"],
            "year_released": record["year"],
            "generation": record["generation"],
            "category": category,
            "description": "سری نمونه ایجادشده توسط seed کاتالوگ زیگما.",
            "is_active": True,
        }
        series, series_status = _upsert(
            BrandSeries,
            {"brand": brand, "slug": record["series_slug"]},
            series_defaults,
        )
        series_stats.add(series_status)

        sample_price = Decimal(record["sample_price"])
        additional_specs = {
            "sample_data": True,
            "sample_data_source": SAMPLE_DATA_MARKER,
            "price_is_sample": True,
            "release_year": record["year"],
            "generation": record["generation"],
        }
        product_defaults = {
            "name": record["name"],
            "slug": record["slug"],
            "condition": ProductCondition.NEW,
            "category": category,
            "brand": brand,
            "series": series,
            "model_number": record["model_number"],
            "additional_specs": additional_specs,
            "cost_price": (sample_price * Decimal("0.82")).quantize(Decimal("1")),
            "selling_price": sample_price,
            "market_price": None,
            "discount_percent": Decimal("0"),
            "currency": "IRR",
            "market_status": MarketListingStatus.DRAFT,
            "market_quantity": 0,
            "is_market_visible": False,
            "market_description": (
                "این رکورد صرفاً داده نمونه توسعه است؛ قیمت آن واقعی یا به‌روز نیست."
            ),
            "market_tags": record["tags"],
            "is_active": True,
        }
        product_defaults.update(record["fields"])
        _, status = _upsert(Product, {"sku": record["sku"]}, product_defaults)
        stats.add(status)

    return stats, series_stats
