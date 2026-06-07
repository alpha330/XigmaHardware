from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from apps.website.models import Page
from apps.website.serializers.page import PageSerializer, PageListSerializer
from apps.website.permissions import IsAdminOrReadOnly


class PageViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                  mixins.CreateModelMixin, mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """ViewSet صفحات وبسایت"""
    queryset = Page.objects.filter(is_active=True)

    def get_serializer_class(self):
        return PageListSerializer if self.action == 'list' else PageSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'about', 'terms']:
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminOrReadOnly()]

    def get_queryset(self):
        qs = Page.objects.filter(is_active=True)
        # ادمین همه رو می‌بینه
        if self.request.user.is_authenticated and self.request.user.is_superuser:
            qs = Page.objects.all()
        page_type = self.request.query_params.get('type')
        if page_type: qs = qs.filter(page_type=page_type)
        return qs

    @action(detail=False, methods=['get'])
    def about(self, request):
        page = Page.objects.filter(page_type='about', is_active=True).first()
        if page: return Response(PageSerializer(page).data)
        return Response({'found': False})

    @action(detail=False, methods=['get'])
    def terms(self, request):
        page = Page.objects.filter(page_type='terms', is_active=True).first()
        if page: return Response(PageSerializer(page).data)
        return Response({'found': False})

    @action(detail=False, methods=['get'])
    def privacy(self, request):
        page = Page.objects.filter(page_type='privacy', is_active=True).first()
        if page: return Response(PageSerializer(page).data)
        return Response({'found': False})