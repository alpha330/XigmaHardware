import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class FAQCategory(models.Model):
    """دسته‌بندی FAQ"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('Name'), max_length=200)
    slug = models.SlugField(unique=True)
    icon = models.CharField(_('Icon'), max_length=50, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'faq_categories'
        ordering = ['sort_order']

    def __str__(self):
        return self.name


class FAQ(models.Model):
    """سوال متداول"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    category = models.ForeignKey(FAQCategory, on_delete=models.CASCADE, related_name='faqs')

    question = models.TextField(_('Question'))
    answer = models.TextField(_('Answer'))

    is_active = models.BooleanField(default=True)
    views_count = models.PositiveIntegerField(default=0)
    helpful_count = models.PositiveIntegerField(default=0)

    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'faqs'
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return self.question[:80]