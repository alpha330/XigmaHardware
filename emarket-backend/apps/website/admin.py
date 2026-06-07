from django.contrib import admin
from django.utils.html import format_html
from .models import Page, Article, ArticleCategory, News, ContactMessage, Newsletter


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ['title', 'page_type', 'is_active', 'updated_at']
    list_filter = ['page_type', 'is_active']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(ArticleCategory)
class ArticleCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'status_badge', 'is_featured', 'views_count', 'published_at']
    list_filter = ['status', 'category', 'is_featured']
    search_fields = ['title', 'content', 'tags']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views_count']

    def status_badge(self, obj):
        colors = {'draft': '#6c757d', 'published': '#28a745', 'archived': '#dc3545'}
        return format_html('<span style="background:{};color:white;padding:2px 6px;border-radius:4px;">{}</span>', colors.get(obj.status, '#6c757d'), obj.get_status_display())
    status_badge.short_description = 'Status'


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'status_badge', 'is_important', 'published_at']
    list_filter = ['status', 'is_important']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}

    def status_badge(self, obj):
        colors = {'draft': '#6c757d', 'published': '#28a745', 'pinned': '#ffc107'}
        return format_html('<span style="background:{};color:white;padding:2px 6px;border-radius:4px;">{}</span>', colors.get(obj.status, '#6c757d'), obj.get_status_display())
    status_badge.short_description = 'Status'


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject_short', 'is_read_badge', 'created_at']
    list_filter = ['is_read', 'is_replied']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['name', 'email', 'phone', 'subject', 'message', 'ip_address', 'created_at']

    def subject_short(self, obj): return obj.subject[:50]
    subject_short.short_description = 'Subject'

    def is_read_badge(self, obj):
        return '✅' if obj.is_read else '📩'
    is_read_badge.short_description = 'Read'


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_active_badge', 'subscribed_at']
    list_filter = ['is_active']
    search_fields = ['email']

    def is_active_badge(self, obj): return '✅' if obj.is_active else '❌'
    is_active_badge.short_description = 'Active'