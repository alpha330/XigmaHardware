from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.logistics.models import UserAddress
from apps.logistics.services.address_service import AddressService


class UserAddressSerializer(serializers.ModelSerializer):
    """سریالایزر آدرس کاربر"""
    full_address = serializers.CharField(read_only=True)
    gps_url = serializers.CharField(read_only=True)
    address_type_display = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = UserAddress
        fields = [
            'id', 'user', 'address_type', 'address_type_display',
            'title', 'recipient_name', 'recipient_mobile',
            'country', 'province', 'city', 'district', 'postal_code',
            'address_line', 'plaque', 'unit', 'floor',
            'latitude', 'longitude', 'full_address', 'gps_url',
            'google_place_id', 'google_formatted_address',
            'is_default', 'is_active', 'is_verified', 'is_owner',
            'delivery_instructions',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def get_address_type_display(self, obj):
        icons = {'home': '🏠', 'office': '🏢', 'warehouse': '🏭', 'other': '📍'}
        return {
            'code': obj.address_type,
            'label': obj.get_address_type_display(),
            'icon': icons.get(obj.address_type, '📍'),
        }

    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.user == request.user
        return False


class UserAddressCreateSerializer(serializers.ModelSerializer):
    """سریالایزر ایجاد آدرس"""

    class Meta:
        model = UserAddress
        fields = [
            'address_type', 'title', 'recipient_name', 'recipient_mobile',
            'country', 'province', 'city', 'district', 'postal_code',
            'address_line', 'plaque', 'unit', 'floor',
            'latitude', 'longitude',
            'google_place_id', 'google_formatted_address',
            'is_default', 'delivery_instructions',
        ]

    def validate_recipient_mobile(self, value):
        """اعتبارسنجی موبایل"""
        if not value or len(value) != 11:
            raise serializers.ValidationError(_('Valid mobile number is required.'))
        if not value.startswith('09'):
            raise serializers.ValidationError(_('Mobile must start with 09.'))
        return value

    def validate(self, data):
        """اعتبارسنجی کلی"""
        # اعتبارسنجی GPS
        lat = data.get('latitude')
        lng = data.get('longitude')

        if not lat or not lng:
            raise serializers.ValidationError(_('GPS coordinates are required.'))

        if not AddressService.validate_gps(float(lat), float(lng)):
            raise serializers.ValidationError(_('Invalid GPS coordinates. Must be in Iran.'))

        # حداکثر ۱۰ آدرس
        user = self.context['request'].user
        if AddressService.get_address_count(user) >= 10:
            raise serializers.ValidationError(_('Maximum 10 addresses allowed.'))

        return data

    def validate_title(self, value):
        """اعتبارسنجی عنوان"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError(_('Title must be at least 2 characters.'))
        return value.strip()