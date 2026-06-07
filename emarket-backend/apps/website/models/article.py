import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import User


class ArticleCategory(models.Model):
    """دسته‌بندی مقالات"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('Name'), max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'article_categories'

    def __str__(self):
        return self.name


class Article(models.Model):
    """مقالات وبسایت"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(_('Title'), max_length=300, db_index=True)
    slug = models.SlugField(unique=True)

    category = models.ForeignKey(ArticleCategory, on_delete=models.SET_NULL, null=True, related_name='articles')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    excerpt = models.TextField(_('Excerpt'), max_length=500, blank=True)
    content = models.TextField(_('Content'))

    image = models.ImageField(upload_to='articles/%Y/%m/', null=True, blank=True)

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft')

    is_featured = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)

    tags = models.CharField(max_length=300, blank=True)

    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(max_length=300, blank=True)

    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'articles'
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title