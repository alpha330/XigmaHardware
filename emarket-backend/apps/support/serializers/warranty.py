from rest_framework import serializers
from django.utils import timezone
from apps.support.models import Warranty


class WarrantySerializer(serializers.ModelSerializer):
    """گارانتی"""
    user_name = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    is_active = serializers.BooleanField(read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Warranty
        fields = [
            'id', 'warranty_number',
            'user', 'user_name', 'product', 'product_name',
            'invoice', 'status', 'status_display',
            'start_date', 'end_date', 'duration_months',
            'serial_number', 'warranty_type', 'coverage', 'terms',
            'is_active', 'days_remaining',
            'claim_date', 'claim_description', 'resolution',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'warranty_number', 'user', 'product', 'created_at', 'updated_at']

    def get_user_name(self, obj):
        return obj.user.get_display_name()

    def get_product_name(self, obj):
        return obj.product.name

    def get_status_display(self, obj):
        colors = {'active': 'success', 'expired': 'dark', 'claimed': 'warning', 'rejected': 'danger', 'completed': 'info'}
        return {'code': obj.status, 'label': obj.get_status_display(), 'color': colors.get(obj.status, 'secondary')}


class WarrantyClaimSerializer(serializers.Serializer):
    """ثبت ادعای گارانتی"""
    description = serializers.CharField(required=True)

    def validate_description(self, value):
        if len(value.strip()) < 20:
            raise serializers.ValidationError('Description must be at least 20 characters.')
        return value