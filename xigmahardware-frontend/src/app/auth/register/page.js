// src/app/auth/register/page.js
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

const RegisterCard = styled.div`
  width: 100%;
  max-width: 480px;
  background: white;
  border-radius: ${props => props.theme.borderRadius.xl};
  padding: 2.5rem;
  box-shadow: ${props => props.theme.shadows.xl};
  animation: slideUp 0.5s ease-out;
  max-height: 90vh;
  overflow-y: auto;
`;

const Logo = styled.div`
  width: 70px;
  height: 70px;
  background: linear-gradient(135deg,
    ${props => props.theme.colors.primary[500]},
    ${props => props.theme.colors.primary[700]}
  );
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  color: white;
  margin: 0 auto 1.5rem;
`;

const Title = styled.h1`
  font-size: ${props => props.theme.fontSizes['2xl']};
  font-weight: 700;
  text-align: center;
  margin-bottom: 0.5rem;
`;

const Subtitle = styled.p`
  text-align: center;
  color: ${props => props.theme.colors.text.muted};
  font-size: ${props => props.theme.fontSizes.sm};
  margin-bottom: 2rem;
`;

const StepsIndicator = styled.div`
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 2rem;
`;

const StepDot = styled.div`
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: ${props => props.$active
    ? props.theme.colors.primary[500]
    : props.theme.colors.gray[200]};
  transition: all ${props => props.theme.transitions.fast};
`;

const ErrorAlert = styled.div`
  background: ${props => props.theme.colors.danger}15;
  border: 1px solid ${props => props.theme.colors.danger}30;
  color: ${props => props.theme.colors.danger};
  padding: 12px 16px;
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: ${props => props.theme.fontSizes.sm};
  margin-bottom: 1rem;
  text-align: center;
`;

const SuccessAlert = styled.div`
  background: ${props => props.theme.colors.success}15;
  border: 1px solid ${props => props.theme.colors.success}30;
  color: ${props => props.theme.colors.success};
  padding: 12px 16px;
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: ${props => props.theme.fontSizes.sm};
  margin-bottom: 1rem;
  text-align: center;
`;

export default function RegisterPage() {
  const [step, setStep] = useState(1);
  const [method, setMethod] = useState('email');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [formData, setFormData] = useState({
    email: '',
    mobile: '',
    password: '',
    passwordConfirm: '',
    firstName: '',
    lastName: '',
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError('');
  };

  const handleNextStep = (e) => {
    e.preventDefault();
    if (step === 1) {
      if (method === 'email' && !formData.email) {
        setError('ایمیل الزامی است.');
        return;
      }
      if (method === 'mobile' && !formData.mobile) {
        setError('شماره موبایل الزامی است.');
        return;
      }
      setStep(2);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();

    if (formData.password !== formData.passwordConfirm) {
      setError('رمز عبور و تکرار آن مطابقت ندارند.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const endpoint = method === 'email'
        ? 'http://localhost:8000/api/v1/accounts/auth/register/email/'
        : 'http://localhost:8000/api/v1/accounts/auth/register/mobile/';

      const body = method === 'email'
        ? {
            email: formData.email,
            password: formData.password,
            password_confirm: formData.passwordConfirm,
            first_name: formData.firstName,
            last_name: formData.lastName,
          }
        : {
            mobile: formData.mobile,
            password: formData.password,
            first_name: formData.firstName,
            last_name: formData.lastName,
          };

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess('ثبت‌نام با موفقیت انجام شد!');
        localStorage.setItem('access_token', data.tokens.access);
        localStorage.setItem('refresh_token', data.tokens.refresh);

        setTimeout(() => {
          window.location.href = '/dashboard';
        }, 1500);
      } else {
        setError(data.error || Object.values(data).flat().join(', '));
      }
    } catch (err) {
      setError('خطا در ارتباط با سرور.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <PageWrapper>
      <RegisterCard>
        <Logo>🛒</Logo>
        <Title>ثبت‌نام در XigmaHardware</Title>
        <Subtitle>به خانواده بزرگ XigmaHardware بپیوندید</Subtitle>

        <StepsIndicator>
          <StepDot $active={step >= 1} />
          <StepDot $active={step >= 2} />
        </StepsIndicator>

        {error && <ErrorAlert>{error}</ErrorAlert>}
        {success && <SuccessAlert>{success}</SuccessAlert>}

        {step === 1 ? (
          <form onSubmit={handleNextStep}>
            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem' }}>
              <Button
                variant={method === 'email' ? 'primary' : 'secondary'}
                size="sm"
                fullWidth
                onClick={() => setMethod('email')}
                type="button"
              >
                📧 ایمیل
              </Button>
              <Button
                variant={method === 'mobile' ? 'primary' : 'secondary'}
                size="sm"
                fullWidth
                onClick={() => setMethod('mobile')}
                type="button"
              >
                📱 موبایل
              </Button>
            </div>

            {method === 'email' ? (
              <Input
                label="ایمیل"
                type="email"
                name="email"
                placeholder="example@email.com"
                value={formData.email}
                onChange={handleChange}
                icon="📧"
                ltr
              />
            ) : (
              <Input
                label="شماره موبایل"
                type="tel"
                name="mobile"
                placeholder="09123456789"
                value={formData.mobile}
                onChange={handleChange}
                icon="📱"
                ltr
              />
            )}

            <Button variant="primary" size="lg" fullWidth type="submit">
              ➡️ ادامه
            </Button>
          </form>
        ) : (
          <form onSubmit={handleRegister}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <Input
                label="نام"
                name="firstName"
                placeholder="نام"
                value={formData.firstName}
                onChange={handleChange}
              />
              <Input
                label="نام خانوادگی"
                name="lastName"
                placeholder="نام خانوادگی"
                value={formData.lastName}
                onChange={handleChange}
              />
            </div>

            <Input
              label="رمز عبور"
              type="password"
              name="password"
              placeholder="حداقل ۸ کاراکتر"
              value={formData.password}
              onChange={handleChange}
              icon="🔒"
            />

            <Input
              label="تکرار رمز عبور"
              type="password"
              name="passwordConfirm"
              placeholder="تکرار رمز عبور"
              value={formData.passwordConfirm}
              onChange={handleChange}
              icon="🔒"
            />

            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <Button
                variant="secondary"
                size="lg"
                fullWidth
                onClick={() => setStep(1)}
                type="button"
              >
                ⬅️ بازگشت
              </Button>
              <Button
                variant="primary"
                size="lg"
                fullWidth
                loading={loading}
                type="submit"
              >
                ✅ ثبت‌نام
              </Button>
            </div>
          </form>
        )}

        <div style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.9rem' }}>
          قبلاً ثبت‌نام کرده‌اید؟{' '}
          <Link href="/auth/login" style={{ color: '#9333ea', fontWeight: 600 }}>
            ورود به حساب
          </Link>
        </div>
      </RegisterCard>
    </PageWrapper>
  );
}