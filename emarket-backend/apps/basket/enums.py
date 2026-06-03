from django.db import models
from django.utils.translation import gettext_lazy as _


class CartType(models.TextChoices):
    """نوع سبد خرید"""
    CART = 'cart', _('Shopping Cart')
    WISHLIST = 'wishlist', _('Wishlist')


class CartStatus(models.TextChoices):
    """وضعیت سبد خرید"""
    ACTIVE = 'active', _('Active')
    CHECKOUT = 'checkout', _('In Checkout')
    ORDERED = 'ordered', _('Ordered')
    ABANDONED = 'abandoned', _('Abandoned')
    CONVERTED = 'converted', _('Converted from Wishlist')


class DiscountType(models.TextChoices):
    """نوع تخفیف"""
    PERCENT = 'percent', _('Percentage')
    FIXED = 'fixed', _('Fixed Amount')
