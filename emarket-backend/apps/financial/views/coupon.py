from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.translation import gettext_lazy as _
from apps.financial.models.coupon import Coupon
from apps.financial.serializers.coupon import CouponSerializer, CouponApplySerializer
from apps.financial.services.coupon_service import CouponService


class CouponViewSet(mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    viewsets.GenericViewSet):
    """مدیریت کوپن‌های تخفیف"""
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated]   # در واقع باید CanManageFinancial باشد

    @action(detail=False, methods=['post'])
    def apply(self, request):
        """اعمال کوپن روی فاکتور"""
        serializer = CouponApplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data['code']
        invoice_id = serializer.validated_data['invoice_id']

        try:
            result = CouponService.apply_coupon(code, invoice_id)
            return Response(result)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def validate(self, request):
        """فقط بررسی اعتبار کوپن"""
        code = request.query_params.get('code')
        if not code:
            return Response({'error': _('Code required.')}, status=400)

        try:
            coupon = Coupon.objects.get(code=code.upper())
            valid, msg = coupon.is_valid()
            return Response({
                'valid': valid,
                'message': str(msg),
                'discount_type': coupon.discount_type,
                'discount_value': float(coupon.discount_value),
            })
        except Coupon.DoesNotExist:
            return Response({'valid': False, 'message': _('Coupon not found.')})