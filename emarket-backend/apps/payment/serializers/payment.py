from decimal import Decimal
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.payment.models import PaymentGateway, PaymentLog


class PaymentGatewaySerializer(serializers.ModelSerializer):
    type_display = serializers.SerializerMethodField()
    mode_display = serializers.SerializerMethodField()

    class Meta:
        model = PaymentGateway
        fields = [
            'id', 'name', 'gateway_type', 'type_display',
            'mode', 'mode_display', 'is_active', 'is_default',
            'priority', 'min_amount', 'max_amount', 'description',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_type_display(self, obj):
        icons = {
            'payping': '🟢',
            'zarinpal': '🔵',
            'crypto': '₿',
            'card_to_card': '💳',
            'custom': '🔧',
        }
        return {
            'code': obj.gateway_type,
            'label': obj.get_gateway_type_display(),
            'icon': icons.get(obj.gateway_type, '💳'),
        }

    def get_mode_display(self, obj):
        return {
            'code': obj.mode,
            'label': obj.get_mode_display(),
            'is_test': obj.mode == 'test',
        }

class PaymentLogSerializer(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField()
    gateway_name = serializers.SerializerMethodField()
    invoice_number = serializers.SerializerMethodField()
    amount_display = serializers.SerializerMethodField()

    class Meta:
        model = PaymentLog
        fields = [
            'id', 'user', 'gateway', 'gateway_name',
            'invoice', 'invoice_number', 'amount', 'amount_display',
            'status', 'status_display', 'gateway_code', 'reference_code',
            'description', 'payment_date', 'verified_at', 'created_at',
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
        return f"{int(obj.amount):,} ریال"


class PaymentCreateSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=Decimal('1000'),
        error_messages={
            'required': _('مبلغ الزامی است.'),
            'min_value': _('حداقل مبلغ پرداخت ۱٬۰۰۰ ریال است.'),
            'invalid': _('مبلغ وارد شده معتبر نیست.'),
        }
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
        error_messages={
            'max_length': _('توضیحات نمی‌تواند بیشتر از ۵۰۰ کاراکتر باشد.'),
        }
    )
    gateway_id = serializers.UUIDField(required=False, allow_null=True)
    invoice_id = serializers.UUIDField(required=False, allow_null=True)
    callback_url = serializers.URLField(required=False, allow_blank=True)

    def validate_amount(self, value):
        if value > Decimal('1000000000'):
            raise serializers.ValidationError(_('حداکثر مبلغ قابل پرداخت ۱ میلیارد ریال است.'))
        return value

    def validate(self, attrs):
        # مثال: اعتبارسنجی ترکیبی (در صورت نیاز)
        if attrs.get('invoice_id') and attrs.get('gateway_id'):
            # می‌توانی اینجا منطق خاصی اضافه کنی
            pass
        return attrs


class PaymentVerifySerializer(serializers.Serializer):
    refid = serializers.CharField(required=False, allow_blank=True)
    clientrefid = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField(required=False, allow_blank=True)
    payment_log_id = serializers.UUIDField(required=False, allow_null=True)
    authority = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if not any([attrs.get('refid'), attrs.get('clientrefid'), attrs.get('authority')]):
            raise serializers.ValidationError({
                'non_field_errors': _('حداقل یکی از فیلدهای refid، clientrefid یا authority باید ارسال شود.')
            })
        return attrs


class PaymentCallbackSerializer(serializers.Serializer):
    refid = serializers.CharField(required=False, allow_blank=True, max_length=200)
    clientrefid = serializers.CharField(required=False, allow_blank=True, max_length=200)
    status = serializers.CharField(required=False, allow_blank=True)
    authority = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if not attrs.get('authority') and not attrs.get('refid'):
            raise serializers.ValidationError({
                'non_field_errors': _('شناسه تراکنش (Authority یا RefID) الزامی است.')
            })
        return attrs