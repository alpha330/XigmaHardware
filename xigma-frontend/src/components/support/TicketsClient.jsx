// src/components/support/TicketsClient.jsx
'use client';

import React, { useState, useEffect } from 'react';
import styled from '@emotion/styled';
import Link from 'next/link';
import { apiFetch } from '../../utils/apiFetch';
import { useToast } from '../ui/ToastProvider';

// ================= STYLES =================
const PageWrapper = styled.div`
  max-width: 1000px;
  margin: 2rem auto;
  padding: 0 2rem;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid ${({ theme }) => theme.colors.border};

  @media (max-width: 600px) {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
`;

const Title = styled.h1`
  font-size: 1.6rem;
  color: ${({ theme }) => theme.colors.textMain};
  display: flex;
  align-items: center;
  gap: 0.8rem;
`;

const CreateBtn = styled.button`
  background-color: ${({ theme }) => theme.colors.primary};
  color: #fff;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s;

  &:hover { background-color: ${({ theme }) => theme.colors.secondary}; }
`;

// --- List Styles ---
const TicketList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const TicketCard = styled(Link)`
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 12px;
  padding: 1.5rem;
  text-decoration: none;
  transition: all 0.2s;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
    border-color: ${({ theme }) => theme.colors.primary}50;
  }

  @media (max-width: 600px) {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
`;

const TicketInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
`;

const TicketSubject = styled.h3`
  font-size: 1.1rem;
  color: ${({ theme }) => theme.colors.textMain};
  margin: 0;
`;

const TicketMeta = styled.div`
  font-size: 0.85rem;
  color: ${({ theme }) => theme.colors.textMuted};
  display: flex;
  gap: 1rem;
  align-items: center;

  .id { font-family: monospace; font-weight: bold; color: ${({ theme }) => theme.colors.primary}; }
`;

const StatusBadge = styled.span`
  font-size: 0.8rem;
  padding: 0.4rem 1rem;
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

// --- Form Modal Styles ---
const ModalOverlay = styled.div`
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.6); display: flex; align-items: center; justify-content: center;
  z-index: 1000; padding: 1rem;
`;

const ModalContent = styled.div`
  background-color: ${({ theme }) => theme.colors.surface};
  border-radius: 16px; width: 100%; max-width: 600px;
  padding: 2rem; max-height: 90vh; overflow-y: auto;
`;

const FormGroup = styled.div`
  display: flex; flex-direction: column; gap: 0.5rem; margin-bottom: 1rem;

  label { font-weight: bold; font-size: 0.9rem; color: ${({ theme }) => theme.colors.textMain}; }
  input, select, textarea {
    padding: 0.8rem; border-radius: 8px; border: 1px solid ${({ theme }) => theme.colors.border};
    background-color: ${({ theme }) => theme.colors.background}; color: ${({ theme }) => theme.colors.textMain};
    font-family: inherit; outline: none;
    &:focus { border-color: ${({ theme }) => theme.colors.primary}; }
  }
  textarea { min-height: 120px; resize: vertical; }
`;

const ModalActions = styled.div`
  display: flex; gap: 1rem; margin-top: 2rem;

  button {
    flex: 1; padding: 1rem; border-radius: 8px; font-weight: bold; cursor: pointer; border: none;
    &.cancel { background-color: ${({ theme }) => theme.colors.background}; color: ${({ theme }) => theme.colors.textMain}; border: 1px solid ${({ theme }) => theme.colors.border}; }
    &.submit { background-color: ${({ theme }) => theme.colors.primary}; color: #fff; }
    &:disabled { opacity: 0.6; cursor: not-allowed; }
  }
`;

const dict = {
  status: {
    open: 'باز',
    in_progress: 'در حال بررسی',
    waiting_customer: 'منتظر پاسخ شما',
    resolved: 'حل شده',
    closed: 'بسته شده'
  },
  priority: {
    low: 'کم',
    medium: 'متوسط',
    high: 'زیاد',
    urgent: 'فوری'
  },
  category: {
    order: 'پیگیری سفارش',
    payment: 'امور مالی و پرداخت',
    product: 'مشاوره محصول',
    warranty: 'گارانتی و خدمات',
    technical: 'پشتیبانی فنی',
    other: 'سایر موارد'
  }
};

export default function TicketsClient() {
  const { showToast } = useToast();
  const [loading, setLoading] = useState(true);
  const [tickets, setTickets] = useState([]);

  const [showModal, setShowModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    subject: '', category: 'other', priority: 'medium', body: ''
  });

  const fetchTickets = async () => {
    try {
      const res = await apiFetch('/api/v1/support/tickets/my_tickets/');
      if (res.ok) {
        const data = await res.json();
        setTickets(data.results || data);
      }
    } catch (error) {
      showToast('خطا در دریافت لیست تیکت‌ها', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchTickets();
  }, [showToast]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.subject || !formData.body) return showToast('لطفا عنوان و متن را وارد کنید', 'error');

    setSubmitting(true);
    try {
      const res = await apiFetch('/api/v1/support/tickets/', {
        method: 'POST',
        body: JSON.stringify(formData)
      });

      const data = await res.json();

      if (!res.ok) {
        // 🎯 این بخش تغییر کرده تا ارورهای DRF را دقیقاً استخراج کند
        console.error("Backend Validation Error:", data);

        // استخراج پیام خطای جنگو
        let errorMsg = 'خطا در ثبت تیکت';
        if (data.error) errorMsg = data.error;
        else if (data.detail) errorMsg = data.detail;
        else if (typeof data === 'object') {
          // تبدیل آبجکت ارورهای جنگو به یک متن قابل خواندن
          errorMsg = Object.entries(data)
            .map(([field, errors]) => `${field}: ${Array.isArray(errors) ? errors[0] : errors}`)
            .join(' | ');
        }

        throw new Error(errorMsg);
      }

      showToast('تیکت شما با موفقیت ثبت شد.', 'success');
      setShowModal(false);
      setFormData({ subject: '', category: 'other', priority: 'medium', body: '' });
      fetchTickets();
    } catch (error) {
      showToast(error.message, 'error');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <PageWrapper><h2 style={{ textAlign: 'center', padding: '4rem' }}>در حال بارگذاری تیکت‌ها...</h2></PageWrapper>;

  return (
    <PageWrapper>
      <Header>
        <Title>🎧 پشتیبانی و تیکت‌ها</Title>
        <CreateBtn onClick={() => setShowModal(true)}>➕ ارسال تیکت جدید</CreateBtn>
      </Header>

      {tickets.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '4rem 0', color: 'var(--textMuted)' }}>
          <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>💬</div>
          <h3>شما تاکنون هیچ تیکتی ثبت نکرده‌اید.</h3>
          <p>در صورت بروز هرگونه مشکل یا سوال، پشتیبانان ما آماده پاسخگویی هستند.</p>
        </div>
      ) : (
        <TicketList>
          {tickets.map(ticket => (
            <TicketCard key={ticket.id} href={`/accounts/tickets/${ticket.id}`}>
              <TicketInfo>
                <TicketSubject>{ticket.subject}</TicketSubject>
                <TicketMeta>
                  <span className="id">{ticket.ticket_number}</span>
                  <span>|</span>
                  <span>{dict.category[ticket.category] || ticket.category}</span>
                  <span>|</span>
                  <span>بروزرسانی: {new Date(ticket.updated_at).toLocaleDateString('fa-IR')}</span>
                </TicketMeta>
              </TicketInfo>
              <StatusBadge status={ticket.status}>
                {dict.status[ticket.status] || ticket.status}
              </StatusBadge>
            </TicketCard>
          ))}
        </TicketList>
      )}

      {/* Modal ثبت تیکت جدید */}
      {showModal && (
        <ModalOverlay onClick={(e) => { if(e.target === e.currentTarget) setShowModal(false); }}>
          <ModalContent>
            <h2 style={{ marginBottom: '1.5rem', color: 'var(--textMain)' }}>ارسال تیکت پشتیبانی</h2>
            <form onSubmit={handleSubmit}>
              <FormGroup>
                <label>موضوع (عنوان)</label>
                <input
                  required
                  value={formData.subject}
                  onChange={e => setFormData({...formData, subject: e.target.value})}
                  placeholder="مثال: پیگیری تاخیر در ارسال سفارش"
                />
              </FormGroup>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <FormGroup>
                  <label>دپارتمان مربوطه</label>
                  <select value={formData.category} onChange={e => setFormData({...formData, category: e.target.value})}>
                    <option value="order">پیگیری سفارش</option>
                    <option value="payment">امور مالی</option>
                    <option value="technical">پشتیبانی فنی</option>
                    <option value="warranty">گارانتی</option>
                    <option value="other">سایر موارد</option>
                  </select>
                </FormGroup>

                <FormGroup>
                  <label>اولویت</label>
                  <select value={formData.priority} onChange={e => setFormData({...formData, priority: e.target.value})}>
                    <option value="low">کم</option>
                    <option value="medium">متوسط</option>
                    <option value="high">زیاد</option>
                    <option value="urgent">فوری</option>
                  </select>
                </FormGroup>
              </div>

              <FormGroup>
                <label>متن پیام</label>
                <textarea
                  required
                  value={formData.body}
                  onChange={e => setFormData({...formData, body: e.target.value})}
                  placeholder="مشکل یا سوال خود را با جزئیات بنویسید..."
                />
              </FormGroup>

              <ModalActions>
                <button type="button" className="cancel" onClick={() => setShowModal(false)}>انصراف</button>
                <button type="submit" className="submit" disabled={submitting}>
                  {submitting ? 'در حال ارسال...' : 'ارسال تیکت'}
                </button>
              </ModalActions>
            </form>
          </ModalContent>
        </ModalOverlay>
      )}
    </PageWrapper>
  );
}