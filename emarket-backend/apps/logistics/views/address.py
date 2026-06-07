import logging
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.logistics.models import UserAddress
from apps.logistics.serializers.address import (
    UserAddressSerializer,
    UserAddressCreateSerializer,
)
from apps.logistics.services.address_service import AddressService
from apps.logistics.permissions import IsAddressOwner

logger = logging.getLogger(__name__)


class AddressViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    """
    ViewSet مدیریت آدرس‌های کاربر

    Actions:
    - list: لیست آدرس‌های کاربر
    - create: ایجاد آدرس جدید
    - retrieve: جزئیات آدرس
    - update/partial_update: ویرایش آدرس
    - destroy: حذف آدرس
    - set_default: تنظیم به عنوان پیش‌فرض
    - default: آدرس پیش‌فرض
    - validate_gps: اعتبارسنجی GPS
    """
    serializer_class = UserAddressSerializer
    permission_classes = [IsAuthenticated, IsAddressOwner]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserAddressCreateSerializer
        return UserAddressSerializer

    def get_queryset(self):
        """فقط آدرس‌های فعال کاربر جاری"""
        return UserAddress.objects.filter(
            user=self.request.user,
            is_active=True
        ).order_by('-is_default', '-created_at')

    def perform_create(self, serializer):
        """ایجاد آدرس"""
        address = AddressService.create_address(
            user=self.request.user,
            data=serializer.validated_data,
        )

        logger.info(
            f"Address created: {address.title} for "
            f"{self.request.user.email or self.request.user.mobile}"
        )

        return address

    def perform_update(self, serializer):
        """بروزرسانی آدرس"""
        address = AddressService.update_address(
            address=self.get_object(),
            data=serializer.validated_data,
        )
        return address

    def perform_destroy(self, instance):
        """حذف نرم آدرس"""
        # چک کن آدرس در محموله فعال استفاده نشده باشه
        from apps.logistics.models import Shipment
        from apps.logistics.enums import ShipmentStatus

        active_shipment = Shipment.objects.filter(
            destination_address=instance,
            status__in=[
                ShipmentStatus.PENDING,
                ShipmentStatus.ASSIGNED,
                ShipmentStatus.PICKED_UP,
                ShipmentStatus.IN_TRANSIT,
            ]
        ).exists()

        if active_shipment:
            return Response(
                {'error': _('Cannot delete address with active shipment.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        AddressService.delete_address(instance)

        logger.info(f"Address deleted: {instance.id}")

    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """تنظیم به عنوان آدرس پیش‌فرض"""
        address = self.get_object()
        AddressService.set_as_default(address)

        return Response({
            'message': _('Set as default address.'),
            'address': UserAddressSerializer(address, context={'request': request}).data,
        })

    @action(detail=False, methods=['get'])
    def default(self, request):
        """دریافت آدرس پیش‌فرض"""
        address = AddressService.get_default_address(request.user)

        if address:
            return Response(
                UserAddressSerializer(address, context={'request': request}).data
            )

        return Response({
            'has_default': False,
            'message': _('No default address set.'),
        })

    @action(detail=False, methods=['post'])
    def validate_gps(self, request):
        """اعتبارسنجی مختصات GPS"""
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')

        if not latitude or not longitude:
            return Response(
                {'error': _('Latitude and longitude are required.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        is_valid = AddressService.validate_gps(
            float(latitude), float(longitude)
        )

        return Response({
            'valid': is_valid,
            'latitude': float(latitude),
            'longitude': float(longitude),
            'google_maps_url': f"https://www.google.com/maps?q={latitude},{longitude}" if is_valid else None,
        })

    @action(detail=False, methods=['get'])
    def count(self, request):
        """تعداد آدرس‌های کاربر"""
        count = AddressService.get_address_count(request.user)
        return Response({
            'count': count,
            'max_allowed': 10,
        })