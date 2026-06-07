// src/app/auth/forgot-password/page.js
'use client';

import { useState } from 'react';
import styled from '@emotion/styled';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

const PageWrapper = styled.div`
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg,
    ${props => props.theme.colors.bg.dark} 0%,
    ${props => props.theme.colors.primary[900]} 100%
  );
  padding: 2rem;
`;

const Card = styled.div`
  width: 100%;
  max-width: 440px;
  background: white;
  border-radius: ${props => props.theme.borderRadius.xl};
  padding: 2.5rem;
  box-shadow: ${props => props.theme.shadows.xl};
  animation: slideUp 0.5s ease-out;
  text-align: center;
`;

const Icon = styled.div`
  font-size: 3rem;
  margin-bottom: 1rem;
`;

const Title = styled.h1`
  font-size: ${props => props.theme.fontSizes['2xl']};
  font-weight: 700;
  margin-bottom: 0.5rem;
`;

const Description = styled.p`
  color: ${props => props.theme.colors.text.muted};
  font-size: ${props => props.theme.fontSizes.sm};
  margin-bottom: 2rem;
  line-height: 1.8;
`;

export default function ForgotPasswordPage() {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [emailOrMobile, setEmailOrMobile] = useState('');
  const [otpCode, setOtpCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleRequestReset = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/v1/accounts/auth/password/reset/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email_or_mobile: emailOrMobile }),
      });

      if (response.ok) {
        setSuccess('لینک/کد بازیابی ارسال شد.');
        setStep(2);
      } else {
        setError('خطا در ارسال درخواست.');
      }
    } catch (err) {
      setError('خطا در ارتباط با سرور.');
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/v1/accounts/auth/password/reset/confirm/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email_or_mobile: emailOrMobile,
          code: otpCode,
          new_password: newPassword,
          new_password_confirm: newPassword,
        }),
      });

      if (response.ok) {
        setSuccess('رمز عبور با موفقیت تغییر کرد!');
        setTimeout(() => {
          window.location.href = '/auth/login';
        }, 1500);
      } else {
        setError('کد نامعتبر است.');
      }
    } catch (err) {
      setError('خطا در ارتباط با سرور.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <PageWrapper>
      <Card>
        {step === 1 ? (
          <>
            <Icon>🔑</Icon>
            <Title>فراموشی رمز عبور</Title>
            <Description>
              ایمیل یا شماره موبایل خود را وارد کنید تا لینک بازیابی برای شما ارسال شود.
            </Description>

            {error && <div style={{ color: '#ef4444', marginBottom: '1rem', fontSize: '0.9rem' }}>{error}</div>}
            {success && <div style={{ color: '#10b981', marginBottom: '1rem', fontSize: '0.9rem' }}>{success}</div>}

            <form onSubmit={handleRequestReset}>
              <Input
                label="ایمیل یا موبایل"
                placeholder="example@email.com یا 09123456789"
                value={emailOrMobile}
                onChange={(e) => setEmailOrMobile(e.target.value)}
                icon="📧"
                ltr
              />

              <Button variant="primary" size="lg" fullWidth loading={loading} type="submit">
                📩 ارسال لینک بازیابی
              </Button>
            </form>
          </>
        ) : (
          <>
            <Icon>🔐</Icon>
            <Title>تغییر رمز عبور</Title>
            <Description>
              کد ارسال شده و رمز جدید را وارد کنید.
            </Description>

            {error && <div style={{ color: '#ef4444', marginBottom: '1rem' }}>{error}</div>}
            {success && <div style={{ color: '#10b981', marginBottom: '1rem' }}>{success}</div>}

            <form onSubmit={handleResetPassword}>
              <Input
                label="کد تایید"
                placeholder="کد ۶ رقمی"
                value={otpCode}
                onChange={(e) => setOtpCode(e.target.value)}
                icon="🔢"
                ltr
              />

              <Input
                label="رمز عبور جدید"
                type="password"
                placeholder="حداقل ۸ کاراکتر"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                icon="🔒"
              />

              <Button variant="primary" size="lg" fullWidth loading={loading} type="submit">
                ✅ تغییر رمز عبور
              </Button>
            </form>
          </>
        )}

        <div style={{ marginTop: '1.5rem', fontSize: '0.9rem' }}>
          <Link href="/auth/login" style={{ color: '#9333ea', fontWeight: 600 }}>
            ⬅️ بازگشت به صفحه ورود
          </Link>
        </div>
      </Card>
    </PageWrapper>
  );
}