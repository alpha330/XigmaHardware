from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from apps.website.models import ContactMessage, Newsletter
from apps.website.serializers.contact import ContactSerializer, NewsletterSerializer
from apps.website.permissions import AllowCreateOnly


class ContactViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                     mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """ViewSet تماس با ما"""
    queryset = ContactMessage.objects.all()
    serializer_class = ContactSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [AllowCreateOnly()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ContactMessage.objects.create(
            name=serializer.validated_data['name'],
            email=serializer.validated_data['email'],
            phone=serializer.validated_data.get('phone', ''),
            subject=serializer.validated_data['subject'],
            message=serializer.validated_data['message'],
            ip_address=self._get_ip(request),
        )

        from apps.website.tasks import send_contact_notification
        send_contact_notification.delay(
            serializer.validated_data['name'],
            serializer.validated_data['email'],
            serializer.validated_data['subject'],
            serializer.validated_data['message'][:200],
        )

        return Response(
            {'message': 'Your message has been sent.'},
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['post'])
    def subscribe(self, request):
        serializer = NewsletterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        Newsletter.objects.get_or_create(
            email=serializer.validated_data['email'],
            defaults={'is_active': True},
        )
        return Response({'message': 'Subscribed.'}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def unsubscribe(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email required.'}, status=400)

        from django.utils import timezone
        Newsletter.objects.filter(email=email).update(is_active=False, unsubscribed_at=timezone.now())
        return Response({'message': 'Unsubscribed.'})

    def _get_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded_for.split(',')[0].strip() if x_forwarded_for else request.META.get('REMOTE_ADDR')