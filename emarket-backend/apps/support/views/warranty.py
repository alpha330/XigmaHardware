from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.translation import gettext_lazy as _
from apps.support.models import Warranty
from apps.support.serializers.warranty import WarrantySerializer, WarrantyClaimSerializer
from apps.support.permissions import CanManageSupport


class WarrantyViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """ViewSet گارانتی‌ها"""
    serializer_class = WarrantySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role == 'super_admin':
            return Warranty.objects.select_related('user', 'product').all()
        return Warranty.objects.filter(user=user)

    @action(detail=True, methods=['post'])
    def claim(self, request, pk=None):
        """ثبت ادعای گارانتی"""
        warranty = self.get_object()
        serializer = WarrantyClaimSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not warranty.is_active:
            return Response({'error': _('Warranty is not active.')}, status=400)

        warranty.status = 'claimed'
        warranty.claim_date = __import__('django').utils.timezone.now().date()
        warranty.claim_description = serializer.validated_data['description']
        warranty.save()

        # ایجاد تیکت خودکار
        from apps.support.models import Ticket
        Ticket.objects.create(
            user=request.user, category='warranty', priority='high',
            subject=f'Warranty Claim: {warranty.product.name}',
            body=serializer.validated_data['description'],
            product=warranty.product,
        )

        return Response({'message': _('Claim registered.')})

    @action(detail=False, methods=['get'])
    def check(self, request):
        """استعلام گارانتی با شماره سریال"""
        serial = request.query_params.get('serial')
        if not serial:
            return Response({'error': _('Serial number required.')}, status=400)

        try:
            warranty = Warranty.objects.get(serial_number=serial)
            return Response(WarrantySerializer(warranty).data)
        except Warranty.DoesNotExist:
            return Response({'found': False, 'message': _('No warranty found.')})

    @action(detail=False, methods=['get'])
    def my_warranties(self, request):
        """گارانتی‌های من"""
        warranties = Warranty.objects.filter(user=request.user)
        return Response(WarrantySerializer(warranties, many=True).data)