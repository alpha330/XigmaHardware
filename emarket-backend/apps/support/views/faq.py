from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from apps.support.models import FAQ, FAQCategory
from apps.support.serializers.faq import FAQSerializer, FAQCategorySerializer


class FAQViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """ViewSet سوالات متداول"""
    queryset = FAQ.objects.filter(is_active=True)
    serializer_class = FAQSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = FAQ.objects.filter(is_active=True)
        category = self.request.query_params.get('category')
        if category: qs = qs.filter(category__slug=category)

        search = self.request.query_params.get('search')
        if search:
            from django.db.models import Q
            qs = qs.filter(Q(question__icontains=search) | Q(answer__icontains=search))

        return qs

    @action(detail=False, methods=['get'])
    def categories(self, request):
        """دسته‌بندی‌های FAQ"""
        categories = FAQCategory.objects.filter(is_active=True).prefetch_related('faqs')
        return Response(FAQCategorySerializer(categories, many=True).data)

    @action(detail=True, methods=['post'])
    def helpful(self, request, pk=None):
        """علامت‌گذاری مفید"""
        faq = self.get_object()
        faq.helpful_count += 1
        faq.save(update_fields=['helpful_count'])
        return Response({'helpful_count': faq.helpful_count})

    @action(detail=True, methods=['post'])
    def view(self, request, pk=None):
        """افزایش بازدید"""
        faq = self.get_object()
        faq.views_count += 1
        faq.save(update_fields=['views_count'])
        return Response({'views_count': faq.views_count})