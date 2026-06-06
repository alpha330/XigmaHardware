from decimal import Decimal
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.payment.models import PaymentGateway, PaymentLog


class PaymentGatewaySerializer(serializers.ModelSerializer):
    """سریالایزر درگاه پرداخت"""
    type_display = serializers.SerializerMethodField()
    mode_display = serializers.SerializerMethodField()

    class Meta:
        model = PaymentGateway
        fields = [
            'id', 'name', 'gateway_type', 'type_display',
            'mode', 'mode_display',
            'is_active', 'is_default', 'priority',
            'min_amount', 'max_amount',
            'description',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_type_display(self, obj):
        return {
            'code': obj.gateway_type,
            'label': obj.get_gateway_type_display(),
            'icon': {
                'payping': '🟢',
                'zarinpal': '🔵',
                'crypto': '₿',
                'card_to_card': '💳',
                'custom': '🔧',
            }.get(obj.gateway_type, '💳')
        }

    def get_mode_display(self, obj):
        return {
            'code': obj.mode,
            'label': obj.get_mode_display(),
            'is_test': obj.mode == 'test',
        }


class PaymentLogSerializer(serializers.ModelSerializer):
    """سریالایزر لاگ پرداخت"""
    status_display = serializers.SerializerMethodField()
    gateway_name = serializers.SerializerMethodField()
    invoice_number = serializers.SerializerMethodField()
    amount_display = serializers.SerializerMethodField()

    class Meta:
        model = PaymentLog
        fields = [
            'id', 'user', 'gateway', 'gateway_name',
            'invoice', 'invoice_number',
            'amount', 'amount_display',
            'status', 'status_display',
            'gateway_code', 'reference_code',
            'description',
            'payment_date', 'verified_at', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_status_display(self, obj):
        colors = {
            'pending': 'warning',
            'redirected': 'info',
            'verified': 'success',
            'failed': 'danger',
            'cancelled': 'secondary',
            'refunded': 'primary',
        }
        return {
            'code': obj.status,
            'label': obj.get_status_display(),
            'color': colors.get(obj.status, 'secondary'),
        }

    def get_gateway_name(self, obj):
        return obj.gateway.name if obj.gateway else '-'

    def get_invoice_number(self, obj):
        return obj.invoice.invoice_number if obj.invoice else None

    def get_amount_display(self, obj):
        return f'{int(obj.amount):,} Rials'


class PaymentCreateSerializer(serializers.Serializer):
    """سریالایزر ایجاد پرداخت"""
    amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=Decimal('1000'),
        error_messages={
            'required': _('Amount is required.'),
            'min_value': _('Minimum amount is 1,000 Rials.'),
        }
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
    )
    gateway_id = serializers.UUIDField(required=False)
    invoice_id = serializers.UUIDField(required=False)
    callback_url = serializers.URLField(required=False)

    def validate_amount(self, value):
        if value > 1000000000:
            raise serializers.ValidationError(_('Maximum amount is 1,000,000,000 Rials.'))
        return value


class PaymentVerifySerializer(serializers.Serializer):
    """سریالایزر تایید پرداخت"""
    refid = serializers.CharField(required=False, allow_blank=True)
    clientrefid = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField(required=False, allow_blank=True)


class PaymentCallbackSerializer(serializers.Serializer):
    """سریالایزر callback"""
    refid = serializers.CharField(required=False, allow_blank=True, max_length=200)
    clientrefid = serializers.CharField(required=False, allow_blank=True, max_length=200)