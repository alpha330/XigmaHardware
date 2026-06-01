"""
Wallet Serializers
- نمایش کیف پول
- تراکنش‌ها
- واریز/برداشت
"""

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from apps.accounts.models import Wallet, WalletTransaction


class WalletSerializer(serializers.ModelSerializer):
    """
    سریالایزر کیف پول
    """
    available_balance = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )
    total_transactions = serializers.SerializerMethodField()
    last_transaction = serializers.SerializerMethodField()
    
    class Meta:
        model = Wallet
        fields = [
            'id', 'user',
            'balance', 'blocked_balance', 'available_balance',
            'is_active',
            'total_transactions', 'last_transaction',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'user', 'balance', 'blocked_balance',
            'is_active', 'created_at', 'updated_at',
        ]
    
    def get_total_transactions(self, obj):
        """تعداد کل تراکنش‌ها"""
        return obj.transactions.count()
    
    def get_last_transaction(self, obj):
        """آخرین تراکنش"""
        last_tx = obj.transactions.first()  # ordering = '-created_at'
        if last_tx:
            return {
                'id': str(last_tx.id),
                'type': last_tx.transaction_type,
                'amount': float(last_tx.amount),
                'status': last_tx.status,
                'date': last_tx.created_at,
            }
        return None


class WalletTransactionSerializer(serializers.ModelSerializer):
    """
    سریالایزر تراکنش کیف پول
    """
    transaction_type_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = WalletTransaction
        fields = [
            'id', 'wallet',
            'transaction_type', 'transaction_type_display',
            'amount', 'status', 'status_display',
            'balance_before', 'balance_after',
            'description', 'reference_id',
            'metadata',
            'created_at', 'completed_at',
        ]
        read_only_fields = [
            'id', 'wallet', 'transaction_type',
            'amount', 'status', 'balance_before', 'balance_after',
            'created_at', 'completed_at',
        ]
    
    def get_transaction_type_display(self, obj):
        """نمایش فارسی نوع تراکنش"""
        type_labels = {
            'deposit': _('Deposit'),
            'withdraw': _('Withdraw'),
            'payment': _('Payment'),
            'refund': _('Refund'),
            'commission': _('Commission'),
            'bonus': _('Bonus'),
        }
        return {
            'code': obj.transaction_type,
            'label': type_labels.get(obj.transaction_type, obj.transaction_type),
            'is_credit': obj.transaction_type in ['deposit', 'refund', 'bonus'],
        }
    
    def get_status_display(self, obj):
        """نمایش فارسی وضعیت"""
        status_colors = {
            'pending': 'warning',
            'completed': 'success',
            'failed': 'danger',
            'cancelled': 'secondary',
        }
        return {
            'code': obj.status,
            'label': obj.get_status_display(),
            'color': status_colors.get(obj.status, 'secondary'),
        }


class WalletDepositSerializer(serializers.Serializer):
    """
    سریالایزر واریز به کیف پول
    """
    amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=1000,  # حداقل 1000 تومان
        error_messages={
            'required': _('Amount is required.'),
            'min_value': _('Minimum deposit amount is 1,000 Rials.'),
        }
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
    )
    reference_id = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=100,
    )
    metadata = serializers.JSONField(
        required=False,
        default=dict,
    )
    
    def validate_amount(self, value):
        """اعتبارسنجی مبلغ"""
        if value <= 0:
            raise serializers.ValidationError(
                _('Amount must be positive.')
            )
        
        # محدودیت حداکثر (مثلاً 100 میلیون تومان)
        if value > 1000000000:
            raise serializers.ValidationError(
                _('Amount exceeds maximum limit.')
            )
        
        return value


class WalletWithdrawSerializer(serializers.Serializer):
    """
    سریالایزر برداشت از کیف پول
    """
    amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=1000,  # حداقل 1000 تومان
        error_messages={
            'required': _('Amount is required.'),
            'min_value': _('Minimum withdrawal amount is 1,000 Rials.'),
        }
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
    )
    reference_id = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=100,
    )
    metadata = serializers.JSONField(
        required=False,
        default=dict,
    )
    
    def validate_amount(self, value):
        """اعتبارسنجی مبلغ"""
        if value <= 0:
            raise serializers.ValidationError(
                _('Amount must be positive.')
            )
        return value