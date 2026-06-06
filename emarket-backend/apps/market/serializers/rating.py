from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.market.models import ProductRating


class RatingSerializer(serializers.ModelSerializer):
    """سریالایزر امتیازدهی"""
    user_name = serializers.SerializerMethodField()
    average_score = serializers.FloatField(read_only=True)

    class Meta:
        model = ProductRating
        fields = [
            'id', 'product', 'user', 'user_name',
            'value_for_money', 'quality', 'performance', 'overall',
            'average_score',
            'is_verified_purchase',
            'created_at',
        ]
        read_only_fields = ['id', 'user', 'created_at']

    def get_user_name(self, obj):
        return obj.user.get_display_name()

    def validate(self, data):
        """هر امتیاز باید ۱-۵ باشه"""
        for field in ['value_for_money', 'quality', 'performance', 'overall']:
            value = data.get(field)
            if value and not 1 <= value <= 5:
                raise serializers.ValidationError({field: _('Must be between 1 and 5.')})
        return data


class RatingCreateSerializer(serializers.ModelSerializer):
    """سریالایزر ایجاد امتیاز"""

    class Meta:
        model = ProductRating
        fields = ['value_for_money', 'quality', 'performance', 'overall']

    def validate(self, data):
        for field in ['value_for_money', 'quality', 'performance', 'overall']:
            if field not in data:
                raise serializers.ValidationError({field: _('This field is required.')})
        return data


class RatingSummarySerializer(serializers.Serializer):
    """خلاصه امتیازات"""
    avg_rating = serializers.DecimalField(max_digits=3, decimal_places=2)
    rating_count = serializers.IntegerField()
    avg_value_for_money = serializers.DecimalField(max_digits=3, decimal_places=2)
    avg_quality = serializers.DecimalField(max_digits=3, decimal_places=2)
    avg_performance = serializers.DecimalField(max_digits=3, decimal_places=2)

    stars_display = serializers.SerializerMethodField()

    def get_stars_display(self, obj):
        return {
            'overall': '⭐' * int(obj['avg_rating']),
            'value_for_money': '⭐' * int(obj['avg_value_for_money']),
            'quality': '⭐' * int(obj['avg_quality']),
            'performance': '⭐' * int(obj['avg_performance']),
        }