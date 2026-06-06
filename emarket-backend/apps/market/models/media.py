import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.market.enums import MediaType


class ProductMedia(models.Model):
    """
    گالری تصاویر و ویدیوهای محصول در مارکت
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    product = models.ForeignKey(
        'market.MarketProduct',
        on_delete=models.CASCADE,
        related_name='media',
        verbose_name=_('Product')
    )

    media_type = models.CharField(
        _('Type'),
        max_length=10,
        choices=MediaType.choices,
        default=MediaType.GALLERY
    )

    # ==================== File ====================
    image = models.ImageField(
        _('Image'),
        upload_to='market/gallery/%Y/%m/',
        null=True,
        blank=True
    )

    video_url = models.URLField(
        _('Video URL'),
        blank=True,
        help_text=_('YouTube, Aparat, or direct video URL')
    )

    video_thumbnail = models.ImageField(
        _('Video Thumbnail'),
        upload_to='market/videos/thumbnails/',
        null=True,
        blank=True
    )

    # ==================== Info ====================
    title = models.CharField(_('Title'), max_length=200, blank=True)
    alt_text = models.CharField(_('Alt Text'), max_length=200, blank=True)

    sort_order = models.PositiveIntegerField(_('Sort Order'), default=0)
    is_main = models.BooleanField(_('Main Image'), default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product_media'
        verbose_name = _('Product Media')
        verbose_name_plural = _('Product Media')
        ordering = ['sort_order', 'created_at']

    def __str__(self):
        return f"{self.get_media_type_display()}: {self.product.title[:30]}"