from rest_framework import serializers
from apps.website.models import News


class NewsListSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = News
        fields = [
            'id', 'title', 'slug', 'excerpt', 'image_url',
            'status', 'is_important', 'published_at',
        ]

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None


class NewsSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = News
        fields = [
            'id', 'title', 'slug', 'excerpt', 'content',
            'image', 'image_url', 'status', 'is_important',
            'published_at', 'created_at',
        ]
        read_only_fields = ['id', 'slug', 'created_at']

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None