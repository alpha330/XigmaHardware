from rest_framework import serializers
from apps.support.models import FAQ, FAQCategory


class FAQSerializer(serializers.ModelSerializer):
    """سوال متداول"""
    category_name = serializers.SerializerMethodField()

    class Meta:
        model = FAQ
        fields = [
            'id', 'category', 'category_name',
            'question', 'answer',
            'is_active', 'views_count', 'helpful_count',
            'sort_order', 'created_at',
        ]

    def get_category_name(self, obj):
        return obj.category.name if obj.category else None


class FAQCategorySerializer(serializers.ModelSerializer):
    """دسته‌بندی FAQ"""
    faqs = FAQSerializer(many=True, read_only=True)
    faqs_count = serializers.SerializerMethodField()

    class Meta:
        model = FAQCategory
        fields = ['id', 'name', 'slug', 'icon', 'sort_order', 'is_active', 'faqs_count', 'faqs']

    def get_faqs_count(self, obj):
        return obj.faqs.filter(is_active=True).count()