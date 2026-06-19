from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.db.models import Count, Q
from .models import UserAddress, Courier, Shipment, ShipmentTracking
from .enums import AddressType, CourierType, ShipmentStatus, VehicleType


# ============================================================
# Inline Models
# ============================================================

class ShipmentTrackingInline(admin.TabularInline):
    """رویدادهای رهگیری داخل Shipment"""
    model = ShipmentTracking
    extra = 0
    fields = ['status_badge', 'description', 'location_link', 'created_by', 'created_at_jalali']
    readonly_fields = ['status_badge', 'location_link', 'created_by', 'created_at_jalali']
    can_delete = False
    max_num = 0
    ordering = ['-created_at']

    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'assigned': '#17a2b8',
            'picked_up': '#6f42c1',
            'in_transit': '#0d6efd',
            'delivered': '#28a745',
            'returned': '#dc3545',
            'cancelled': '#6c757d',
        }
        return format_html(
            '<span style="background:{}; color:white; padding:2px 8px; '
            'border-radius:4px; font-size:11px;">{}</span>',
            colors.get(obj.status, '#6c757d'), obj.get_status_display()
        )
    status_badge.short_description = _('Status')

    def location_link(self, obj):
        if obj.location_latitude and obj.location_longitude:
            return format_html(
                '<a href="https://maps.google.com/?q={},{}" target="_blank">📍 View</a>',
                obj.location_latitude, obj.location_longitude
            )
        return '-'
    location_link.short_description = _('Location')

    def created_at_jalali(self, obj):
        try:
            import jdatetime
            return jdatetime.datetime.fromgregorian(
                datetime=obj.created_at
            ).strftime('%Y/%m/%d %H:%M')
        except ImportError:
            return obj.created_at.strftime('%Y-%m-%d %H:%M')
    created_at_jalali.short_description = _('Date')


class ShipmentInline(admin.TabularInline):
    """محموله‌های یک پیک"""
    model = Shipment
    fk_name = 'courier'
    extra = 0
    fields = ['id_short', 'customer_info', 'status_badge', 'destination_city', 'created_at_jalali']
    readonly_fields = ['id_short', 'customer_info', 'status_badge', 'destination_city', 'created_at_jalali']
    can_delete = False
    max_num = 0
    ordering = ['-created_at']
    show_change_link = True

    def id_short(self, obj):
        return str(obj.id)[:8]
    id_short.short_description = _('ID')

    def customer_info(self, obj):
        if obj.user:
            return obj.user.get_display_name()
        return '-'
    customer_info.short_description = _('Customer')

    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107', 'assigned': '#17a2b8',
            'picked_up': '#6f42c1', 'in_transit': '#0d6efd',
            'delivered': '#28a745', 'returned': '#dc3545', 'cancelled': '#6c757d',
        }
        return format_html(
            '<span style="background:{}; color:white; padding:2px 6px; '
            'border-radius:4px; font-size:10px;">{}</span>',
            colors.get(obj.status, '#6c757d'), obj.get_status_display()
        )
    status_badge.short_description = _('Status')

    def destination_city(self, obj):
        if obj.destination_address:
            return obj.destination_address.city
        return '-'
    destination_city.short_description = _('City')

    def created_at_jalali(self, obj):
        try:
            import jdatetime
            return jdatetime.datetime.fromgregorian(
                datetime=obj.created_at
            ).strftime('%Y/%m/%d')
        except ImportError:
            return obj.created_at.strftime('%Y-%m-%d')
    created_at_jalali.short_description = _('Date')


# ============================================================
# User Address Admin
# ============================================================

@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'user_info', 'address_type_badge',
        'recipient_info', 'city_display', 'gps_link',
        'is_default_badge', 'is_active',
        'created_at_jalali',
    ]
    list_filter = ['address_type', 'is_active', 'is_default', 'city', 'province']
    search_fields = [
        'title', 'recipient_name', 'recipient_mobile',
        'address_line', 'city', 'province',
        'user__email', 'user__mobile',
    ]
    readonly_fields = ['id', 'user', 'created_at', 'updated_at']
    autocomplete_fields = ['user']

    fieldsets = (
        (_('Owner'), {'fields': ('user',)}),
        (_('Address Info'), {
            'fields': ('address_type', 'title', 'recipient_name', 'recipient_mobile')
        }),
        (_('Location'), {
            'fields': (
                'country', 'province', 'city', 'district', 'postal_code',
                'address_line', 'plaque', 'unit', 'floor'
            )
        }),
        (_('GPS'), {
            'fields': ('latitude', 'longitude', 'google_place_id', 'google_formatted_address')
        }),
        (_('Settings'), {
            'fields': ('is_default', 'is_active', 'is_verified', 'delivery_instructions')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    list_per_page = 50

    # ==================== List Display ====================

    @admin.display(description=_('User'), ordering='user__email')
    def user_info(self, obj):
        return format_html(
            '<b>{}</b><br/><small>{}</small>',
            obj.user.get_display_name(),
            obj.user.email or obj.user.mobile or ''
        )

    @admin.display(description=_('Type'))
    def address_type_badge(self, obj):
        icons = {'home': '🏠', 'office': '🏢', 'warehouse': '🏭', 'other': '📍'}
        return format_html('{} {}', icons.get(obj.address_type, '📍'), obj.get_address_type_display())

    @admin.display(description=_('Recipient'))
    def recipient_info(self, obj):
        return format_html(
            '<b>{}</b><br/><small style="direction: ltr;">{}</small>',
            obj.recipient_name, obj.recipient_mobile
        )

    @admin.display(description=_('City'))
    def city_display(self, obj):
        return f"{obj.city}, {obj.province}"

    @admin.display(description=_('GPS'))
    def gps_link(self, obj):
        if obj.latitude is not None and obj.longitude is not None:
            return format_html(
                '<a href="https://maps.google.com/?q={},{}" target="_blank">📍 {:.4f}, {:.4f}</a>',
                float(obj.latitude), float(obj.longitude)
            )
        return '❌ No GPS'

    @admin.display(description=_('Default'))
    def is_default_badge(self, obj):
        return '⭐' if obj.is_default else '-'

    @admin.display(description=_('Created'))
    def created_at_jalali(self, obj):
        try:
            import jdatetime
            return jdatetime.datetime.fromgregorian(
                datetime=obj.created_at
            ).strftime('%Y/%m/%d')
        except ImportError:
            return obj.created_at.strftime('%Y-%m-%d')

    # ==================== Actions ====================

    actions = ['set_as_default', 'activate_addresses', 'deactivate_addresses']

    @admin.action(description=_('Set selected as default'))
    def set_as_default(self, request, queryset):
        for address in queryset:
            address.set_as_default()
        self.message_user(request, _(f'{queryset.count()} address(es) set as default.'))

    @admin.action(description=_('Activate selected'))
    def activate_addresses(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, _('Addresses activated.'))

    @admin.action(description=_('Deactivate selected'))
    def deactivate_addresses(self, request, queryset):
        queryset.update(is_active=False, is_default=False)
        self.message_user(request, _('Addresses deactivated.'), level='warning')


# ============================================================
# Courier Admin
# ============================================================

@admin.register(Courier)
class CourierAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'courier_type_badge', 'vehicle_type_badge',
        'contact_info', 'availability_badge', 'rating_stars',
        'success_rate_display', 'location_updated',
        'is_active',
    ]
    list_filter = ['courier_type', 'vehicle_type', 'is_active', 'is_available']
    search_fields = ['name', 'phone', 'email', 'vehicle_plate', 'national_code']
    readonly_fields = ['total_deliveries', 'successful_deliveries', 'rating', 'created_at', 'updated_at']
    autocomplete_fields = ['user']

    fieldsets = (
        (_('Basic Info'), {
            'fields': ('courier_type', 'name', 'phone', 'email')
        }),
        (_('Internal Courier'), {
            'fields': ('user', 'national_code'),
            'classes': ('collapse',)
        }),
        (_('Vehicle'), {
            'fields': ('vehicle_type', 'vehicle_plate')
        }),
        (_('API Credentials'), {
            'fields': ('api_key', 'api_secret', 'webhook_url', 'extra_config'),
            'classes': ('collapse',)
        }),
        (_('Status'), {
            'fields': ('is_active', 'is_available')
        }),
        (_('Current Location'), {
            'fields': ('current_latitude', 'current_longitude', 'location_updated_at')
        }),
        (_('Stats'), {
            'fields': ('rating', 'total_deliveries', 'successful_deliveries')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    inlines = [ShipmentInline]
    list_per_page = 30

    # ==================== List Display ====================

    @admin.display(description=_('Type'))
    def courier_type_badge(self, obj):
        colors = {
            'internal': '#28a745', 'alopeyk': '#17a2b8',
            'snappbox': '#6f42c1', 'post': '#ffc107', 'tipax': '#fd7e14',
        }
        return format_html(
            '<span style="background:{}; color:white; padding:3px 8px; '
            'border-radius:12px; font-size:11px;">{}</span>',
            colors.get(obj.courier_type, '#6c757d'), obj.get_courier_type_display()
        )

    @admin.display(description=_('Vehicle'))
    def vehicle_type_badge(self, obj):
        icons = {
            'motorcycle': '🏍️', 'car': '🚗', 'pickup': '🛻',
            'van': '🚐', 'truck': '🚛',
        }
        return format_html('{} {}', icons.get(obj.vehicle_type, '🛵'), obj.get_vehicle_type_display())

    @admin.display(description=_('Contact'))
    def contact_info(self, obj):
        parts = []
        if obj.phone:
            parts.append(f'📱 {obj.phone}')
        if obj.email:
            parts.append(f'📧 {obj.email}')
        return format_html('<br/>'.join(parts)) if parts else '-'

    @admin.display(description=_('Available'))
    def availability_badge(self, obj):
        if not obj.is_active:
            return format_html('<span style="color:#dc3545;">❌ Inactive</span>')
        if obj.is_available:
            return format_html('<span style="color:#28a745;">✅ Available</span>')
        return format_html('<span style="color:#ffc107;">⏳ Busy</span>')

    @admin.display(description=_('Rating'))
    def rating_stars(self, obj):
        rating = obj.rating if obj.rating is not None else 0
        stars = '⭐' * int(rating)
        return format_html('{} <small>({})</small>', stars, float(rating))

    @admin.display(description=_('Success'))
    def success_rate_display(self, obj):
        rate = obj.success_rate if obj.success_rate is not None else 0
        color = '#28a745' if rate > 90 else '#ffc107' if rate > 70 else '#dc3545'
        return format_html(
            '<span style="color:{}; font-weight:bold;">{}%</span>',
            color, rate
        )

    @admin.display(description=_('GPS Updated'))
    def location_updated(self, obj):
        if obj.location_updated_at:
            try:
                import jdatetime
                return jdatetime.datetime.fromgregorian(
                    datetime=obj.location_updated_at
                ).strftime('%H:%M')
            except ImportError:
                return obj.location_updated_at.strftime('%H:%M')
        return '-'

    # ==================== Actions ====================

    actions = ['toggle_available', 'toggle_active']

    @admin.action(description=_('Toggle availability'))
    def toggle_available(self, request, queryset):
        for courier in queryset:
            courier.is_available = not courier.is_available
            courier.save()
        self.message_user(request, _('Availability toggled.'))

    @admin.action(description=_('Toggle active status'))
    def toggle_active(self, request, queryset):
        for courier in queryset:
            courier.is_active = not courier.is_active
            courier.save()
        self.message_user(request, _('Active status toggled.'))


# ============================================================
# Shipment Admin
# ============================================================

@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = [
        'id_short', 'customer_info', 'status_badge',
        'origin_dest_display', 'courier_info',
        'cost_display', 'distance_display',
        'created_at_jalali',
    ]
    list_filter = ['status', 'courier', 'created_at', 'courier__courier_type']
    search_fields = [
        'id', 'user__email', 'user__mobile',
        'destination_address__recipient_name', 'destination_address__city',
        'courier__name', 'courier_tracking_code',
    ]
    readonly_fields = [
        'id', 'user', 'origin_warehouse', 'destination_address',
        'created_at', 'updated_at', 'assigned_at', 'picked_up_at', 'delivered_at',
    ]
    autocomplete_fields = ['user', 'origin_warehouse', 'destination_address', 'courier', 'invoice']

    fieldsets = (
        (_('Shipment Info'), {'fields': ('id', 'user', 'invoice')}),
        (_('Addresses'), {
            'fields': (
                'origin_warehouse', 'origin_address',
                'origin_latitude', 'origin_longitude',
                'destination_address',
                'destination_latitude', 'destination_longitude',
            )
        }),
        (_('Courier'), {
            'fields': ('courier', 'courier_tracking_code')
        }),
        (_('Status'), {
            'fields': ('status',)
        }),
        (_('Pricing'), {
            'fields': ('shipping_cost', 'courier_cost', 'customer_cost')
        }),
        (_('Details'), {
            'fields': ('distance_km', 'estimated_duration', 'package_weight_kg', 'package_description')
        }),
        (_('Notes'), {
            'fields': ('notes', 'courier_notes')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at', 'assigned_at', 'picked_up_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )

    inlines = [ShipmentTrackingInline]
    list_per_page = 50
    date_hierarchy = 'created_at'

    # ==================== List Display ====================

    @admin.display(description=_('ID'))
    def id_short(self, obj):
        return str(obj.id)[:8]

    @admin.display(description=_('Customer'), ordering='user__email')
    def customer_info(self, obj):
        if obj.user:
            return format_html(
                '<b>{}</b>',
                obj.user.get_display_name()
            )
        return '-'

    @admin.display(description=_('Status'))
    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107', 'assigned': '#17a2b8',
            'picked_up': '#6f42c1', 'in_transit': '#0d6efd',
            'delivered': '#28a745', 'returned': '#dc3545', 'cancelled': '#6c757d',
        }
        return format_html(
            '<span style="background:{}; color:white; padding:4px 10px; '
            'border-radius:12px; font-size:11px;">{}</span>',
            colors.get(obj.status, '#6c757d'), obj.get_status_display()
        )

    @admin.display(description=_('Route'))
    def origin_dest_display(self, obj):
        origin = obj.origin_warehouse.code if obj.origin_warehouse else '📍'
        dest = obj.destination_address.city if obj.destination_address else '📍'
        return format_html('{} → {}', origin, dest)

    @admin.display(description=_('Courier'))
    def courier_info(self, obj):
        if obj.courier:
            return format_html(
                '<b>{}</b><br/><small>{}</small>',
                obj.courier.name,
                obj.courier.get_courier_type_display()
            )
        return format_html('<span style="color:#dc3545;">Not assigned</span>')

    @admin.display(description=_('Cost'))
    def cost_display(self, obj):
        cost = obj.customer_cost if obj.customer_cost is not None else 0
        return format_html(
            '<span style="color:#e94560;">{}</span>',
            f'{int(cost):,}'
        )

    @admin.display(description=_('Distance'))
    def distance_display(self, obj):
        if obj.distance_km is not None:
            return f'{float(obj.distance_km):.1f} km'
        return '-'

    @admin.display(description=_('Created'))
    def created_at_jalali(self, obj):
        try:
            import jdatetime
            return jdatetime.datetime.fromgregorian(
                datetime=obj.created_at
            ).strftime('%Y/%m/%d %H:%M')
        except ImportError:
            return obj.created_at.strftime('%Y-%m-%d %H:%M')

    # ==================== Actions ====================

    actions = [
        'mark_as_delivered', 'mark_as_cancelled',
        'assign_nearest_courier',
    ]

    @admin.action(description=_('Mark selected as DELIVERED'))
    def mark_as_delivered(self, request, queryset):
        count = 0
        for shipment in queryset.filter(status__in=['picked_up', 'in_transit', 'assigned']):
            shipment.mark_delivered()
            ShipmentTracking.objects.create(
                shipment=shipment,
                status='delivered',
                description='Marked as delivered by admin',
                created_by=request.user,
            )
            count += 1
        self.message_user(request, _(f'{count} shipment(s) marked as delivered.'))

    @admin.action(description=_('Mark selected as CANCELLED'))
    def mark_as_cancelled(self, request, queryset):
        count = 0
        for shipment in queryset.filter(status__in=['pending', 'assigned']):
            shipment.cancel()
            ShipmentTracking.objects.create(
                shipment=shipment,
                status='cancelled',
                description='Cancelled by admin',
                created_by=request.user,
            )
            count += 1
        self.message_user(request, _(f'{count} shipment(s) cancelled.'), level='warning')

    @admin.action(description=_('Assign nearest available courier'))
    def assign_nearest_courier(self, request, queryset):
        from apps.logistics.services.shipping_service import ShippingService

        count = 0
        for shipment in queryset.filter(status='pending'):
            if shipment.origin_latitude and shipment.origin_longitude:
                nearest = ShippingService.find_nearest_available_couriers(
                    float(shipment.origin_latitude),
                    float(shipment.origin_longitude),
                    limit=1
                )
                if nearest:
                    courier = nearest[0]['courier']
                    shipment.assign_courier(courier)
                    ShipmentTracking.objects.create(
                        shipment=shipment,
                        status='assigned',
                        description=f'Auto-assigned to {courier.name} ({nearest[0]["distance_km"]:.1f}km)',
                        created_by=request.user,
                    )
                    count += 1

        self.message_user(request, _(f'{count} shipment(s) assigned to nearest courier.'))


# ============================================================
# ShipmentTracking Admin
# ============================================================

@admin.register(ShipmentTracking)
class ShipmentTrackingAdmin(admin.ModelAdmin):
    list_display = [
        'shipment_link', 'status_badge', 'description_short',
        'location_link', 'created_by_name', 'created_at_jalali',
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['shipment__id', 'description']
    readonly_fields = ['id', 'shipment', 'status', 'created_at', 'created_by']
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False

    @admin.display(description=_('Shipment'))
    def shipment_link(self, obj):
        return format_html(
            '<a href="{}">#{}</a>',
            f'/admin/logistics/shipment/{obj.shipment.id}/change/',
            str(obj.shipment.id)[:8]
        )

    @admin.display(description=_('Status'))
    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107', 'assigned': '#17a2b8',
            'picked_up': '#6f42c1', 'in_transit': '#0d6efd',
            'delivered': '#28a745', 'returned': '#dc3545', 'cancelled': '#6c757d',
        }
        return format_html(
            '<span style="background:{}; color:white; padding:2px 8px; '
            'border-radius:4px; font-size:11px;">{}</span>',
            colors.get(obj.status, '#6c757d'), obj.get_status_display()
        )

    @admin.display(description=_('Description'))
    def description_short(self, obj):
        return obj.description[:80] if obj.description else '-'

    @admin.display(description=_('Location'))
    def location_link(self, obj):
        if obj.location_latitude and obj.location_longitude:
            return format_html(
                '<a href="https://maps.google.com/?q={},{}" target="_blank">📍 Map</a>',
                obj.location_latitude, obj.location_longitude
            )
        return '-'

    @admin.display(description=_('By'))
    def created_by_name(self, obj):
        return obj.created_by.get_display_name() if obj.created_by else 'System'

    @admin.display(description=_('Date'))
    def created_at_jalali(self, obj):
        try:
            import jdatetime
            return jdatetime.datetime.fromgregorian(
                datetime=obj.created_at
            ).strftime('%Y/%m/%d %H:%M')
        except ImportError:
            return obj.created_at.strftime('%Y-%m-%d %H:%M')
