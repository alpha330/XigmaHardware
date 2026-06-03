import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.stock.enums import ProductCondition, ProductCategoryType


class ProductCategory(models.Model):
    """
    دسته‌بندی چندسطحی محصولات

    ساختار:
    - وضعیت (نو/دسته دو)
      └── کاربری (سرور/خانگی/پرتابل/ورک‌استیشن)
          └── برند (HP/Dell/Lenovo)
              └── نوع (Server/Laptop/Desktop)
                  └── سری/سال (G10/2023)
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.CharField(
        _('Category Name'),
        max_length=200,
        db_index=True
    )

    slug = models.SlugField(
        _('Slug'),
        max_length=250,
        unique=True
    )

    category_type = models.CharField(
        _('Category Type'),
        max_length=20,
        choices=ProductCategoryType.choices,
        db_index=True
    )

    # ==================== Hierarchy ====================
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_('Parent Category')
    )

    # ==================== Condition (فقط برای سطح اول) ====================
    condition = models.CharField(
        _('Condition'),
        max_length=20,
        choices=ProductCondition.choices,
        null=True,
        blank=True,
        help_text=_('Only for top-level categories')
    )

    # ==================== Display ====================
    icon = models.ImageField(
        _('Icon'),
        upload_to='categories/icons/',
        null=True,
        blank=True
    )

    image = models.ImageField(
        _('Image'),
        upload_to='categories/images/',
        null=True,
        blank=True
    )

    description = models.TextField(_('Description'), blank=True)

    # ==================== Meta ====================
    is_active = models.BooleanField(_('Active'), default=True, db_index=True)
    is_featured = models.BooleanField(_('Featured'), default=False)

    level = models.PositiveSmallIntegerField(
        _('Level'),
        default=0,
        help_text=_('Category depth: 0=root, 1=condition, 2=usage, 3=brand, 4=type, 5=series')
    )

    sort_order = models.PositiveIntegerField(_('Sort Order'), default=0)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        db_table = 'product_categories'
        verbose_name = _('Product Category')
        verbose_name_plural = _('Product Categories')
        ordering = ['level', 'sort_order', 'name']
        indexes = [
            models.Index(fields=['category_type', 'is_active']),
            models.Index(fields=['parent', 'is_active']),
            models.Index(fields=['slug']),
        ]
        unique_together = [
            ['slug', 'parent'],
        ]

    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"

    @property
    def is_root(self):
        return self.parent is None

    @property
    def is_leaf(self):
        return not self.children.exists()

    def get_ancestors(self):
        """دریافت مسیر کامل دسته‌بندی"""
        ancestors = []
        current = self.parent
        while current:
            ancestors.insert(0, current)
            current = current.parent
        return ancestors

    def get_full_path(self):
        """مسیر کامل: نو > سرور > HP > Server > G10"""
        path = self.get_ancestors()
        path.append(self)
        return ' > '.join([cat.name for cat in path])

    def get_descendants(self, include_self=False):
        """دریافت همه زیرمجموعه‌ها"""
        descendants = []
        if include_self:
            descendants.append(self)
        for child in self.children.all():
            descendants.extend(child.get_descendants(include_self=True))
        return descendants