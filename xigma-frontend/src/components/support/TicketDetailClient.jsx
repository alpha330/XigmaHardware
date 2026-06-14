// src/components/support/TicketDetailClient.jsx
'use client';

import React, { useState, useEffect, useRef } from 'react';
import styled from '@emotion/styled';
import Link from 'next/link';
import { apiFetch } from '../../utils/apiFetch';
import { useToast } from '../ui/ToastProvider';

// ================= STYLES =================
const PageWrapper = styled.div`
  max-width: 900px;
  margin: 2rem auto;
  padding: 0 2rem;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 120px); /* برای فیکس کردن باکس چت در صفحه */
`;

const BackLink = styled(Link)`
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 0.95rem;
  margin-bottom: 1.5rem;
  text-decoration: none;
  font-weight: bold;
  &:hover { color: ${({ theme }) => theme.colors.primary}; }
`;

const TicketHeader = styled.div`
  background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 16px 16px 0 0;
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;

  @media (max-width: 600px) {
    flex-direction: column; align-items: flex-start; gap: 1rem;
  }
`;

const TitleInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.4rem;

  h1 { margin: 0; font-size: 1.4rem; color: ${({ theme }) => theme.colors.textMain}; }
  span { font-size: 0.85rem; color: ${({ theme }) => theme.colors.textMuted}; font-family: monospace; }
`;

const StatusBadge = styled.div`
  font-size: 0.85rem;
  padding: 0.5rem 1.2rem;
  border-radius: 20px;
  font-weight: bold;
  background-color: ${({ theme, status }) =>
    status === 'open' ? `${theme.colors.success}15` :
    status === 'in_progress' ? `${theme.colors.primary}15` :
    status === 'waiting_customer' ? `${theme.colors.warning}15` :
    status === 'closed' || status === 'resolved' ? `${theme.colors.textMuted}20` : `${theme.colors.border}50`};

  color: ${({ theme, status }) =>
    status === 'open' ? theme.colors.success :
    status === 'in_progress' ? theme.colors.primary :
    status === 'waiting_customer' ? theme.colors.warning :
    status === 'closed' || status === 'resolved' ? theme.colors.textMuted : theme.colors.textMain};
`;

// --- Messages Area ---
const ChatBox = styled.div`
  flex: 1;
  background-color: ${({ theme }) => theme.colors.background};
  border-left: 1px solid ${({ theme }) => theme.colors.border};
  border-right: 1px solid ${({ theme }) => theme.colors.border};
  padding: 1.5rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;

  &::-webkit-scrollbar { width: 6px; }
  &::-webkit-scrollbar-thumb { background-color: ${({ theme }) => theme.colors.border}; border-radius: 4px; }
`;

const MessageBubbleWrapper = styled.div`
  display: flex;
  flex-direction: column;
  align-items: ${({ isStaff }) => isStaff ? 'flex-start' : 'flex-end'};
  max-width: 80%;
  align-self: ${({ isStaff }) => isStaff ? 'flex-start' : 'flex-end'};
`;

const SenderName = styled.span`
  font-size: 0.8rem;
  color: ${({ theme }) => theme.colors.textMuted};
  margin-bottom: 0.3rem;
  margin-right: ${({ isStaff }) => isStaff ? '0' : '0.5rem'};
  margin-left: ${({ isStaff }) => isStaff ? '0.5rem' : '0'};
`;

const BubbleContent = styled.div`
  background-color: ${({ theme, isStaff }) => isStaff ? theme.colors.surface : theme.colors.primary};
  color: ${({ theme, isStaff }) => isStaff ? theme.colors.textMain : '#fff'};
  border: 1px solid ${({ theme, isStaff }) => isStaff ? theme.colors.border : theme.colors.primary};
  padding: 1rem 1.2rem;
  border-radius: ${({ isStaff }) => isStaff ? '16px 16px 16px 0' : '16px 16px 0 16px'};
  line-height: 1.6;
  font-size: 0.95rem;
  white-space: pre-wrap;
  word-break: break-word;
`;

const AttachmentLink = styled.a`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.8rem;
  padding: 0.5rem 0.8rem;
  background-color: rgba(0,0,0,0.1);
  border-radius: 8px;
  text-decoration: none;
  font-size: 0.85rem;
  color: inherit;
  font-weight: bold;

  &:hover { background-color: rgba(0,0,0,0.15); }
`;

const MessageTime = styled.div`
  font-size: 0.75rem;
  color: ${({ theme }) => theme.colors.textMuted};
  margin-top: 0.3rem;
  align-self: ${({ isStaff }) => isStaff ? 'flex-end' : 'flex-start'};
`;

// --- Reply Area ---
const ReplyForm = styled.form`
  background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 0 0 16px 16px;
  padding: 1rem;
  display: flex;
  align-items: flex-end;
  gap: 1rem;
`;

const TextArea = styled.textarea`
  flex: 1;
  background-color: ${({ theme }) => theme.colors.background};
  border: 1px solid ${({ theme }) => theme.colors.border};
  color: ${({ theme }) => theme.colors.textMain};
  padding: 1rem;
  border-radius: 12px;
  font-family: inherit;
  resize: none;
  height: 80px;
  outline: none;
  &:focus { border-color: ${({ theme }) => theme.colors.primary}; }
`;

const Controls = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
`;

const AttachButton = styled.label`
  background-color: ${({ theme }) => theme.colors.background};
  border: 1px dashed ${({ theme, hasFile }) => hasFile ? theme.colors.success : theme.colors.border};
  color: ${({ theme, hasFile }) => hasFile ? theme.colors.success : theme.colors.textMuted};
  padding: 0.5rem;
  border-radius: 8px;
  cursor: pointer;
  text-align: center;
  font-size: 0.85rem;
  transition: all 0.2s;

  &:hover { border-color: ${({ theme }) => theme.colors.primary}; color: ${({ theme }) => theme.colors.primary}; }
  input { display: none; }
`;

const SendButton = styled.button`
  background-color: ${({ theme }) => theme.colors.primary};
  color: #fff;
  border: none;
  height: 45px;
  padding: 0 1.5rem;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: opacity 0.2s;

  &:hover:not(:disabled) { opacity: 0.9; }
  &:disabled { opacity: 0.5; cursor: not-allowed; }
`;

export default function TicketDetailClient({ ticketId }) {
  const { showToast } = useToast();
  const [loading, setLoading] = useState(true);
  const [ticket, setTicket] = useState(null);

  // Reply State
  const [replyBody, setReplyBody] = useState('');
  const [attachment, setAttachment] = useState(null);
  const [sending, setSending] = useState(false);

  const messagesEndRef = useRef(null);

  // Auto scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchTicket = async () => {
    try {
      const res = await apiFetch(`/api/v1/support/tickets/${ticketId}/`);
      if (res.ok) {
        const data = await res.json();
        setTicket(data);
      } else {
        showToast('تیکت یافت نشد.', 'error');
      }
    } catch (error) {
      showToast('خطا در دریافت اطلاعات تیکت', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (ticketId) fetchTicket();
  }, [ticketId]);

  useEffect(() => {
    if (!loading) scrollToBottom();
  }, [loading, ticket?.messages?.length]);

  const handleReply = async (e) => {
    e.preventDefault();
    if (!replyBody.trim()) return;

    setSending(true);

    // چون فایل داریم، باید از FormData استفاده کنیم
    const formData = new FormData();
    formData.append('body', replyBody);
    if (attachment) {
      formData.append('attachment', attachment);
    }

    try {
      const res = await apiFetch(`/api/v1/support/tickets/${ticketId}/reply/`, {
        method: 'POST',
        // apiFetch باید از ارسال Content-Type خودداری کند تا مرورگر خودش boundary بسازد
        // در apiFetch باید شرط بگذاریم که اگر body از نوع FormData است، Content-Type ست نشود
        body: formData,
        isFormData: true // این یک فلگ سفارشی است که باید در apiFetch شما پشتیبانی شود
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || 'خطا در ارسال پیام');
      }

      setReplyBody('');
      setAttachment(null);
      fetchTicket(); // رفرش تیکت برای دیدن پیام جدید

    } catch (error) {
      showToast(error.message, 'error');
    } finally {
      setSending(false);
    }
  };

  if (loading) return <PageWrapper><h2 style={{ textAlign: 'center', padding: '4rem' }}>در حال بارگذاری گفتگو...</h2></PageWrapper>;
  if (!ticket) return <PageWrapper><h2>تیکت یافت نشد.</h2></PageWrapper>;

  const isClosed = ticket.status === 'closed' || ticket.status === 'resolved';

  return (
    <PageWrapper>
      <BackLink href="/accounts/tickets">➡️ بازگشت به لیست تیکت‌ها</BackLink>

      <TicketHeader>
        <TitleInfo>
          <h1>{ticket.subject}</h1>
          <span>کد پیگیری: {ticket.ticket_number} | دپارتمان: {ticket.category}</span>
        </TitleInfo>
        <StatusBadge status={ticket.status}>
          وضعیت: {ticket.status}
        </StatusBadge>
      </TicketHeader>

      <ChatBox>
        {ticket.messages && ticket.messages.map((msg) => {
          // مخفی کردن پیام‌های داخلی (Internal Notes) برای کاربر
          if (msg.is_internal_note) return null;

          return (
            <MessageBubbleWrapper key={msg.id} isStaff={msg.is_staff_reply}>
              <SenderName isStaff={msg.is_staff_reply}>
                {msg.is_staff_reply ? '🎧 پشتیبانی زیگما' : '👤 شما'}
              </SenderName>

              <BubbleContent isStaff={msg.is_staff_reply}>
                {msg.body}

                {msg.attachment && (
                  <AttachmentLink href={msg.attachment} target="_blank" rel="noopener noreferrer">
                    📎 دانلود فایل ضمیمه
                  </AttachmentLink>
                )}
              </BubbleContent>

              <MessageTime isStaff={msg.is_staff_reply}>
                {new Date(msg.created_at).toLocaleTimeString('fa-IR', { hour: '2-digit', minute: '2-digit' })} - {new Date(msg.created_at).toLocaleDateString('fa-IR')}
              </MessageTime>
            </MessageBubbleWrapper>
          );
        })}
        <div ref={messagesEndRef} />
      </ChatBox>

      {isClosed ? (
        <div style={{ backgroundColor: 'var(--surface)', padding: '1.5rem', textAlign: 'center', borderRadius: '0 0 16px 16px', color: 'var(--textMuted)' }}>
          این تیکت بسته شده است و امکان ارسال پیام جدید وجود ندارد. در صورت نیاز تیکت جدیدی ثبت کنید.
        </div>
      ) : (
        <ReplyForm onSubmit={handleReply}>
          <TextArea
            placeholder="پاسخ خود را اینجا بنویسید..."
            value={replyBody}
            onChange={(e) => setReplyBody(e.target.value)}
            disabled={sending}
          />
          <Controls>
            <AttachButton hasFile={!!attachment}>
              {attachment ? '✅ فایل انتخاب شد' : '📎 ضمیمه فایل'}
              <input
                type="file"
                onChange={(e) => setAttachment(e.target.files[0])}
                disabled={sending}
              />
            </AttachButton>

            <SendButton type="submit" disabled={sending || !replyBody.trim()}>
              {sending ? '...' : 'ارسال پیام ✈️'}
            </SendButton>
          </Controls>
        </ReplyForm>
      )}
    </PageWrapper>
  );
}