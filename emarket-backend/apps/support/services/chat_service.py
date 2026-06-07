import logging
from django.db import transaction as db_transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.support.models import ChatSession, ChatMessage
from apps.support.enums import ChatStatus

logger = logging.getLogger(__name__)


class ChatService:
    """
    سرویس مدیریت چت آنلاین

    عملیات:
    - شروع چت
    - ارسال پیام
    - اتصال agent
    - بستن چت
    """

    @classmethod
    @db_transaction.atomic
    def start_chat(cls, user, subject='', message=''):
        """
        شروع چت جدید

        Args:
            user: کاربر
            subject: موضوع
            message: اولین پیام

        Returns:
            ChatSession
        """
        # بستن چت‌های باز قبلی
        ChatSession.objects.filter(
            user=user, status__in=[ChatStatus.WAITING, ChatStatus.ACTIVE]
        ).update(status=ChatStatus.CLOSED, ended_at=timezone.now())

        session = ChatSession.objects.create(
            user=user,
            subject=subject,
            status=ChatStatus.WAITING,
        )

        if message:
            ChatMessage.objects.create(
                session=session,
                sender=user,
                message=message,
            )

        logger.info(f"Chat started: {session.id} by {user.email or user.mobile}")

        return session

    @classmethod
    @db_transaction.atomic
    def send_message(cls, session, sender, message):
        """
        ارسال پیام در چت

        Args:
            session: جلسه چت
            sender: فرستنده
            message: متن

        Returns:
            ChatMessage
        """
        if session.status == ChatStatus.CLOSED:
            raise ValueError(_('Chat is closed.'))

        # اگر agent هست و چت waiting بود، فعالش کن
        if sender.is_staff and session.status == ChatStatus.WAITING:
            session.status = ChatStatus.ACTIVE
            session.agent = sender
            session.save()

        msg = ChatMessage.objects.create(
            session=session,
            sender=sender,
            message=message,
        )

        logger.info(f"Chat message: {session.id} by {sender.get_display_name()}")

        return msg

    @classmethod
    @db_transaction.atomic
    def assign_agent(cls, session, agent):
        """
        اتصال agent به چت

        Args:
            session: جلسه چت
            agent: کاربر پشتیبان

        Returns:
            ChatSession
        """
        session.agent = agent
        session.status = ChatStatus.ACTIVE
        session.save()

        logger.info(f"Agent {agent.get_display_name()} assigned to chat {session.id}")

        return session

    @classmethod
    @db_transaction.atomic
    def close_chat(cls, session):
        """
        بستن چت

        Args:
            session: جلسه چت
        """
        session.status = ChatStatus.CLOSED
        session.ended_at = timezone.now()
        session.save()

        logger.info(f"Chat closed: {session.id}")

    @classmethod
    def get_waiting_chats(cls):
        """چت‌های در انتظار"""
        return ChatSession.objects.filter(status=ChatStatus.WAITING)

    @classmethod
    def get_active_chats_for_agent(cls, agent):
        """چت‌های فعال یک agent"""
        return ChatSession.objects.filter(agent=agent, status=ChatStatus.ACTIVE)