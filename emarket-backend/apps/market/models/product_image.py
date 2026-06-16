import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

class ProductImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        'market.MarketProduct',
        on_delete=models.CASCADE,
        related_name='product_images'
    )
    image = models.ImageField(_('Image'), upload_to='market/products/images/%Y/%m/')
    title = models.CharField(_('Title'), max_length=200, blank=True)
    is_main = models.BooleanField(_('Main Image'), default=False)
    sort_order = models.PositiveIntegerField(_('Sort Order'), default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'market_product_images'
        verbose_name = _('Product Image')
        verbose_name_plural = _('Product Images')
        ordering = ['sort_order', 'created_at']

    def __str__(self):
        return f"Image for {self.product.title[:30]}"