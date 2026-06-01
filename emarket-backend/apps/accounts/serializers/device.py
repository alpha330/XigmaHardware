"""
Device Serializers
- نمایش دستگاه
- مدیریت دستگاه‌ها
"""

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from apps.accounts.models import UserDevice


class DeviceSerializer(serializers.ModelSerializer):
    """
    سریالایزر دستگاه
    """
    device_info = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    is_current_device = serializers.SerializerMethodField()
    
    class Meta:
        model = UserDevice
        fields = [
            'id', 'user',
            'device_name', 'device_type',
            'operating_system', 'browser', 'browser_version',
            'ip_address',
            'country', 'city', 'location',
            'device_info',
            'is_active', 'is_trusted', 'is_current_device',
            'last_used', 'first_seen', 'created_at',
        ]
        read_only_fields = [
            'id', 'user', 'device_name', 'device_type',
            'operating_system', 'browser', 'browser_version',
            'ip_address', 'country', 'city',
            'last_used', 'first_seen', 'created_at',
        ]
    
    def get_device_info(self, obj):
        """اطلاعات کامل دستگاه"""
        return {
            'name': obj.device_name,
            'type': obj.device_type,
            'os': obj.operating_system,
            'browser': f"{obj.browser} {obj.browser_version}".strip(),
        }
    
    def get_location(self, obj):
        """موقعیت جغرافیایی"""
        if obj.city and obj.country:
            return {
                'city': obj.city,
                'country': obj.country,
                'full': f"{obj.city}, {obj.country}"
            }
        return None
    
    def get_is_current_device(self, obj):
        """آیا دستگاه جاری است؟"""
        request = self.context.get('request')
        if request and hasattr(request, 'device'):
            return request.device.id == obj.id
        return False


class DeviceTrustSerializer(serializers.Serializer):
    """
    سریالایزر اعتماد به دستگاه
    """
    trust = serializers.BooleanField(
        required=True,
        error_messages={
            'required': _('Trust value is required.'),
        }
    )
    
    def validate_trust(self, value):
        """بررسی منطق اعتماد"""
        device = self.context.get('device')
        if device and device.is_trusted == value:
            action = 'trusted' if value else 'not trusted'
            raise serializers.ValidationError(
                _(f'Device is already {action}.')
            )
        return value