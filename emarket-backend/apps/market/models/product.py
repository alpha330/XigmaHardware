import uuid
from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.stock.models import Product as StockProduct


class MarketProduct(models.Model):
    """
    محصول در مارکت

    ارتباط با Stock Product - وقتی محصول از انبار به مارکت میاد
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # ==================== Link to Stock ====================
    stock_product = models.OneToOneField(
        StockProduct,
        on_delete=models.CASCADE,
        related_name='market_product',
        verbose_name=_('Stock Product'),
        limit_choices_to={'is_market_visible': True}
    )

    # ==================== Market Info ====================
    title = models.CharField(_('Market Title'), max_length=500, db_index=True)

    slug = models.SlugField(_('Slug'), max_length=550, unique=True)

    short_description = models.TextField(
        _('Short Description'),
        max_length=500,
        blank=True
    )

    full_description = models.TextField(
        _('Full Description'),
        blank=True
    )

    # ==================== Pricing ====================
    market_price = models.DecimalField(
        _('Market Price'),
        max_digits=15,
        decimal_places=2,
        db_index=True
    )

    discount_price = models.DecimalField(
        _('Discount Price'),
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )

    discount_percent = models.DecimalField(
        _('Discount %'),
        max_digits=5,
        decimal_places=2,
        default=0
    )

    discount_start = models.DateTimeField(null=True, blank=True)
    discount_end = models.DateTimeField(null=True, blank=True)

    # ==================== Stock ====================
    available_quantity = models.PositiveIntegerField(
        _('Available Quantity'),
        default=0,
        help_text=_('Synced with stock product market_quantity')
    )

    min_order_quantity = models.PositiveIntegerField(
        _('Min Order'),
        default=1
    )

    max_order_quantity = models.PositiveIntegerField(
        _('Max Order'),
        default=10
    )

    # ==================== Tags & SEO ====================
    tags = models.CharField(_('Tags'), max_length=500, blank=True)

    meta_title = models.CharField(_('Meta Title'), max_length=200, blank=True)
    meta_description = models.TextField(_('Meta Description'), max_length=300, blank=True)
    meta_keywords = models.CharField(_('Meta Keywords'), max_length=300, blank=True)

    # ==================== Stats ====================
    views_count = models.PositiveIntegerField(_('Views'), default=0)
    sales_count = models.PositiveIntegerField(_('Sales'), default=0)
    wishlist_count = models.PositiveIntegerField(_('Wishlists'), default=0)

    # ==================== Ratings (Cached) ====================
    avg_rating = models.DecimalField(
        _('Average Rating'),
        max_digits=3,
        decimal_places=2,
        default=0
    )

    rating_count = models.PositiveIntegerField(_('Rating Count'), default=0)

    avg_value_for_money = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    avg_quality = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    avg_performance = models.DecimalField(max_digits=3, decimal_places=2, default=0)

    # ==================== Status ====================
    is_active = models.BooleanField(_('Active'), default=True, db_index=True)
    is_featured = models.BooleanField(_('Featured'), default=False)
    is_bestseller = models.BooleanField(_('Bestseller'), default=False)

    priority = models.PositiveIntegerField(_('Priority'), default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'market_products'
        verbose_name = _('Market Product')
        verbose_name_plural = _('Market Products')
        ordering = ['-priority', '-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'is_featured']),
            models.Index(fields=['avg_rating']),
            models.Index(fields=['market_price']),
        ]

    def __str__(self):
        return f"🛒 {self.title}"

    @property
    def final_price(self):
        """قیمت نهایی با تخفیف"""
        from django.utils import timezone
        now = timezone.now()

        if self.discount_price and self.discount_start and self.discount_end:
            if self.discount_start <= now <= self.discount_end:
                return self.discount_price

        if self.discount_percent > 0:
            return self.market_price * (1 - self.discount_percent / 100)

        return self.market_price

    @property
    def has_discount(self):
        from django.utils import timezone
        now = timezone.now()

        if self.discount_price and self.discount_start and self.discount_end:
            if self.discount_start <= now <= self.discount_end:
                return True

        return self.discount_percent > 0

    @property
    def is_in_stock(self):
        return self.available_quantity > 0

    @property
    def stock_info(self):
        """اطلاعات محصول از انبار"""
        return {
            'sku': self.stock_product.sku,
            'condition': self.stock_product.condition,
            'brand': self.stock_product.brand.name if self.stock_product.brand else None,
            'category': self.stock_product.category.name if self.stock_product.category else None,
            'processor': self.stock_product.processor,
            'ram': self.stock_product.ram,
            'storage': self.stock_product.storage,
            'form_factor': self.stock_product.form_factor,
        }

    def increment_views(self):
        """افزایش بازدید"""
        self.views_count += 1
        self.save(update_fields=['views_count'])

    def update_ratings_cache(self):
        """بروزرسانی کش امتیازات"""
        ratings = self.ratings.filter(is_active=True)
        count = ratings.count()

        if count > 0:
            from django.db.models import Avg
            self.rating_count = count
            self.avg_rating = ratings.aggregate(Avg('overall'))['overall__avg'] or 0
            self.avg_value_for_money = ratings.aggregate(Avg('value_for_money'))['value_for_money__avg'] or 0
            self.avg_quality = ratings.aggregate(Avg('quality'))['quality__avg'] or 0
            self.avg_performance = ratings.aggregate(Avg('performance'))['performance__avg'] or 0
        else:
            self.rating_count = 0
            self.avg_rating = 0
            self.avg_value_for_money = 0
            self.avg_quality = 0
            self.avg_performance = 0

        self.save()