// src/components/auth/LoginClient.jsx
'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Cookies from 'js-cookie';
import {
  AuthContainer, AuthCard, AuthTitle, AuthSubtitle, InputGroup,
  Label, Input, SubmitButton, BottomLink, Tabs, Tab
} from './AuthStyles';
import { useToast } from '../ui/ToastProvider';
import { apiFetch } from '../../utils/apiFetch';
import OTPInput from '../OTPInput/OTPInput';

export default function LoginClient() {
  const router = useRouter();
  const { showToast } = useToast();

  const [activeTab, setActiveTab] = useState('password'); // 'password' | 'otp'
  const [step, setStep] = useState(1); // 1: ورود هویت، 2: تایید OTP
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState({ email_or_mobile: '', password: '' });
  const [otpData, setOtpData] = useState({ otp_id: '', code: '' });

  // درخواست اولیه (یا ارسال کد OTP یا چک کردن رمز)
  const handleInitialSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const payload = activeTab === 'password'
      ? { email: formData.email_or_mobile, password: formData.password }
      : { mobile: formData.email_or_mobile }; // درخواست OTP

    try {
      const res = await apiFetch('/api/v1/accounts/auth/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      console.log(data)
      if (!res.ok) throw new Error(data.error || 'اطلاعات صحیح نیست.');

      if (activeTab === 'otp') {
        setOtpData({ ...otpData, otp_id: data.otp_id });
        setStep(2);
        showToast('کد تایید ارسال شد.', 'success');
      } else {
        saveTokens(data.tokens);
      }
    } catch (error) {
      showToast(error.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async (code) => {
    setLoading(true);
    try {
      const res = await apiFetch('/api/v1/accounts/auth/otp/verify/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            otp_id: otpData.otp_id,
            mobile: formData.email_or_mobile,
            code: code,
        })
      });
      console.log(otpData)
      const data = await res.json();

      if (!res.ok) throw new Error(data.error || 'کد نامعتبر است.');
      saveTokens(data.tokens);
    } catch (error) {
      showToast(error.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const saveTokens = (tokens) => {
    Cookies.set('token', tokens.access, { expires: 1 / 24, path: '/' });
    Cookies.set('refresh', tokens.refresh, { expires: 7, path: '/' });
    showToast('خوش آمدید!', 'success');
    setTimeout(() => router.push('/accounts/profile'), 1000);
  };

  return (
    <AuthContainer>
      <AuthCard>
        <AuthTitle>{step === 1 ? 'ورود به حساب' : 'تایید کد ورود'}</AuthTitle>

        {step === 1 && (
          <Tabs>
            <Tab active={activeTab === 'password'} onClick={() => setActiveTab('password')}>با رمز عبور</Tab>
            <Tab active={activeTab === 'otp'} onClick={() => setActiveTab('otp')}>با کد یکبار مصرف</Tab>
          </Tabs>
        )}

        {step === 1 ? (
          <form onSubmit={handleInitialSubmit}>
            <InputGroup>
              <Label>ایمیل یا موبایل</Label>
              <Input dir="ltr" value={formData.email_or_mobile}
                onChange={(e) => setFormData({ ...formData, email_or_mobile: e.target.value })} required />
            </InputGroup>

            {activeTab === 'password' && (
              <InputGroup>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Label>رمز عبور</Label>
                  <Link href="/auth/forgot-password" style={{ fontSize: '0.8rem', color: 'var(--primary)' }}>فراموشی رمز؟</Link>
                </div>
                <Input type="password" dir="ltr" value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })} required />
              </InputGroup>
            )}

            <SubmitButton type="submit" disabled={loading}>
              {loading ? 'در حال پردازش...' : (activeTab === 'password' ? 'ورود' : 'دریافت کد تایید')}
            </SubmitButton>
          </form>
        ) : (
          <OTPInput onComplete={handleVerifyOtp} resendOTP={() => handleInitialSubmit({ preventDefault: () => {} })} />
        )}

        <BottomLink>
          حساب ندارید؟ <Link href="/auth/register">ثبت‌نام کنید</Link>
        </BottomLink>
      </AuthCard>
    </AuthContainer>
  );
}