import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class Brand(models.Model):
    """
    مدل برند محصولات
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.CharField(
        _('Brand Name'),
        max_length=200,
        unique=True,
        db_index=True
    )

    slug = models.SlugField(
        _('Slug'),
        max_length=250,
        unique=True
    )

    # ==================== Info ====================
    persian_name = models.CharField(
        _('Persian Name'),
        max_length=200,
        blank=True,
        help_text=_('نام فارسی برند')
    )

    logo = models.ImageField(
        _('Logo'),
        upload_to='brands/logos/',
        null=True,
        blank=True
    )

    website = models.URLField(
        _('Website'),
        blank=True
    )

    country = models.CharField(
        _('Country of Origin'),
        max_length=100,
        blank=True
    )

    # ==================== Description ====================
    description = models.TextField(_('Description'), blank=True)

    warranty_info = models.TextField(
        _('Warranty Information'),
        blank=True,
        help_text=_('General warranty policy for this brand')
    )

    # ==================== Status ====================
    is_active = models.BooleanField(_('Active'), default=True, db_index=True)
    is_partner = models.BooleanField(
        _('Official Partner'),
        default=False,
        help_text=_('Are we an official partner/reseller?')
    )

    # ==================== Meta ====================
    popularity_score = models.PositiveIntegerField(
        _('Popularity Score'),
        default=0,
        help_text=_('Based on sales and views')
    )

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        db_table = 'brands'
        verbose_name = _('Brand')
        verbose_name_plural = _('Brands')
        ordering = ['-popularity_score', 'name']
        indexes = [
            models.Index(fields=['is_active', 'is_partner']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.persian_name or self.name

    @property
    def products_count(self):
        return self.products.count()

    @property
    def active_products_count(self):
        return self.products.filter(is_active=True).count()


class BrandSeries(models.Model):
    """
    سری/مدل برند - مثلاً HP ProLiant DL380 G10
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name='series',
        verbose_name=_('Brand')
    )

    name = models.CharField(
        _('Series Name'),
        max_length=200,
        db_index=True
    )

    slug = models.SlugField(_('Slug'), max_length=250)

    # ==================== Specs ====================
    year_released = models.PositiveIntegerField(
        _('Year Released'),
        null=True,
        blank=True
    )

    generation = models.CharField(
        _('Generation'),
        max_length=50,
        blank=True,
        help_text=_('e.g., G10, G11, Gen 2')
    )

    # ==================== Category ====================
    category = models.ForeignKey(
        'stock.ProductCategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='series',
        verbose_name=_('Product Category'),
        limit_choices_to={'category_type': 'series'}
    )

    description = models.TextField(_('Description'), blank=True)

    is_active = models.BooleanField(_('Active'), default=True)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        db_table = 'brand_series'
        verbose_name = _('Brand Series')
        verbose_name_plural = _('Brand Series')
        ordering = ['brand__name', '-year_released', 'name']
        unique_together = [
            ['brand', 'slug'],
        ]
        indexes = [
            models.Index(fields=['brand', 'is_active']),
        ]

    def __str__(self):
        return f"{self.brand.name} {self.name} ({self.generation or self.year_released or ''})"

    @property
    def full_name(self):
        parts = [self.brand.name, self.name]
        if self.generation:
            parts.append(self.generation)
        if self.year_released:
            parts.append(str(self.year_released))
        return ' '.join(parts)