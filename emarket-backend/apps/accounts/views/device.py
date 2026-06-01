import logging
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.accounts.models import UserDevice
from apps.accounts.serializers.device import (
    DeviceSerializer,
    DeviceTrustSerializer,
)
from apps.accounts.permissions import (
    IsDeviceOwner,
    IsAdminOrStaff,
)

logger = logging.getLogger(__name__)


class DeviceViewSet(viewsets.GenericViewSet):
    """
    ViewSet مدیریت دستگاه‌های کاربر
    
    Actions:
    - my_devices: لیست دستگاه‌های کاربر جاری
    - trust_device: اعتماد به دستگاه
    - revoke_device: لغو اعتماد/غیرفعال کردن دستگاه
    - list: لیست همه دستگاه‌ها (فقط ادمین)
    - retrieve: جزئیات دستگاه (فقط ادمین)
    """
    
    queryset = UserDevice.objects.all()
    serializer_class = DeviceSerializer
    
    def get_permissions(self):
        if self.action in ['my_devices', 'trust_device', 'revoke_device']:
            permission_classes = [IsAuthenticated, IsDeviceOwner]
        elif self.action in ['list', 'retrieve']:
            permission_classes = [IsAdminOrStaff]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        فیلتر دستگاه‌ها بر اساس کاربر
        """
        if self.action == 'my_devices':
            return UserDevice.objects.filter(user=self.request.user)
        return UserDevice.objects.all()
    
    @action(detail=False, methods=['get'])
    def my_devices(self, request):
        """
        لیست دستگاه‌های کاربر جاری
        """
        devices = self.get_queryset()
        
        # جدا کردن دستگاه جاری
        current_device = None
        if hasattr(request, 'device'):
            current_device = request.device
        
        serializer = self.get_serializer(devices, many=True)
        
        return Response({
            'devices': serializer.data,
            'current_device_id': str(current_device.id) if current_device else None,
            'total_devices': devices.count(),
            'active_devices': devices.filter(is_active=True).count(),
            'trusted_devices': devices.filter(is_trusted=True).count(),
        })
    
    @action(detail=True, methods=['post'])
    def trust_device(self, request, pk=None):
        """
        اعتماد به یک دستگاه
        """
        device = self.get_object()
        
        # بررسی مالکیت
        if device.user != request.user:
            return Response({
                'error': _('You can only trust your own devices.')
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            device.trust()
            
            logger.info(f"Device trusted: {device.id} for user {request.user.email or request.user.mobile}")
            
            return Response({
                'message': _('Device trusted successfully.'),
                'device': DeviceSerializer(device).data
            })
            
        except Exception as e:
            logger.error(f"Trust device failed: {str(e)}")
            return Response({
                'error': _('Failed to trust device.')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def revoke_device(self, request, pk=None):
        """
        لغو اعتماد یا غیرفعال کردن دستگاه
        """
        device = self.get_object()
        
        # بررسی مالکیت
        if device.user != request.user:
            return Response({
                'error': _('You can only revoke your own devices.')
            }, status=status.HTTP_403_FORBIDDEN)
        
        # نمی‌توان دستگاه جاری را غیرفعال کرد
        if hasattr(request, 'device') and request.device == device:
            return Response({
                'error': _('Cannot revoke current device.')
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # غیرفعال کردن و لغو اعتماد
            device.is_active = False
            device.revoke_trust()
            device.save()
            
            logger.info(f"Device revoked: {device.id} for user {request.user.email or request.user.mobile}")
            
            return Response({
                'message': _('Device revoked successfully.'),
                'device': DeviceSerializer(device).data
            })
            
        except Exception as e:
            logger.error(f"Revoke device failed: {str(e)}")
            return Response({
                'error': _('Failed to revoke device.')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def revoke_all_other(self, request):
        """
        لغو همه دستگاه‌های دیگر به جز دستگاه جاری
        """
        try:
            current_device = getattr(request, 'device', None)
            
            other_devices = UserDevice.objects.filter(
                user=request.user,
                is_active=True
            )
            
            if current_device:
                other_devices = other_devices.exclude(id=current_device.id)
            
            count = other_devices.count()
            other_devices.update(is_active=False, is_trusted=False)
            
            logger.info(
                f"Revoked {count} other devices for user "
                f"{request.user.email or request.user.mobile}"
            )
            
            return Response({
                'message': _(f'{count} other device(s) revoked.'),
                'revoked_count': count
            })
            
        except Exception as e:
            logger.error(f"Revoke all devices failed: {str(e)}")
            return Response({
                'error': _('Failed to revoke devices.')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)