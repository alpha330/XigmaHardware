import logging
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.logistics.models import Courier
from apps.logistics.serializers.courier import (
    CourierSerializer,
    CourierCreateSerializer,
    CourierLocationSerializer,
)
from apps.logistics.permissions import CanManageLogistics, IsCourierOwner
from apps.logistics.services.courier_service import CourierService

logger = logging.getLogger(__name__)


class CourierViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     viewsets.GenericViewSet):
    """
    ViewSet مدیریت پیک‌ها

    Actions:
    - list: لیست پیک‌های فعال
    - create: ایجاد پیک جدید (ادمین)
    - retrieve: جزئیات پیک
    - update: ویرایش (ادمین)
    - toggle_available: تغییر وضعیت آماده‌به‌کار
    - update_location: بروزرسانی موقعیت
    - my_shipments: محموله‌های من (برای پیک)
    - nearby: پیک‌های نزدیک
    """
    queryset = Courier.objects.filter(is_active=True)
    serializer_class = CourierSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return CourierCreateSerializer
        elif self.action == 'update_location':
            return CourierLocationSerializer
        return CourierSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'nearby']:
            return [IsAuthenticated()]
        elif self.action in ['update_location', 'my_shipments']:
            return [IsAuthenticated(), IsCourierOwner()]
        return [IsAuthenticated(), CanManageLogistics()]

    def get_queryset(self):
        queryset = Courier.objects.filter(is_active=True)

        # فیلتر بر اساس نوع
        courier_type = self.request.query_params.get('type')
        if courier_type:
            queryset = queryset.filter(courier_type=courier_type)

        # فقط پیک‌های آماده
        available = self.request.query_params.get('available')
        if available:
            queryset = queryset.filter(is_available=True)

        # فقط پیک‌های داخلی
        internal = self.request.query_params.get('internal')
        if internal:
            queryset = queryset.filter(courier_type='internal')

        return queryset

    @action(detail=True, methods=['post'])
    def toggle_available(self, request, pk=None):
        """تغییر وضعیت آماده‌به‌کار"""
        courier = self.get_object()

        # فقط خود پیک یا ادمین
        if courier.user != request.user and not request.user.is_superuser:
            return Response(
                {'error': _('Permission denied.')},
                status=status.HTTP_403_FORBIDDEN
            )

        courier.is_available = not courier.is_available
        courier.save(update_fields=['is_available'])

        logger.info(
            f"Courier {courier.name} availability: {courier.is_available}"
        )

        return Response({
            'is_available': courier.is_available,
            'message': _('Available' if courier.is_available else 'Unavailable'),
        })

    @action(detail=True, methods=['post'])
    def update_location(self, request, pk=None):
        """بروزرسانی موقعیت پیک"""
        courier = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from django.utils import timezone

        courier.current_latitude = serializer.validated_data['latitude']
        courier.current_longitude = serializer.validated_data['longitude']
        courier.location_updated_at = timezone.now()
        courier.save(update_fields=[
            'current_latitude', 'current_longitude', 'location_updated_at'
        ])

        return Response({
            'message': _('Location updated.'),
            'latitude': float(courier.current_latitude),
            'longitude': float(courier.current_longitude),
            'updated_at': courier.location_updated_at.isoformat(),
        })

    @action(detail=True, methods=['get'])
    def my_shipments(self, request, pk=None):
        """محموله‌های این پیک"""
        courier = self.get_object()

        from apps.logistics.services.shipping_service import ShippingService
        from apps.logistics.serializers.shipment import ShipmentSerializer

        shipments = ShippingService.get_active_shipments_for_courier(courier)

        page = self.paginate_queryset(shipments)
        if page is not None:
            serializer = ShipmentSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = ShipmentSerializer(shipments, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """پیدا کردن پیک‌های نزدیک"""
        lat = request.query_params.get('latitude')
        lng = request.query_params.get('longitude')

        if not lat or not lng:
            return Response(
                {'error': _('Latitude and longitude required.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        from apps.logistics.services.shipping_service import ShippingService

        nearby = ShippingService.find_nearest_available_couriers(
            float(lat), float(lng), limit=10
        )

        result = []
        for item in nearby:
            courier = item['courier']
            result.append({
                'id': str(courier.id),
                'name': courier.name,
                'phone': courier.phone,
                'vehicle_type': courier.vehicle_type,
                'distance_km': item['distance_km'],
                'rating': float(courier.rating),
                'current_lat': float(courier.current_latitude) if courier.current_latitude else None,
                'current_lng': float(courier.current_longitude) if courier.current_longitude else None,
            })

        return Response(result)

    @action(detail=False, methods=['get'])
    def external_estimate(self, request):
        """استعلام قیمت از پیک‌های خارجی"""
        origin_lat = request.query_params.get('origin_lat')
        origin_lng = request.query_params.get('origin_lng')
        dest_lat = request.query_params.get('dest_lat')
        dest_lng = request.query_params.get('dest_lng')

        if not all([origin_lat, origin_lng, dest_lat, dest_lng]):
            return Response(
                {'error': _('All coordinates required.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        estimates = CourierService.get_price_estimates(
            origin_lat=float(origin_lat),
            origin_lng=float(origin_lng),
            dest_lat=float(dest_lat),
            dest_lng=float(dest_lng),
        )

        return Response(estimates)