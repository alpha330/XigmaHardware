from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from apps.website.models import Article, ArticleCategory
from apps.website.serializers.article import ArticleSerializer, ArticleListSerializer, ArticleCategorySerializer
from apps.website.permissions import IsAdminOrReadOnly, IsAuthorOrAdmin


class ArticleViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                     mixins.CreateModelMixin, mixins.UpdateModelMixin,
                     viewsets.GenericViewSet):
    """ViewSet مقالات"""

    def get_serializer_class(self):
        return ArticleListSerializer if self.action == 'list' else ArticleSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'featured', 'categories', 'view']:
            return [AllowAny()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAuthorOrAdmin()]
        return [IsAuthenticated(), IsAdminOrReadOnly()]

    def get_queryset(self):
        qs = Article.objects.select_related('category', 'author')
        # ادمین همه رو می‌بینه
        user = self.request.user
        if not user.is_authenticated or not (user.is_superuser or user.role == 'super_admin'):
            qs = qs.filter(status='published')

        category = self.request.query_params.get('category')
        if category: qs = qs.filter(category__slug=category)
        search = self.request.query_params.get('search')
        if search:
            from django.db.models import Q
            qs = qs.filter(Q(title__icontains=search) | Q(content__icontains=search) | Q(tags__icontains=search))
        return qs.order_by('-published_at')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        articles = Article.objects.filter(status='published', is_featured=True)[:5]
        return Response(ArticleListSerializer(articles, many=True, context={'request': request}).data)

    @action(detail=False, methods=['get'])
    def categories(self, request):
        categories = ArticleCategory.objects.filter(is_active=True)
        return Response(ArticleCategorySerializer(categories, many=True).data)

    @action(detail=True, methods=['post'])
    def view(self, request, pk=None):
        article = self.get_object()
        article.views_count += 1
        article.save(update_fields=['views_count'])
        return Response({'views_count': article.views_count})