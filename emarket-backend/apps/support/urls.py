from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.ticket import TicketViewSet
from .views.warranty import WarrantyViewSet
from .views.chat import ChatViewSet
from .views.faq import FAQViewSet

router = DefaultRouter()
router.register(r'tickets', TicketViewSet, basename='ticket')
router.register(r'warranties', WarrantyViewSet, basename='warranty')
router.register(r'chats', ChatViewSet, basename='chat')
router.register(r'faqs', FAQViewSet, basename='faq')

app_name = 'support'

urlpatterns = [
    path('', include(router.urls)),
]