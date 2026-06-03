from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.db.models import Sum, Count, Q
from .models import Cart, CartItem, Wishlist, WishlistShare


# ============================================================
# Inline Models
# ============================================================

class CartItemInline(admin.TabularInline):
    """آیتم‌های سبد خرید داخل Cart"""
    model = CartItem
    extra = 0
    fields = [
        'product', 'product_image_preview', 'quantity',
        'unit_price_display', 'total_price_display',
        'is_active', 'added_from_wishlist'
    ]
    readonly_fields = [
        'product_image_preview', 'unit_price_display',
        'total_price_display', 'added_from_wishlist'
    ]
    can_delete = True
    show_change_link = True

    def product_image_preview(self, obj):
        if obj.product.main_image:
            return format_html(
                '<img src="{}" style="max-height: 40px; border-radius: 4px;" />',
                obj.product.main_image.url
            )
        return '🖼️'
    product_image_preview.short_description = _('Image')

    def unit_price_display(self, obj):
        return format_html('<b>{:,}</b> Rials', int(obj.unit_price))
    unit_price_display.short_description = _('Unit Price')

    def total_price_display(self, obj):
        return format_html(
            '<span style="color: #e94560; font-weight: bold;">{:,}</span> Rials',
            int(obj.total_price)
        )
    total_price_display.short_description = _('Total')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')


class WishlistInline(admin.StackedInline):
    """Wishlist های کاربر داخل User admin (اگه بخوایم)"""
    model = Wishlist
    extra = 0
    fields = ['name', 'budget_limit', 'target_date', 'conversion_count', 'is_active']
    readonly_fields = ['conversion_count']
    show_change_link = True
    can_delete = False


# ============================================================
# Cart Admin
# ============================================================

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = [
        'id_short', 'user_info', 'cart_type_badge',
        'status_badge', 'items_summary',
        'price_summary', 'discount_badge',
        'is_converted', 'created_at_persian',
    ]
    list_filter = [
        'cart_type', 'status', 'created_at',
        'discount_percent', 'discount_set_by',
    ]
    search_fields = [
        'user__email', 'user__mobile', 'user__first_name',
        'user__last_name', 'name',
        'items__product__sku', 'items__product__name',
    ]
    readonly_fields = [
        'id', 'user', 'cart_type', 'created_at', 'updated_at',
        'converted_from', 'converted_at',
    ]
    autocomplete_fields = ['user', 'converted_from', 'discount_set_by']

    fieldsets = (
        (_('Cart Information'), {
            'fields': ('id', 'user', 'cart_type', 'status', 'name')
        }),
        (_('Pricing'), {
            'fields': ('discount_percent', 'discount_amount', 'discount_type',
                       'discount_set_by', 'discount_note', 'discount_approved_at')
        }),
        (_('Conversion'), {
            'fields': ('converted_from', 'converted_at'),
            'classes': ('collapse',)
        }),
        (_('Notes'), {
            'fields': ('notes',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at', 'expires_at'),
            'classes': ('collapse',)
        }),
    )

    inlines = [CartItemInline]
    list_per_page = 50
    date_hierarchy = 'created_at'

    # ==================== List Display Methods ====================

    @admin.display(description=_('ID'))
    def id_short(self, obj):
        return str(obj.id)[:8] + '...'

    @admin.display(description=_('User'), ordering='user__email')
    def user_info(self, obj):
        user = obj.user
        return format_html(
            '<div><b>{}</b></div>'
            '<small style="color: #666;">{}</small>',
            user.get_display_name(),
            user.email or user.mobile or ''
        )

    @admin.display(description=_('Type'))
    def cart_type_badge(self, obj):
        if obj.is_cart:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 4px 10px; '
                'border-radius: 20px; font-size: 12px;">🛒 Cart</span>'
            )
        return format_html(
            '<span style="background-color: #ffc107; color: #333; padding: 4px 10px; '
            'border-radius: 20px; font-size: 12px;">⭐ Wishlist</span>'
        )

    @admin.display(description=_('Status'))
    def status_badge(self, obj):
        colors = {
            'active': ('#28a745', '✅'),
            'checkout': ('#17a2b8', '💳'),
            'ordered': ('#6f42c1', '📦'),
            'abandoned': ('#6c757d', '🗑️'),
            'converted': ('#fd7e14', '🔄'),
        }
        color, icon = colors.get(obj.status, ('#6c757d', '❓'))
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 4px; font-size: 11px;">{} {}</span>',
            color, icon, obj.get_status_display()
        )

    @admin.display(description=_('Items'))
    def items_summary(self, obj):
        total = obj.total_items
        qty = obj.total_quantity
        return format_html(
            '<b>{}</b> items<br/><small>{}</b> units</small>',
            total, qty
        )

    @admin.display(description=_('Price'))
    def price_summary(self, obj):
        subtotal = int(obj.subtotal)
        grand = int(obj.grand_total)

        if obj.discount_percent > 0 or obj.discount_amount > 0:
            return format_html(
                '<span style="text-decoration: line-through; color: #999;">{:,}</span><br/>'
                '<span style="color: #e94560; font-weight: bold;">{:,}</span>',
                subtotal, grand
            )
        return format_html('<b>{:,}</b>', subtotal)

    @admin.display(description=_('Discount'))
    def discount_badge(self, obj):
        if obj.discount_percent > 0:
            return format_html(
                '<span style="background-color: #e94560; color: white; padding: 2px 8px; '
                'border-radius: 12px; font-size: 11px;">-{}%</span>',
                int(obj.discount_percent)
            )
        elif obj.discount_amount > 0:
            return format_html(
                '<span style="background-color: #e94560; color: white; padding: 2px 8px; '
                'border-radius: 12px; font-size: 11px;">-{:,}</span>',
                int(obj.discount_amount)
            )
        return '-'

    @admin.display(description=_('Converted'))
    def is_converted(self, obj):
        if obj.converted_from:
            return format_html(
                '<a href="{}" title="Converted from wishlist">🔄</a>',
                f'/admin/basket/cart/{obj.converted_from.id}/change/'
            )
        if obj.status == 'converted':
            # این Wishlist به Cart تبدیل شده
            converted_to = Cart.objects.filter(converted_from=obj).first()
            if converted_to:
                return format_html(
                    '<a href="{}" title="View converted cart">➡️🛒</a>',
                    f'/admin/basket/cart/{converted_to.id}/change/'
                )
        return '-'

    @admin.display(description=_('Created'))
    def created_at_persian(self, obj):
        import jdatetime
        return jdatetime.datetime.fromgregorian(
            datetime=obj.created_at
        ).strftime('%Y/%m/%d %H:%M')

    # ==================== Actions ====================

    actions = [
        'mark_as_abandoned', 'apply_10_percent_discount',
        'apply_20_percent_discount', 'clear_discount',
        'export_cart_summary',
    ]

    @admin.action(description=_('Mark selected as abandoned'))
    def mark_as_abandoned(self, request, queryset):
        updated = queryset.filter(status='active').update(status='abandoned')
        self.message_user(request, _(f'{updated} cart(s) marked as abandoned.'), level='warning')

    @admin.action(description=_('Apply 10% discount'))
    def apply_10_percent_discount(self, request, queryset):
        count = 0
        for cart in queryset.filter(cart_type='wishlist', status='active'):
            cart.discount_percent = 10
            cart.discount_type = 'percent'
            cart.discount_set_by = request.user
            cart.discount_approved_at = __import__('django').utils.timezone.now()
            cart.save()
            count += 1
        self.message_user(request, _(f'10% discount applied to {count} wishlist(s).'))

    @admin.action(description=_('Apply 20% discount'))
    def apply_20_percent_discount(self, request, queryset):
        count = 0
        for cart in queryset.filter(cart_type='wishlist', status='active'):
            cart.discount_percent = 20
            cart.discount_type = 'percent'
            cart.discount_set_by = request.user
            cart.discount_approved_at = __import__('django').utils.timezone.now()
            cart.save()
            count += 1
        self.message_user(request, _(f'20% discount applied to {count} wishlist(s).'))

    @admin.action(description=_('Clear discount'))
    def clear_discount(self, request, queryset):
        updated = queryset.update(
            discount_percent=0,
            discount_amount=0,
            discount_set_by=None,
            discount_note='',
            discount_approved_at=None
        )
        self.message_user(request, _(f'Discount cleared from {updated} cart(s).'))

    @admin.action(description=_('Export cart summary'))
    def export_cart_summary(self, request, queryset):
        from django.http import HttpResponse
        import csv

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="carts_export.csv"'
        response.write('\ufeff'.encode('utf-8'))  # BOM for Excel

        writer = csv.writer(response)
        writer.writerow([
            'Cart ID', 'User', 'Type', 'Status', 'Total Items',
            'Total Quantity', 'Subtotal', 'Discount', 'Grand Total',
            'Created At'
        ])

        for cart in queryset:
            writer.writerow([
                str(cart.id),
                cart.user.get_display_name(),
                cart.cart_type,
                cart.status,
                cart.total_items,
                cart.total_quantity,
                int(cart.subtotal),
                int(cart.discount_total),
                int(cart.grand_total),
                cart.created_at.isoformat(),
            ])

        return response


# ============================================================
# CartItem Admin
# ============================================================

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = [
        'product_image', 'product_name', 'product_sku',
        'cart_link', 'quantity', 'unit_price_display',
        'total_price_display', 'is_active_badge',
        'added_from_wishlist', 'created_at_persian',
    ]
    list_filter = [
        'is_active', 'added_from_wishlist', 'created_at',
        'cart__cart_type', 'cart__status',
    ]
    search_fields = [
        'product__sku', 'product__name', 'product__model_number',
        'cart__user__email', 'cart__id',
    ]
    readonly_fields = [
        'id', 'cart', 'product', 'unit_price',
        'added_from_wishlist', 'created_at', 'updated_at',
    ]
    autocomplete_fields = ['cart', 'product']

    fieldsets = (
        (_('Relations'), {'fields': ('cart', 'product')}),
        (_('Details'), {'fields': ('quantity', 'unit_price', 'is_active', 'added_from_wishlist')}),
        (_('Notes'), {'fields': ('notes',)}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )

    list_per_page = 100

    @admin.display(description=_('Image'))
    def product_image(self, obj):
        if obj.product.main_image:
            return format_html(
                '<img src="{}" style="max-height: 40px; border-radius: 4px;" />',
                obj.product.main_image.url
            )
        return '🖼️'

    @admin.display(description=_('Product'), ordering='product__name')
    def product_name(self, obj):
        return obj.product.name[:60]

    @admin.display(description=_('SKU'))
    def product_sku(self, obj):
        return obj.product.sku

    @admin.display(description=_('Cart'))
    def cart_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            f'/admin/basket/cart/{obj.cart.id}/change/',
            str(obj.cart.id)[:8]
        )

    @admin.display(description=_('Unit Price'))
    def unit_price_display(self, obj):
        return '{:,}'.format(int(obj.unit_price))

    @admin.display(description=_('Total'))
    def total_price_display(self, obj):
        return format_html(
            '<span style="color: #e94560; font-weight: bold;">{:,}</span>',
            int(obj.total_price)
        )

    @admin.display(description=_('Active'))
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html('✅')
        return format_html('❌')

    @admin.display(description=_('Created'))
    def created_at_persian(self, obj):
        import jdatetime
        return jdatetime.datetime.fromgregorian(
            datetime=obj.created_at
        ).strftime('%Y/%m/%d %H:%M')

    actions = ['mark_inactive']

    @admin.action(description=_('Mark selected as inactive'))
    def mark_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, _(f'{updated} item(s) marked as inactive.'))


# ============================================================
# Wishlist Admin
# ============================================================

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'user_info', 'items_count',
        'budget_info', 'has_discount_badge',
        'can_convert_badge', 'conversion_count',
        'is_active_badge', 'created_at_persian',
    ]
    list_filter = [
        'is_active', 'can_convert', 'created_at',
        'converted_at',
    ]
    search_fields = [
        'name', 'description',
        'user__email', 'user__mobile', 'user__first_name',
    ]
    readonly_fields = [
        'id', 'user', 'conversion_count', 'converted_at',
        'created_at', 'updated_at',
    ]
    autocomplete_fields = ['user']

    fieldsets = (
        (_('Wishlist Info'), {
            'fields': ('user', 'name', 'description')
        }),
        (_('Budget'), {
            'fields': ('budget_limit',)
        }),
        (_('Settings'), {
            'fields': ('is_active', 'is_public', 'can_convert')
        }),
        (_('Conversion Stats'), {
            'fields': ('conversion_count', 'converted_at')
        }),
        (_('Dates'), {
            'fields': ('target_date', 'created_at', 'updated_at')
        }),
    )

    list_per_page = 50

    @admin.display(description=_('User'), ordering='user__email')
    def user_info(self, obj):
        return format_html(
            '<b>{}</b><br/><small>{}</small>',
            obj.user.get_display_name(),
            obj.user.email or obj.user.mobile or ''
        )

    @admin.display(description=_('Items'))
    def items_count(self, obj):
        if hasattr(obj, 'cart'):
            return obj.cart.total_items
        return 0

    @admin.display(description=_('Budget'))
    def budget_info(self, obj):
        if obj.budget_limit:
            total = obj.estimated_total if hasattr(obj, 'cart') else 0
            color = '#dc3545' if total > obj.budget_limit else '#28a745'
            return format_html(
                '<span>Budget: <b>{:,}</b></span><br/>'
                '<span style="color: {};">Current: <b>{:,}</b></span>',
                int(obj.budget_limit), color, int(total)
            )
        return format_html('<span style="color: #6c757d;">No budget</span>')

    @admin.display(description=_('Discount'))
    def has_discount_badge(self, obj):
        if hasattr(obj, 'cart') and obj.cart and (obj.cart.discount_percent > 0 or obj.cart.discount_amount > 0):
            if obj.cart.discount_percent > 0:
                return format_html(
                    '<span style="background-color: #e94560; color: white; padding: 2px 8px; '
                    'border-radius: 12px;">-{}%</span>',
                    int(obj.cart.discount_percent)
                )
            return format_html('💰 Yes')
        return '❌'

    @admin.display(description=_('Convert'))
    def can_convert_badge(self, obj):
        if obj.can_convert:
            return format_html('✅ Allowed')
        return format_html('🚫 Blocked')

    @admin.display(description=_('Conv.'))
    def conversion_count(self, obj):
        return obj.conversion_count

    @admin.display(description=_('Active'))
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html('✅')
        return format_html('❌')

    @admin.display(description=_('Created'))
    def created_at_persian(self, obj):
        import jdatetime
        return jdatetime.datetime.fromgregorian(
            datetime=obj.created_at
        ).strftime('%Y/%m/%d %H:%M')

    actions = [
        'block_conversion', 'allow_conversion',
        'activate_wishlists', 'deactivate_wishlists',
    ]

    @admin.action(description=_('Block conversion for selected'))
    def block_conversion(self, request, queryset):
        updated = queryset.update(can_convert=False)
        self.message_user(request, _(f'Conversion blocked for {updated} wishlist(s).'), level='warning')

    @admin.action(description=_('Allow conversion for selected'))
    def allow_conversion(self, request, queryset):
        updated = queryset.update(can_convert=True)
        self.message_user(request, _(f'Conversion allowed for {updated} wishlist(s).'))

    @admin.action(description=_('Activate selected wishlists'))
    def activate_wishlists(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, _(f'{updated} wishlist(s) activated.'))

    @admin.action(description=_('Deactivate selected wishlists'))
    def deactivate_wishlists(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, _(f'{updated} wishlist(s) deactivated.'), level='warning')


# ============================================================
# WishlistShare Admin (Future)
# ============================================================

@admin.register(WishlistShare)
class WishlistShareAdmin(admin.ModelAdmin):
    list_display = [
        'wishlist_name', 'shared_with_user', 'shared_by_user',
        'can_edit_badge', 'created_at',
    ]
    list_filter = ['can_edit', 'created_at']
    search_fields = [
        'wishlist__name', 'shared_with__email',
        'shared_by__email',
    ]
    readonly_fields = ['created_at']
    autocomplete_fields = ['wishlist', 'shared_with', 'shared_by']

    @admin.display(description=_('Wishlist'))
    def wishlist_name(self, obj):
        return obj.wishlist.name

    @admin.display(description=_('Shared With'))
    def shared_with_user(self, obj):
        return obj.shared_with.get_display_name()

    @admin.display(description=_('Shared By'))
    def shared_by_user(self, obj):
        if obj.shared_by:
            return obj.shared_by.get_display_name()
        return '-'

    @admin.display(description=_('Can Edit'))
    def can_edit_badge(self, obj):
        return '✏️' if obj.can_edit else '👁️'
