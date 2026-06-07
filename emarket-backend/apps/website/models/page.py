import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class Page(models.Model):
    """صفحات وبسایت (About Us, Terms, Privacy, ...)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(_('Title'), max_length=200)
    slug = models.SlugField(_('Slug'), unique=True)

    PAGE_TYPES = [
        ('about', 'About Us'),
        ('terms', 'Terms & Conditions'),
        ('privacy', 'Privacy Policy'),
        ('faq', 'FAQ Page'),
        ('contact', 'Contact Page'),
        ('custom', 'Custom Page'),
    ]
    page_type = models.CharField(_('Type'), max_length=20, choices=PAGE_TYPES, default='custom')

    content = models.TextField(_('Content'))

    meta_title = models.CharField(_('Meta Title'), max_length=200, blank=True)
    meta_description = models.TextField(_('Meta Description'), max_length=300, blank=True)

    is_active = models.BooleanField(_('Active'), default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'website_pages'
        ordering = ['page_type', 'title']

    def __str__(self):
        return self.title