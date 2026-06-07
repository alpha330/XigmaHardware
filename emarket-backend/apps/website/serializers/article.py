from rest_framework import serializers
from apps.website.models import Article, ArticleCategory


class ArticleCategorySerializer(serializers.ModelSerializer):
    articles_count = serializers.SerializerMethodField()

    class Meta:
        model = ArticleCategory
        fields = ['id', 'name', 'slug', 'description', 'is_active', 'articles_count']

    def get_articles_count(self, obj):
        return obj.articles.filter(status='published').count()


class ArticleListSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'category_name', 'author_name',
            'excerpt', 'image_url', 'is_featured',
            'views_count', 'tags', 'published_at', 'created_at',
        ]

    def get_category_name(self, obj): return obj.category.name if obj.category else None
    def get_author_name(self, obj): return obj.author.get_display_name() if obj.author else None
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None


class ArticleSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    related_articles = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'category', 'category_name',
            'author', 'author_name', 'excerpt', 'content',
            'image', 'image_url', 'status', 'is_featured',
            'views_count', 'tags',
            'meta_title', 'meta_description',
            'related_articles',
            'published_at', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'views_count', 'created_at', 'updated_at']

    def get_category_name(self, obj): return obj.category.name if obj.category else None
    def get_author_name(self, obj): return obj.author.get_display_name() if obj.author else None
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None

    def get_related_articles(self, obj):
        related = Article.objects.filter(category=obj.category, status='published').exclude(id=obj.id)[:3]
        return ArticleListSerializer(related, many=True, context=self.context).data