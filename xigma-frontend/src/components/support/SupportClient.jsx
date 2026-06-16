// src/components/support/SupportClient.jsx
'use client';

import React, { useState, useEffect } from 'react';
import styled from '@emotion/styled';
import Link from 'next/link';
import { apiFetch } from '../../utils/apiFetch';
import { useToast } from '../ui/ToastProvider';

// ================= STYLES =================
const PageWrapper = styled.div`
  max-width: 1100px;
  margin: 0 auto;
  padding: 2rem;
`;

// --- Hero & Search ---
const HeroSection = styled.div`
  background: linear-gradient(135deg, ${({ theme }) => theme.colors.primary}15 0%, ${({ theme }) => theme.colors.secondary}15 100%);
  border-radius: 24px;
  padding: 4rem 2rem;
  text-align: center;
  margin-bottom: 3rem;
`;

const Title = styled.h1`
  font-size: 2.5rem;
  color: ${({ theme }) => theme.colors.textMain};
  margin-bottom: 1rem;
`;

const Subtitle = styled.p`
  font-size: 1.1rem;
  color: ${({ theme }) => theme.colors.textMuted};
  margin-bottom: 2rem;
`;

// --- Quick Actions (NEW) ---
const QuickActionsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 4rem;
`;

const ActionCard = styled.div`
  background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 16px;
  padding: 2rem;
  text-align: center;
  box-shadow: 0 4px 15px rgba(0,0,0,0.02);
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: transform 0.2s;

  &:hover { transform: translateY(-5px); border-color: ${({ theme }) => theme.colors.primary}50; }

  .icon { font-size: 3rem; margin-bottom: 1rem; }
  h3 { color: ${({ theme }) => theme.colors.textMain}; margin-bottom: 0.5rem; font-size: 1.2rem; }
  p { color: ${({ theme }) => theme.colors.textMuted}; font-size: 0.9rem; margin-bottom: 1.5rem; line-height: 1.6; flex: 1; }

  button, a {
    width: 100%; padding: 0.8rem; border-radius: 8px; font-weight: bold; cursor: pointer; border: none; text-decoration: none;
    &.primary { background-color: ${({ theme }) => theme.colors.primary}; color: #fff; }
    &.secondary { background-color: ${({ theme }) => theme.colors.background}; border: 1px solid ${({ theme }) => theme.colors.border}; color: ${({ theme }) => theme.colors.textMain}; }
  }
`;

// --- Warranty Form Styles ---
const WarrantyInput = styled.div`
  display: flex; width: 100%; border: 1px solid ${({ theme }) => theme.colors.border}; border-radius: 8px; overflow: hidden; margin-bottom: 1rem;
  input { flex: 1; border: none; padding: 0.8rem; outline: none; background: ${({ theme }) => theme.colors.background}; color: ${({ theme }) => theme.colors.textMain}; font-family: monospace; text-align: center; }
  button { width: 40px; border-radius: 0; background-color: ${({ theme }) => theme.colors.primary}; color: white; display: flex; align-items: center; justify-content: center; }
`;

const WarrantyResult = styled.div`
  background-color: ${({ theme, status }) => status === 'active' ? `${theme.colors.success}15` : `${theme.colors.error}15`};
  color: ${({ theme, status }) => status === 'active' ? theme.colors.success : theme.colors.error};
  padding: 0.8rem; border-radius: 8px; font-size: 0.85rem; font-weight: bold; width: 100%; margin-bottom: 1rem;
`;

// --- FAQ Styles ---
const FAQHeader = styled.h2`
  text-align: center; color: ${({ theme }) => theme.colors.textMain}; margin-bottom: 2rem; font-size: 1.8rem;
`;

const FAQList = styled.div`
  display: flex; flex-direction: column; gap: 1rem; max-width: 800px; margin: 0 auto;
`;

const FAQItem = styled.div`
  background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme, isOpen }) => isOpen ? theme.colors.primary : theme.colors.border};
  border-radius: 12px; overflow: hidden; transition: border-color 0.2s;
`;

const FAQQuestion = styled.button`
  width: 100%; text-align: right; padding: 1.5rem; background: none; border: none; font-size: 1.1rem; font-weight: bold;
  color: ${({ theme, isOpen }) => isOpen ? theme.colors.primary : theme.colors.textMain};
  display: flex; justify-content: space-between; align-items: center; cursor: pointer; font-family: inherit;
  .icon { font-size: 1.5rem; transition: transform 0.3s; transform: ${({ isOpen }) => isOpen ? 'rotate(180deg)' : 'rotate(0)'}; }
`;

const FAQAnswer = styled.div`
  padding: 0 1.5rem 1.5rem 1.5rem; color: ${({ theme }) => theme.colors.textMuted}; line-height: 1.8; font-size: 0.95rem;
  display: ${({ isOpen }) => isOpen ? 'block' : 'none'}; border-top: 1px dashed ${({ theme }) => theme.colors.border}; margin-top: 0.5rem; padding-top: 1rem;
`;

export default function SupportClient() {
  const { showToast } = useToast();
  const [faqs, setFaqs] = useState([]);
  const [openFaqId, setOpenFaqId] = useState(null);

  // Warranty State
  const [serial, setSerial] = useState('');
  const [warrantyLoading, setWarrantyLoading] = useState(false);
  const [warrantyResult, setWarrantyResult] = useState(null); // { found: true/false, status: 'active', ... }

  useEffect(() => {
    apiFetch('/api/v1/support/faqs/')
      .then(res => res.json())
      .then(data => setFaqs(data.results || data))
      .catch(err => console.error(err));
  }, []);

  const handleCheckWarranty = async (e) => {
    e.preventDefault();
    if (!serial.trim()) return showToast('شماره سریال را وارد کنید', 'warning');

    setWarrantyLoading(true);
    setWarrantyResult(null);
    try {
      const res = await apiFetch(`/api/v1/support/warranties/check/?serial=${serial}`);
      const data = await res.json();

      if (res.ok && data.id) {
        setWarrantyResult({ found: true, ...data });
      } else {
        setWarrantyResult({ found: false, message: data.message || 'گارانتی با این شماره یافت نشد.' });
      }
    } catch (error) {
      showToast('خطا در ارتباط با سرور', 'error');
    } finally {
      setWarrantyLoading(false);
    }
  };

  const triggerLiveChat = () => {
    window.dispatchEvent(new Event('open-live-chat'));
    const chatWidgetBtn = document.getElementById('chat-toggle-btn');
    if (chatWidgetBtn) {
      chatWidgetBtn.click();
    }
  };

  return (
    <PageWrapper>
      <HeroSection>
        <Title>مرکز پشتیبانی زیگما سخت‌افزار</Title>
        <Subtitle>چگونه می‌توانیم به شما کمک کنیم؟ ما همیشه در کنار شما هستیم.</Subtitle>
      </HeroSection>

      <QuickActionsGrid>
        {/* ۱. بررسی گارانتی */}
        <ActionCard>
          <span className="icon">🛡️</span>
          <h3>استعلام گارانتی</h3>
          <p>شماره سریال کالا را وارد کنید تا از وضعیت گارانتی و اعتبار آن مطلع شوید.</p>

          <form onSubmit={handleCheckWarranty} style={{ width: '100%' }}>
            <WarrantyInput>
              <input
                placeholder="SN-XXXXXXX"
                value={serial}
                onChange={(e) => setSerial(e.target.value)}
              />
              <button type="submit" disabled={warrantyLoading}>
                {warrantyLoading ? '...' : '🔍'}
              </button>
            </WarrantyInput>
          </form>

          {warrantyResult && (
            <WarrantyResult status={warrantyResult.found && warrantyResult.is_active ? 'active' : 'inactive'}>
              {warrantyResult.found
                ? `اعتبار گارانتی تا: ${new Date(warrantyResult.end_date).toLocaleDateString('fa-IR')} (${warrantyResult.is_active ? 'فعال' : 'منقضی شده'})`
                : warrantyResult.message}
            </WarrantyResult>
          )}
        </ActionCard>

        {/* ۲. چت آنلاین */}
        <ActionCard>
          <span className="icon">💬</span>
          <h3>چت آنلاین با کارشناسان</h3>
          <p>برای مشاوره خرید یا دریافت راهنمایی فوری، مستقیماً با کارشناسان ما گفتگو کنید.</p>
          <button className="primary" onClick={triggerLiveChat}>شروع گفتگو ⚡</button>
        </ActionCard>

        {/* ۳. ثبت تیکت */}
        <ActionCard>
          <span className="icon">📝</span>
          <h3>ثبت تیکت پشتیبانی</h3>
          <p>برای پیگیری سفارشات، امور مالی و مشکلات فنی، یک تیکت ثبت کنید تا بررسی شود.</p>
          <Link href="/accounts/tickets" className="secondary" style={{ display: 'block', textAlign: 'center' }}>
            ورود به پنل تیکت‌ها
          </Link>
        </ActionCard>
      </QuickActionsGrid>

      {/* بخش سوالات متداول */}
      <FAQHeader>پاسخ پرسش‌های پر تکرار</FAQHeader>
      <FAQList>
        {faqs.map(faq => (
          <FAQItem key={faq.id} isOpen={openFaqId === faq.id}>
            <FAQQuestion isOpen={openFaqId === faq.id} onClick={() => setOpenFaqId(openFaqId === faq.id ? null : faq.id)}>
              {faq.question}
              <span className="icon">⬇</span>
            </FAQQuestion>
            <FAQAnswer isOpen={openFaqId === faq.id}>
              {faq.answer}
            </FAQAnswer>
          </FAQItem>
        ))}
      </FAQList>

    </PageWrapper>
  );
}