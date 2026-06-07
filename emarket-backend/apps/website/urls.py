from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.page import PageViewSet
from .views.article import ArticleViewSet
from .views.news import NewsViewSet
from .views.contact import ContactViewSet

router = DefaultRouter()
router.register(r'pages', PageViewSet, basename='page')
router.register(r'articles', ArticleViewSet, basename='article')
router.register(r'news', NewsViewSet, basename='news')
router.register(r'contact', ContactViewSet, basename='contact')

app_name = 'website'

urlpatterns = [
    path('', include(router.urls)),
    path('newsletter/subscribe/', ContactViewSet.as_view({'post': 'subscribe'}), name='newsletter-subscribe'),
    path('newsletter/unsubscribe/', ContactViewSet.as_view({'post': 'unsubscribe'}), name='newsletter-unsubscribe'),
]