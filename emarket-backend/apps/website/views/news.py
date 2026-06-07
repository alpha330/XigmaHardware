from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from apps.website.models import News
from apps.website.serializers.news import NewsSerializer, NewsListSerializer
from apps.website.permissions import IsAdminOrReadOnly
from rest_framework.permissions import IsAuthenticated


class NewsViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                  mixins.CreateModelMixin, mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """ViewSet اخبار"""

    def get_serializer_class(self):
        return NewsListSerializer if self.action == 'list' else NewsSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'pinned', 'important']:
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminOrReadOnly()]

    def get_queryset(self):
        qs = News.objects.all()
        user = self.request.user
        if not user.is_authenticated or not (user.is_superuser or user.role == 'super_admin'):
            qs = qs.filter(status__in=['published', 'pinned'])
        return qs.order_by('-published_at')

    @action(detail=False, methods=['get'])
    def pinned(self, request):
        news = News.objects.filter(status='pinned').order_by('-published_at')[:5]
        return Response(NewsListSerializer(news, many=True, context={'request': request}).data)

    @action(detail=False, methods=['get'])
    def important(self, request):
        news = News.objects.filter(is_important=True, status__in=['published', 'pinned'])[:5]
        return Response(NewsListSerializer(news, many=True, context={'request': request}).data)