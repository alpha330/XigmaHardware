"""Curated, deterministic sample catalog used by stock seed commands."""

from .brands import BRANDS
from .categories import CATEGORY_TREE
from .products import PRODUCTS

__all__ = ["BRANDS", "CATEGORY_TREE", "PRODUCTS"]
