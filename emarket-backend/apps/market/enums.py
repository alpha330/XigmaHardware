from django.db import models
from django.utils.translation import gettext_lazy as _


class RatingCategory(models.TextChoices):
    """دسته‌بندی امتیازدهی"""
    VALUE_FOR_MONEY = 'value_for_money', _('Value for Money')     # ارزش خرید
    QUALITY = 'quality', _('Product Quality')                     # کیفیت محصول
    PERFORMANCE = 'performance', _('Performance')                 # کارایی
    OVERALL = 'overall', _('Overall Rating')                      # امتیاز کلی


class ReviewStatus(models.TextChoices):
    """وضعیت ریویو"""
    DRAFT = 'draft', _('Draft')
    PUBLISHED = 'published', _('Published')
    HIDDEN = 'hidden', _('Hidden')
    REPORTED = 'reported', _('Reported')


class CommentStatus(models.TextChoices):
    """وضعیت کامنت"""
    ACTIVE = 'active', _('Active')
    HIDDEN = 'hidden', _('Hidden')
    DELETED = 'deleted', _('Deleted')


class MediaType(models.TextChoices):
    """نوع مدیا"""
    IMAGE = 'image', _('Image')
    VIDEO = 'video', _('Video')
    GALLERY = 'gallery', _('Gallery Image')