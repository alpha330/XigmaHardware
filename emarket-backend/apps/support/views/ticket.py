from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.translation import gettext_lazy as _
from apps.support.models import Ticket, TicketMessage
from apps.support.serializers.ticket import (
    TicketSerializer, TicketListSerializer, TicketCreateSerializer,
    TicketMessageSerializer, TicketStatusSerializer, TicketReplySerializer,
)
from apps.support.permissions import CanManageSupport


class TicketViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                    mixins.CreateModelMixin, viewsets.GenericViewSet):
    """ViewSet مدیریت تیکت‌ها"""
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create': return TicketCreateSerializer
        if self.action == 'list': return TicketListSerializer
        if self.action == 'reply': return TicketReplySerializer
        if self.action == 'update_status': return TicketStatusSerializer
        return TicketSerializer

    def get_queryset(self):
        qs = Ticket.objects.prefetch_related('messages')
        user = self.request.user
        if user.is_superuser or user.role in ['super_admin', 'accountant']:
            # فیلترها
            status_f = self.request.query_params.get('status')
            if status_f: qs = qs.filter(status=status_f)
            priority_f = self.request.query_params.get('priority')
            if priority_f: qs = qs.filter(priority=priority_f)
            return qs
        return qs.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        """پاسخ به تیکت"""
        ticket = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        msg = TicketMessage.objects.create(
            ticket=ticket, sender=request.user,
            body=serializer.validated_data['body'],
            is_staff_reply=request.user.is_staff or request.user.is_superuser,
            is_internal_note=serializer.validated_data.get('is_internal_note', False),
            attachment=serializer.validated_data.get('attachment'),
        )

        # آپدیت وضعیت تیکت
        if ticket.status in ['open', 'waiting_customer']:
            ticket.status = 'in_progress' if request.user.is_staff else 'waiting_customer'
            ticket.save()

        return Response(TicketMessageSerializer(msg).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """تغییر وضعیت تیکت"""
        ticket = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ticket.status = serializer.validated_data['status']
        if ticket.status in ['resolved', 'closed']:
            from django.utils import timezone
            ticket.resolved_at = timezone.now()
        ticket.save()

        if serializer.validated_data.get('note'):
            TicketMessage.objects.create(
                ticket=ticket, sender=request.user,
                body=serializer.validated_data['note'],
                is_staff_reply=True, is_internal_note=True,
            )

        return Response({'message': _('Status updated.'), 'status': ticket.status})

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """تخصیص تیکت به ادمین"""
        if not request.user.is_superuser:
            return Response({'error': _('Permission denied.')}, status=403)

        ticket = self.get_object()
        agent_id = request.data.get('agent_id')

        from apps.accounts.models import User
        agent = User.objects.get(id=agent_id)
        ticket.assigned_to = agent
        ticket.status = 'in_progress'
        ticket.save()

        return Response({'message': _('Assigned.'), 'assigned_to': agent.get_display_name()})

    @action(detail=False, methods=['get'])
    def my_tickets(self, request):
        """تیکت‌های من"""
        tickets = Ticket.objects.filter(user=request.user).order_by('-created_at')
        return Response(TicketListSerializer(tickets, many=True).data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """آمار تیکت‌ها (ادمین)"""
        if not request.user.is_superuser:
            return Response({'error': _('Permission denied.')}, status=403)

        from django.db.models import Count
        stats = {
            'total': Ticket.objects.count(),
            'open': Ticket.objects.filter(status='open').count(),
            'in_progress': Ticket.objects.filter(status='in_progress').count(),
            'resolved': Ticket.objects.filter(status='resolved').count(),
            'unassigned': Ticket.objects.filter(assigned_to__isnull=True).count(),
        }
        return Response(stats)