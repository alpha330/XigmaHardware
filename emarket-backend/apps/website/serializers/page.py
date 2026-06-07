from rest_framework import serializers
from apps.website.models import Page


class PageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ['id', 'title', 'slug', 'page_type', 'is_active', 'updated_at']


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = [
            'id', 'title', 'slug', 'page_type', 'content',
            'meta_title', 'meta_description',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']