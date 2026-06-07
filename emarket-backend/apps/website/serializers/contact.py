from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.website.models import ContactMessage, Newsletter


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError(_('Name must be at least 2 characters.'))
        return value.strip()

    def validate_subject(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError(_('Subject must be at least 5 characters.'))
        return value.strip()

    def validate_message(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError(_('Message must be at least 10 characters.'))
        return value.strip()


class NewsletterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newsletter
        fields = ['email']

    def validate_email(self, value):
        if Newsletter.objects.filter(email=value, is_active=True).exists():
            raise serializers.ValidationError(_('This email is already subscribed.'))
        return value.lower()