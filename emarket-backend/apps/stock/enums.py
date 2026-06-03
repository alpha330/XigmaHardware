from django.db import models
from django.utils.translation import gettext_lazy as _


class WarehouseType(models.TextChoices):
    """نوع انبار"""
    MAIN = 'main', _('Main Warehouse')
    SUB = 'sub', _('Sub Warehouse')
    SPECIALIZED = 'specialized', _('Specialized Warehouse')
    TEMPORARY = 'temporary', _('Temporary Warehouse')


class WarehouseScope(models.TextChoices):
    """محدوده انبار"""
    GENERAL = 'general', _('General - All Hardware')
    SPECIALIZED = 'specialized', _('Specialized - Specific Hardware')


class ProductCondition(models.TextChoices):
    """وضعیت کالا"""
    NEW = 'new', _('New - Brand New')
    LIKE_NEW = 'like_new', _('Like New - Open Box')
    USED = 'used', _('Used - Second Hand')
    REFURBISHED = 'refurbished', _('Refurbished')
    DAMAGED = 'damaged', _('Damaged - For Parts')


class ProductCategoryType(models.TextChoices):
    """نوع دسته‌بندی کالا"""
    CONDITION = 'condition', _('Condition')       # نو/آکبند، دسته دو
    USAGE = 'usage', _('Usage')                   # سرور، خانگی، پرتابل
    BRAND = 'brand', _('Brand')                   # HP, Dell, Lenovo
    TYPE = 'type', _('Type')                      # Server, Laptop, Desktop
    SERIES = 'series', _('Series & Year')         # G10, 2023


class InventoryStatus(models.TextChoices):
    """وضعیت موجودی"""
    IN_STOCK = 'in_stock', _('In Stock')
    RESERVED = 'reserved', _('Reserved')
    IN_TRANSIT = 'in_transit', _('In Transit')
    DAMAGED = 'damaged', _('Damaged')
    RETURNED = 'returned', _('Returned')


class MarketListingStatus(models.TextChoices):
    """وضعیت انتشار در مارکت"""
    DRAFT = 'draft', _('Draft')
    PUBLISHED = 'published', _('Published')
    ARCHIVED = 'archived', _('Archived')
    SOLD_OUT = 'sold_out', _('Sold Out')