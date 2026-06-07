import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class News(models.Model):
    """اخبار و اطلاعیه‌ها"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(_('Title'), max_length=300)
    slug = models.SlugField(unique=True)

    excerpt = models.TextField(_('Excerpt'), max_length=500, blank=True)
    content = models.TextField(_('Content'))

    image = models.ImageField(upload_to='news/%Y/%m/', null=True, blank=True)

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('pinned', 'Pinned'),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft')

    is_important = models.BooleanField(default=False)

    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'news'
        ordering = ['-published_at', '-created_at']
        verbose_name_plural = 'News'

    def __str__(self):
        return self.title