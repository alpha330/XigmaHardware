from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.translation import gettext_lazy as _
from apps.support.models import ChatSession, ChatMessage
from apps.support.serializers.chat import ChatSessionSerializer, ChatMessageSerializer, ChatStartSerializer


class ChatViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """ViewSet چت آنلاین"""
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'start': return ChatStartSerializer
        return ChatSessionSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role == 'super_admin':
            return ChatSession.objects.prefetch_related('messages').all()
        return ChatSession.objects.filter(user=user)

    @action(detail=False, methods=['post'])
    def start(self, request):
        """شروع چت جدید"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # غیرفعال کردن چت‌های قبلی
        ChatSession.objects.filter(user=request.user, status='waiting').update(status='closed')

        session = ChatSession.objects.create(
            user=request.user,
            subject=serializer.validated_data.get('subject', ''),
            status='waiting',
        )

        ChatMessage.objects.create(
            session=session, sender=request.user,
            message=serializer.validated_data['message'],
        )

        return Response(ChatSessionSerializer(session, context={'request': request}).data, status=201)

    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """ارسال پیام"""
        session = self.get_object()
        message = request.data.get('message', '')

        if not message.strip():
            return Response({'error': _('Message required.')}, status=400)

        ChatMessage.objects.create(session=session, sender=request.user, message=message)

        return Response({'message': _('Sent.')})

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """بستن چت"""
        session = self.get_object()
        session.status = 'closed'
        session.ended_at = __import__('django').utils.timezone.now()
        session.save()
        return Response({'message': _('Chat closed.')})

    @action(detail=False, methods=['get'])
    def active(self, request):
        """چت‌های فعال (ادمین)"""
        if not request.user.is_superuser:
            return Response({'error': _('Permission denied.')}, status=403)

        sessions = ChatSession.objects.filter(status__in=['waiting', 'active'])
        return Response(ChatSessionSerializer(sessions, many=True).data)