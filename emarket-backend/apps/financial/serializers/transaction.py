from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.financial.models import FinancialTransaction
from apps.financial.enums import TransactionType, PaymentStatus


class TransactionListSerializer(serializers.ModelSerializer):
    """سریالایزر لیست تراکنش‌ها"""
    user_name = serializers.SerializerMethodField()
    type_badge = serializers.SerializerMethodField()
    status_badge = serializers.SerializerMethodField()
    invoice_number = serializers.SerializerMethodField()
    transaction_date_jalali = serializers.SerializerMethodField()

    class Meta:
        model = FinancialTransaction
        fields = [
            'id', 'transaction_number', 'transaction_type', 'type_badge',
            'amount', 'status', 'status_badge',
            'user_name', 'invoice_number', 'payment_method',
            'reference_code', 'description',
            'transaction_date', 'transaction_date_jalali',
            'verified_at',
        ]

    def get_user_name(self, obj):
        if obj.user:
            return obj.user.get_display_name()
        return 'N/A'

    def get_type_badge(self, obj):
        icons = {
            'payment': '💳',
            'deposit': '📥',
            'withdraw': '📤',
            'refund': '↩️',
            'commission': '💸',
            'adjustment': '🔧',
            'wallet_charge': '💰',
        }
        return {
            'code': obj.transaction_type,
            'label': obj.get_transaction_type_display(),
            'icon': icons.get(obj.transaction_type, '💳'),
            'is_credit': obj.transaction_type in ['deposit', 'refund', 'wallet_charge'],
            'is_debit': obj.transaction_type in ['payment', 'withdraw', 'commission'],
        }

    def get_status_badge(self, obj):
        colors = {
            'pending': 'warning',
            'verified': 'success',
            'failed': 'danger',
            'refunded': 'info',
        }
        return {
            'code': obj.status,
            'label': obj.get_status_display(),
            'color': colors.get(obj.status, 'secondary'),
        }

    def get_invoice_number(self, obj):
        if obj.invoice:
            return obj.invoice.invoice_number
        return None

    def get_transaction_date_jalali(self, obj):
        try:
            import jdatetime
            return jdatetime.datetime.fromgregorian(
                datetime=obj.transaction_date
            ).strftime('%Y/%m/%d %H:%M')
        except ImportError:
            return None


class TransactionSerializer(serializers.ModelSerializer):
    """سریالایزر کامل تراکنش"""
    user_name = serializers.SerializerMethodField()
    type_badge = serializers.SerializerMethodField()
    status_badge = serializers.SerializerMethodField()
    invoice_number = serializers.SerializerMethodField()
    transaction_date_jalali = serializers.SerializerMethodField()
    verified_at_jalali = serializers.SerializerMethodField()

    class Meta:
        model = FinancialTransaction
        fields = [
            'id', 'transaction_number', 'transaction_type', 'type_badge',
            'user', 'user_name', 'invoice', 'invoice_number',
            'wallet', 'amount', 'status', 'status_badge',
            'payment_method', 'reference_code', 'gateway_response',
            'description', 'transaction_date', 'transaction_date_jalali',
            'verified_at', 'verified_at_jalali', 'verified_by',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'transaction_number', 'created_at', 'updated_at',
        ]

    def get_user_name(self, obj):
        return obj.user.get_display_name() if obj.user else 'N/A'

    def get_type_badge(self, obj):
        return {
            'code': obj.transaction_type,
            'label': obj.get_transaction_type_display(),
        }

    def get_status_badge(self, obj):
        return {
            'code': obj.status,
            'label': obj.get_status_display(),
        }

    def get_invoice_number(self, obj):
        return obj.invoice.invoice_number if obj.invoice else None

    def get_transaction_date_jalali(self, obj):
        try:
            import jdatetime
            return jdatetime.datetime.fromgregorian(
                datetime=obj.transaction_date
            ).strftime('%Y/%m/%d %H:%M')
        except ImportError:
            return None

    def get_verified_at_jalali(self, obj):
        if obj.verified_at:
            try:
                import jdatetime
                return jdatetime.datetime.fromgregorian(
                    datetime=obj.verified_at
                ).strftime('%Y/%m/%d %H:%M')
            except ImportError:
                return None
        return None


class PaymentVerificationSerializer(serializers.Serializer):
    """سریالایزر تایید پرداخت"""
    reference_code = serializers.CharField(required=True, max_length=100)
    payment_method = serializers.ChoiceField(
        choices=[('card_to_card', 'Card to Card'), ('bank_transfer', 'Bank Transfer'),
                 ('online_gateway', 'Online Gateway'), ('wallet', 'Wallet'),
                 ('cash', 'Cash'), ('cheque', 'Cheque')],
        required=True
    )
    notes = serializers.CharField(required=False, allow_blank=True, max_length=500)

    def validate_reference_code(self, value):
        """بررسی یکتایی کد پیگیری"""
        if FinancialTransaction.objects.filter(reference_code=value, status='verified').exists():
            raise serializers.ValidationError(_('This reference code has already been used.'))
        return value