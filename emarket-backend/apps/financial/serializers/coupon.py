from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.financial.models.coupon import Coupon


class CouponSerializer(serializers.ModelSerializer):
    is_valid_now = serializers.SerializerMethodField()

    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'discount_type', 'discount_value',
            'max_uses', 'used_count',
            'min_order_amount', 'valid_from', 'valid_to',
            'is_active', 'description', 'is_valid_now',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'used_count', 'created_at', 'updated_at']

    def get_is_valid_now(self, obj):
        valid, _ = obj.is_valid()
        return valid


class CouponApplySerializer(serializers.Serializer):
    code = serializers.CharField(required=True)
    invoice_id = serializers.UUIDField(required=True)