from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import (
    MarketProduct, ProductRating, ProductReview, ReviewLike,
    ProductComment, ProductMedia
)


# ----- Inline ها (بدون ProductImage/ProductDocument که قبلاً داشتیم) -----
class RatingInline(admin.TabularInline):
    model = ProductRating
    extra = 0
    fields = ['user', 'overall', 'value_for_money', 'quality', 'performance', 'is_verified_purchase']
    readonly_fields = ['user', 'overall', 'value_for_money', 'quality', 'performance', 'is_verified_purchase']
    can_delete = False
    max_num = 0


class ReviewInline(admin.TabularInline):
    model = ProductReview
    extra = 0
    fields = ['user', 'title', 'likes_count', 'status', 'created_at']
    readonly_fields = ['user', 'title', 'likes_count', 'status', 'created_at']
    can_delete = False
    max_num = 0


# ======================= MarketProduct Admin =======================
@admin.register(MarketProduct)
class MarketProductAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'stock_product_sku', 'brand_info',
        'price_info', 'avg_rating_stars',
         'is_active', 'created_at_jalali'
    ]
    list_filter = [
        'is_active', 'is_featured',
        'stock_product__condition',   # ← از طریق رابطه
        'stock_product__brand',
        'created_at'
    ]
    search_fields = [
        'title', 'stock_product__sku', 'stock_product__name',
        'tags', 'stock_product__brand__name'
    ]
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'views_count', 'sales_count',
        'avg_rating', 'rating_count'
    ]
    autocomplete_fields = ['stock_product']

    # ===== fieldsets فقط با فیلدهای موجود در مدل =====
    fieldsets = (
        (_('Basic'), {'fields': ('stock_product', 'title', 'slug')}),
        (_('Pricing'), {'fields': ('market_price', 'discount_price', 'discount_percent',
                                   'discount_start', 'discount_end')}),
        (_('Descriptions'), {'fields': ('short_description', 'full_description')}),
        (_('Stock & Limits'), {'fields': ('available_quantity', 'min_order_quantity', 'max_order_quantity')}),
        (_('SEO'), {'fields': ('tags', 'meta_title', 'meta_description', 'meta_keywords')}),
        (_('Flags'), {'fields': ('is_active', 'is_featured', 'is_bestseller', 'priority')}),
        (_('Stats'), {'fields': ('views_count', 'sales_count', 'wishlist_count',
                                 'avg_rating', 'rating_count')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )

    inlines = [RatingInline, ReviewInline]

    # ----- متدهای نمایش -----
    @admin.display(description=_('Image'))
    def main_image_preview(self, obj):
        media = obj.media.filter(is_main=True).first()
        if not media:
            media = obj.media.first()
        if media and media.image:
            return format_html('<img src="{}" style="max-height:40px; border-radius:4px;" />', media.image.url)
        return '🖼️'

    @admin.display(description=_('SKU'), ordering='stock_product__sku')
    def stock_product_sku(self, obj):
        return obj.stock_product.sku

    @admin.display(description=_('Brand'))
    def brand_info(self, obj):
        sp = obj.stock_product
        if sp.brand:
            return sp.brand.persian_name or sp.brand.name
        return '-'

    @admin.display(description=_('Price'))
    def price_info(self, obj):
        final = obj.final_price
        if obj.has_discount:
            return format_html(
                '<span style="text-decoration:line-through; color:#999;">{:,}</span> '
                '<span style="color:#e94560; font-weight:bold;">{:,}</span>',
                int(obj.market_price), int(final)
            )
        return '{:,}'.format(int(final))

    @admin.display(description=_('Rating'))
    def avg_rating_stars(self, obj):
        stars = '⭐' * int(obj.avg_rating)
        return format_html('{} <small>({})</small>', stars, obj.rating_count)

    # @admin.display(description=_('Stock'))
    # def stock_summary(self, obj):
    #     return format_html('Total: <b>{}</b><br>Available: <b style="color:#28a745;">{}</b>',
    #                        obj.total_stock, obj.available_stock)

    @admin.display(description=_('Created'))
    def created_at_jalali(self, obj):
        try:
            import jdatetime
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        except:
            return obj.created_at.strftime('%Y-%m-%d %H:%M')

    actions = ['make_featured', 'unfeature']

    @admin.action(description=_('Mark as featured'))
    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, _('Products marked as featured.'))

    @admin.action(description=_('Remove featured'))
    def unfeature(self, request, queryset):
        queryset.update(is_featured=False)
        self.message_user(request, _('Featured removed.'))


# ======================= ProductRating Admin =======================
@admin.register(ProductRating)
class ProductRatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'overall_stars', 'value_for_money', 'quality',
                    'performance', 'is_verified_purchase', 'created_at_jalali']
    list_filter = ['is_active', 'is_verified_purchase', 'created_at']
    search_fields = ['user__email', 'product__title']
    readonly_fields = ['id', 'user', 'product', 'created_at', 'updated_at']

    def overall_stars(self, obj):
        return '⭐' * obj.overall
    overall_stars.short_description = _('Overall')

    def created_at_jalali(self, obj):
        try:
            import jdatetime
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        except:
            return obj.created_at.strftime('%Y-%m-%d %H:%M')
    created_at_jalali.short_description = _('Created')


# ======================= ProductReview Admin =======================
@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'title', 'likes_count', 'status_badge', 'created_at_jalali']
    list_filter = ['status', 'is_verified_purchase', 'created_at']
    search_fields = ['user__email', 'product__title', 'title', 'body']
    readonly_fields = ['id', 'user', 'product', 'likes_count', 'dislikes_count', 'created_at', 'updated_at']

    def status_badge(self, obj):
        colors = {'draft': '#6c757d', 'published': '#28a745', 'hidden': '#dc3545'}
        return format_html('<span style="background:{}; color:white; padding:2px 6px; border-radius:4px;">{}</span>',
                           colors.get(obj.status, '#6c757d'), obj.get_status_display())
    status_badge.short_description = _('Status')

    def created_at_jalali(self, obj):
        try:
            import jdatetime
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        except:
            return obj.created_at.strftime('%Y-%m-%d %H:%M')
    created_at_jalali.short_description = _('Created')

    actions = ['approve_reviews', 'hide_reviews']

    @admin.action(description=_('Approve selected'))
    def approve_reviews(self, request, queryset):
        queryset.update(status='published')
        self.message_user(request, _('Reviews approved.'))

    @admin.action(description=_('Hide selected'))
    def hide_reviews(self, request, queryset):
        queryset.update(status='hidden')
        self.message_user(request, _('Reviews hidden.'))


# ======================= ReviewLike Admin =======================
@admin.register(ReviewLike)
class ReviewLikeAdmin(admin.ModelAdmin):
    list_display = ['review', 'user', 'is_like', 'created_at']
    search_fields = ['review__title', 'user__email']
    readonly_fields = ['id', 'created_at']


# ======================= ProductComment Admin =======================
@admin.register(ProductComment)
class ProductCommentAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'body_short', 'parent_link', 'is_pinned', 'status_badge', 'created_at_jalali']
    list_filter = ['status', 'is_pinned', 'created_at']
    search_fields = ['user__email', 'product__title', 'body']
    readonly_fields = ['id', 'user', 'product', 'parent', 'created_at', 'updated_at']

    def body_short(self, obj):
        return obj.body[:80]
    body_short.short_description = _('Comment')

    def parent_link(self, obj):
        if obj.parent:
            return format_html('<a href="{}">{}</a>',
                               f'/admin/market/productcomment/{obj.parent.id}/change/',
                               obj.parent.body[:50])
        return '-'
    parent_link.short_description = _('Parent')

    def status_badge(self, obj):
        colors = {'active': '#28a745', 'hidden': '#dc3545', 'deleted': '#6c757d'}
        return format_html('<span style="background:{}; color:white; padding:2px 6px; border-radius:4px;">{}</span>',
                           colors.get(obj.status, '#6c757d'), obj.get_status_display())
    status_badge.short_description = _('Status')

    def created_at_jalali(self, obj):
        try:
            import jdatetime
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        except:
            return obj.created_at.strftime('%Y-%m-%d %H:%M')
    created_at_jalali.short_description = _('Created')

    actions = ['approve_comments', 'hide_comments']

    @admin.action(description=_('Activate selected'))
    def approve_comments(self, request, queryset):
        queryset.update(status='active')
        self.message_user(request, _('Comments activated.'))

    @admin.action(description=_('Hide selected'))
    def hide_comments(self, request, queryset):
        queryset.update(status='hidden')
        self.message_user(request, _('Comments hidden.'))


# ======================= ProductMedia Admin =======================
@admin.register(ProductMedia)
class ProductMediaAdmin(admin.ModelAdmin):
    list_display = ['product', 'media_type_badge', 'image_preview', 'is_main', 'sort_order']
    list_filter = ['media_type', 'is_main']
    search_fields = ['product__title', 'title']
    fields = ['product', 'media_type', 'image', 'video_url', 'video_thumbnail', 'title', 'alt_text', 'sort_order', 'is_main']

    def media_type_badge(self, obj):
        icons = {'image': '🖼️', 'video': '🎬', 'gallery': '📸'}
        return format_html('{} {}', icons.get(obj.media_type, ''), obj.get_media_type_display())
    media_type_badge.short_description = _('Type')

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:40px; border-radius:4px;" />', obj.image.url)
        return '-'
    image_preview.short_description = _('Preview')