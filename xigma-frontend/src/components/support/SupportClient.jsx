// src/components/support/SupportClient.jsx
'use client';

import React, { useState } from 'react';
import styled from '@emotion/styled';
import Link from 'next/link';

const PageWrapper = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 4rem 2rem;
`;

const HeaderSection = styled.div`
  text-align: center;
  margin-bottom: 4rem;
`;

const Title = styled.h1`
  font-size: 2.5rem;
  font-weight: 900;
  color: ${({ theme }) => theme.colors.textMain};
  margin-bottom: 1rem;
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3rem;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const SectionBox = styled.div`
  background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 16px;
  padding: 2.5rem;
  height: fit-content;
`;

const SectionTitle = styled.h2`
  font-size: 1.5rem;
  color: ${({ theme }) => theme.colors.primary};
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

/* --- استایل‌های بخش استعلام گارانتی --- */
const InputGroup = styled.div`
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;

  @media (max-width: 500px) {
    flex-direction: column;
  }
`;

const SerialInput = styled.input`
  flex: 1;
  background-color: ${({ theme }) => theme.colors.background};
  border: 1px solid ${({ theme }) => theme.colors.border};
  color: ${({ theme }) => theme.colors.textMain};
  padding: 1rem;
  border-radius: 8px;
  font-family: inherit;
  outline: none;
  font-size: 1rem;

  &:focus {
    border-color: ${({ theme }) => theme.colors.primary};
    box-shadow: 0 0 0 3px ${({ theme }) => `${theme.colors.primary}33`};
  }
`;

const CheckBtn = styled.button`
  background-color: ${({ theme }) => theme.colors.primary};
  color: #fff;
  border: none;
  padding: 1rem 2rem;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background-color: ${({ theme }) => theme.colors.secondary};
  }

  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
`;

const WarrantyResult = styled.div`
  padding: 1.5rem;
  border-radius: 8px;
  background-color: ${({ theme, status }) =>
    status === 'valid' ? `${theme.colors.success}15` :
    status === 'invalid' ? `${theme.colors.error}15` : theme.colors.background};
  border: 1px solid ${({ theme, status }) =>
    status === 'valid' ? theme.colors.success :
    status === 'invalid' ? theme.colors.error : theme.colors.border};
  color: ${({ theme }) => theme.colors.textMain};
  margin-top: 1rem;
`;

/* --- استایل‌های بخش سوالات متداول (FAQ) --- */
const FaqItem = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.colors.border};
  padding: 1rem 0;

  &:last-child {
    border-bottom: none;
  }
`;

const FaqQuestion = styled.button`
  width: 100%;
  background: none;
  border: none;
  text-align: right;
  font-size: 1.1rem;
  font-weight: bold;
  color: ${({ theme }) => theme.colors.textMain};
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-family: inherit;
  padding: 0.5rem 0;
`;

const FaqAnswer = styled.div`
  color: ${({ theme }) => theme.colors.textMuted};
  line-height: 1.8;
  padding-top: 1rem;
  display: ${({ isOpen }) => (isOpen ? 'block' : 'none')};
  animation: fadeIn 0.3s ease-out;

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(-5px); }
    to { opacity: 1; transform: translateY(0); }
  }
`;

/* --- لینک‌های دسترسی سریع --- */
const QuickLinks = styled.div`
  display: flex;
  gap: 1rem;
  margin-top: 2rem;

  @media (max-width: 500px) {
    flex-direction: column;
  }
`;

const ActionLink = styled(Link)`
  flex: 1;
  text-align: center;
  padding: 1rem;
  border-radius: 8px;
  font-weight: bold;
  transition: all 0.2s ease;
  background-color: ${({ theme, primary }) => primary ? theme.colors.primary : 'transparent'};
  color: ${({ theme, primary }) => primary ? '#fff' : theme.colors.textMain};
  border: 1px solid ${({ theme, primary }) => primary ? theme.colors.primary : theme.colors.border};

  &:hover {
    background-color: ${({ theme, primary }) => primary ? theme.colors.secondary : theme.colors.background};
    transform: translateY(-2px);
  }
`;

export default function SupportClient({ faqs }) {
  const [openFaq, setOpenFaq] = useState(null);
  const [serial, setSerial] = useState('');
  const [warrantyStatus, setWarrantyStatus] = useState(null); // 'valid' | 'invalid' | null
  const [isChecking, setIsChecking] = useState(false);

  // تغییر وضعیت آکاردئون
  const toggleFaq = (index) => {
    setOpenFaq(openFaq === index ? null : index);
  };

  // بررسی وضعیت گارانتی
  const handleCheckWarranty = async () => {
    if (!serial.trim()) return;
    setIsChecking(true);
    setWarrantyStatus(null);

    try {
      const res = await fetch(`http://localhost:8000/api/v1/support/warranties/check/?serial=${serial}`);
      if (!res.ok) throw new Error();

      const data = await res.json();
      // بر اساس پاسخ واقعی بک‌اند شما این شرط تنظیم می‌شود
      if (data.is_valid || data.status === 'active') {
         setWarrantyStatus({ status: 'valid', message: `گارانتی دستگاه معتبر است. (انقضا: ${data.expire_date || 'نامشخص'})` });
      } else {
         setWarrantyStatus({ status: 'invalid', message: 'گارانتی این سریال نامعتبر یا منقضی شده است.' });
      }
    } catch (error) {
      // شبیه‌سازی برای زمان عدم اتصال بک‌اند
      setTimeout(() => {
        if (serial === '12345') {
          setWarrantyStatus({ status: 'valid', message: 'گارانتی دستگاه معتبر است. انقضا: 1404/08/12' });
        } else {
          setWarrantyStatus({ status: 'invalid', message: 'سریال وارد شده در سیستم یافت نشد.' });
        }
      }, 1000);
    } finally {
      setIsChecking(false);
    }
  };

  return (
    <PageWrapper>
      <HeaderSection>
        <Title>مرکز پشتیبانی مشتریان</Title>
        <p style={{ color: 'var(--textMuted)', fontSize: '1.1rem' }}>
          چگونه می‌توانیم به شما کمک کنیم؟
        </p>
      </HeaderSection>

      <Grid>
        {/* بخش راست: استعلام گارانتی و دسترسی سریع */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          <SectionBox>
            <SectionTitle>🛡️ استعلام اصالت و گارانتی</SectionTitle>
            <p style={{ color: 'var(--textMuted)', marginBottom: '1.5rem', lineHeight: '1.6' }}>
              برای اطمینان از اصالت کالای خریداری شده و اطلاع از وضعیت گارانتی، شماره سریال (S/N) درج شده روی جعبه یا بدنه دستگاه را وارد کنید.
            </p>
            <InputGroup>
              <SerialInput
                type="text"
                placeholder="مثال: SN-987654321"
                value={serial}
                onChange={(e) => setSerial(e.target.value)}
                dir="ltr"
              />
              <CheckBtn onClick={handleCheckWarranty} disabled={isChecking || !serial}>
                {isChecking ? 'در حال بررسی...' : 'بررسی سریال'}
              </CheckBtn>
            </InputGroup>

            {warrantyStatus && (
              <WarrantyResult status={warrantyStatus.status}>
                {warrantyStatus.status === 'valid' ? '✅ ' : '❌ '}
                {warrantyStatus.message}
              </WarrantyResult>
            )}
          </SectionBox>

          <SectionBox>
            <SectionTitle>🎧 نیاز به کمک بیشتر دارید؟</SectionTitle>
            <p style={{ color: 'var(--textMuted)', marginBottom: '1rem' }}>
              در صورتی که پاسخ خود را پیدا نکردید، می‌توانید به صورت آنلاین با کارشناسان ما در ارتباط باشید.
            </p>
            <QuickLinks>
              <ActionLink href="/support/tickets" primary="true">
                📝 ثبت تیکت پشتیبانی
              </ActionLink>
              <ActionLink href="/support/chat">
                💬 چت آنلاین با کارشناس
              </ActionLink>
            </QuickLinks>
          </SectionBox>
        </div>

        {/* بخش چپ: سوالات متداول */}
        <SectionBox>
          <SectionTitle>❓ سوالات متداول (FAQ)</SectionTitle>
          {faqs && faqs.length > 0 ? (
            faqs.map((faq, index) => (
              <FaqItem key={faq.id || index}>
                <FaqQuestion onClick={() => toggleFaq(index)}>
                  {faq.question}
                  <span>{openFaq === index ? '−' : '+'}</span>
                </FaqQuestion>
                <FaqAnswer isOpen={openFaq === index}>
                  {faq.answer}
                </FaqAnswer>
              </FaqItem>
            ))
          ) : (
            <p style={{ color: 'var(--textMuted)' }}>در حال حاضر سوالی ثبت نشده است.</p>
          )}
        </SectionBox>
      </Grid>
    </PageWrapper>
  );
}