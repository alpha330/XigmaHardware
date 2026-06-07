import logging
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.logistics.models import Shipment, ShipmentTracking, Courier
from apps.logistics.serializers.shipment import (
    ShipmentSerializer,
    ShipmentCreateSerializer,
    ShipmentTrackingSerializer,
    ShipmentStatusUpdateSerializer,
    ShipmentAssignSerializer,
    ShipmentCostEstimateSerializer,
)
from apps.logistics.services.shipping_service import ShippingService
from apps.logistics.services.courier_service import CourierService
from apps.logistics.permissions import CanManageLogistics

logger = logging.getLogger(__name__)


class ShipmentViewSet(mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.CreateModelMixin,
                      viewsets.GenericViewSet):
    """
    ViewSet مدیریت ارسال‌ها

    Actions:
    - list: لیست محموله‌ها
    - create: ایجاد محموله جدید
    - retrieve: جزئیات محموله
    - assign_courier: تخصیص پیک
    - update_status: بروزرسانی وضعیت
    - tracking: رهگیری
    - cost_estimate: استعلام هزینه
    - my_shipments: محموله‌های من
    - cancel: لغو محموله
    """
    queryset = Shipment.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return ShipmentCreateSerializer
        elif self.action == 'update_status':
            return ShipmentStatusUpdateSerializer
        elif self.action == 'assign_courier':
            return ShipmentAssignSerializer
        elif self.action == 'cost_estimate':
            return ShipmentCostEstimateSerializer
        return ShipmentSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'tracking', 'my_shipments']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), CanManageLogistics()]

    def get_queryset(self):
        qs = Shipment.objects.select_related(
            'courier', 'user', 'destination_address', 'origin_warehouse',
        ).prefetch_related('tracking_events')

        user = self.request.user

        # کاربران عادی فقط محموله‌های خودشون
        if not user.is_superuser and user.role not in ['super_admin', 'stock_keeper', 'courier']:
            qs = qs.filter(user=user)

        # پیک فقط محموله‌های خودش
        if user.role == 'courier':
            try:
                courier = Courier.objects.get(user=user)
                qs = qs.filter(courier=courier)
            except Courier.DoesNotExist:
                qs = qs.none()

        # فیلتر وضعیت
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)

        return qs.order_by('-created_at')

    def perform_create(self, serializer):
        """ایجاد محموله"""
        shipment = ShippingService.create_shipment(
            user=self.request.user,
            invoice=serializer.validated_data.get('invoice'),
            origin_warehouse=serializer.validated_data.get('origin_warehouse'),
            destination_address=serializer.validated_data.get('destination_address'),
            courier=serializer.validated_data.get('courier'),
            package_description=serializer.validated_data.get('package_description', ''),
            package_weight_kg=serializer.validated_data.get('package_weight_kg'),
            notes=serializer.validated_data.get('notes', ''),
        )

        # ارسال ایمیل ایجاد
        from apps.logistics.tasks import send_shipment_created_email
        send_shipment_created_email.delay(str(shipment.id))

        logger.info(f"Shipment created: {shipment.id}")

        return shipment

    @action(detail=True, methods=['post'])
    def assign_courier(self, request, pk=None):
        """تخصیص پیک به محموله"""
        shipment = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        courier = serializer.context['courier']

        try:
            shipment = ShippingService.assign_courier(shipment, courier)

            # ارسال ایمیل
            from apps.logistics.tasks import send_shipment_status_email
            send_shipment_status_email.delay(str(shipment.id), 'assigned')

            return Response({
                'message': _(f'Courier {courier.name} assigned.'),
                'shipment': ShipmentSerializer(shipment, context={'request': request}).data,
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """بروزرسانی وضعیت محموله"""
        shipment = self.get_object()
        serializer = self.get_serializer(
            data=request.data,
            context={'shipment': shipment}
        )
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data['status']
        description = serializer.validated_data.get('description', '')
        latitude = serializer.validated_data.get('latitude')
        longitude = serializer.validated_data.get('longitude')

        shipment = ShippingService.update_shipment_status(
            shipment=shipment,
            status=new_status,
            description=description,
            latitude=float(latitude) if latitude else None,
            longitude=float(longitude) if longitude else None,
            updated_by=request.user,
        )

        # ارسال ایمیل نوتیفیکیشن
        from apps.logistics.tasks import send_shipment_status_email
        send_shipment_status_email.delay(str(shipment.id), new_status)

        return Response({
            'message': _('Status updated.'),
            'shipment': ShipmentSerializer(shipment, context={'request': request}).data,
        })

    @action(detail=True, methods=['get'])
    def tracking(self, request, pk=None):
        """رهگیری کامل محموله"""
        shipment = self.get_object()
        tracking_data = ShippingService.get_shipment_tracking(shipment)
        return Response(tracking_data)

    @action(detail=False, methods=['post'])
    def cost_estimate(self, request):
        """استعلام هزینه ارسال"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from apps.logistics.services.shipping_service import ShippingService

        # محاسبه هزینه داخلی
        cost = ShippingService.calculate_shipping_cost(
            origin_lat=float(serializer.validated_data['origin_lat']),
            origin_lng=float(serializer.validated_data['origin_lng']),
            dest_lat=float(serializer.validated_data['dest_lat']),
            dest_lng=float(serializer.validated_data['dest_lng']),
            vehicle_type=serializer.validated_data.get('vehicle_type', 'motorcycle'),
            package_weight_kg=float(serializer.validated_data.get('package_weight_kg', 0)) if serializer.validated_data.get('package_weight_kg') else None,
            is_fragile=serializer.validated_data.get('is_fragile', False),
            is_express=serializer.validated_data.get('is_express', False),
        )

        # استعلام از سرویس‌های خارجی
        external = {}
        try:
            external = CourierService.get_price_estimates(
                origin_lat=float(serializer.validated_data['origin_lat']),
                origin_lng=float(serializer.validated_data['origin_lng']),
                dest_lat=float(serializer.validated_data['dest_lat']),
                dest_lng=float(serializer.validated_data['dest_lng']),
            )
        except Exception:
            pass

        return Response({
            'internal': cost,
            'external': external,
            'recommended': external.get('best') or 'internal',
        })

    @action(detail=False, methods=['get'])
    def my_shipments(self, request):
        """محموله‌های کاربر جاری"""
        shipments = ShippingService.get_user_shipments(request.user)

        page = self.paginate_queryset(shipments)
        if page is not None:
            serializer = ShipmentSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = ShipmentSerializer(shipments, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """لغو محموله"""
        shipment = self.get_object()

        if not shipment.can_cancel:
            return Response(
                {'error': _('Cannot cancel shipment in current status.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        reason = request.data.get('reason', 'Cancelled by user')

        shipment = ShippingService.update_shipment_status(
            shipment=shipment,
            status='cancelled',
            description=reason,
            updated_by=request.user,
        )

        # ارسال ایمیل
        from apps.logistics.tasks import send_shipment_status_email
        send_shipment_status_email.delay(str(shipment.id), 'cancelled')

        return Response({
            'message': _('Shipment cancelled.'),
            'shipment': ShipmentSerializer(shipment, context={'request': request}).data,
        })