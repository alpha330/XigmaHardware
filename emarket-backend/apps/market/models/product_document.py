import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

class ProductDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        'market.MarketProduct',
        on_delete=models.CASCADE,
        related_name='product_documents'
    )
    title = models.CharField(_('Title'), max_length=200)
    file = models.FileField(_('File'), upload_to='market/products/documents/%Y/%m/')
    doc_type = models.CharField(
        _('Document Type'),
        max_length=50,
        choices=[
            ('datasheet', _('Datasheet')),
            ('manual', _('Manual')),
            ('warranty', _('Warranty Card')),
            ('certificate', _('Certificate')),
            ('other', _('Other')),
        ],
        default='other'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'market_product_documents'
        verbose_name = _('Product Document')
        verbose_name_plural = _('Product Documents')
        ordering = ['doc_type', 'title']

    def __str__(self):
        return f"{self.title} - {self.product.title[:30]}"