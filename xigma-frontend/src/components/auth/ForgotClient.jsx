// src/components/auth/ForgotClient.jsx
'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  AuthContainer, AuthCard, AuthTitle, AuthSubtitle,
  InputGroup, Label, Input, SubmitButton, SecondaryButton, BottomLink
} from './AuthStyles';
import Link from 'next/link';
import { useToast } from '../ui/ToastProvider';
import { apiFetch } from '../../utils/apiFetch';

export default function ForgotClient() {
  const router = useRouter();
  const [step, setStep] = useState(1); // 1: Request, 2: Confirm
  const { showToast } = useToast();
  const [identity, setIdentity] = useState(''); // email_or_mobile
  const [confirmData, setConfirmData] = useState({ code: '', new_password: '', new_password_confirm: '' });
  const [otpId, setOtpId] = useState('');
  const [deliveryChannel, setDeliveryChannel] = useState('');

  const [isLoading, setIsLoading] = useState(false);

  // مرحله اول: درخواست بازیابی
  const handleRequest = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const trimmedIdentity = identity.trim();
      const normalizedIdentity = trimmedIdentity.includes('@') ? trimmedIdentity.toLowerCase() : trimmedIdentity;
      const res = await apiFetch('/api/v1/accounts/auth/password/reset/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email_or_mobile: normalizedIdentity })
      });
      const data = await res.json();

      if (!res.ok) throw new Error(data.error || data.detail || Object.values(data)[0] || 'ارسال کد بازیابی انجام نشد.');

      if (!data.otp_id) {
        showToast('اگر حسابی با این مشخصات وجود داشته باشد، کد بازیابی برای آن ارسال می‌شود.', 'success');
        return;
      }

      const resolvedChannel = data.delivery_channel || (normalizedIdentity.includes('@') ? 'email' : 'sms');
      setIdentity(normalizedIdentity);
      setOtpId(data.otp_id);
      setDeliveryChannel(resolvedChannel);
      setStep(2);
      showToast(
        resolvedChannel === 'email'
          ? 'کد بازیابی به ایمیل شما ارسال شد.'
          : 'کد بازیابی به موبایل شما ارسال شد.',
        'success'
      );

    } catch (error) {
      showToast(error.message, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  // مرحله دوم: تایید کد و رمز جدید
  const handleConfirm = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    if (confirmData.new_password !== confirmData.new_password_confirm) {
      showToast('رمز عبور و تکرار آن یکسان نیستند.', 'error');
      setIsLoading(false);
      return;
    }

    try {
      const res = await apiFetch('/api/v1/accounts/auth/password/reset/confirm/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email_or_mobile: identity,
          new_password: confirmData.new_password,
          new_password_confirm: confirmData.new_password_confirm,
          otp_id: otpId,
          code: confirmData.code
        })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.error || data.detail || Object.values(data)[0] || 'کد وارد شده اشتباه است یا منقضی شده.');

      showToast('رمز عبور با موفقیت تغییر کرد!', 'success');
      setTimeout(() => router.push('/auth/login'), 2000);

    } catch (error) {
      showToast(error.message, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthContainer>
      <AuthCard>
        <AuthTitle>بازیابی رمز عبور</AuthTitle>
        <AuthSubtitle>
          {step === 1
            ? 'ایمیل یا شماره موبایل حساب خود را وارد کنید.'
            : `کد شش‌رقمی ارسال‌شده به ${deliveryChannel === 'email' ? 'ایمیل' : 'موبایل'} را همراه رمز جدید وارد کنید.`}
        </AuthSubtitle>

        {step === 1 ? (
          <form onSubmit={handleRequest}>
            <InputGroup>
              <Label>ایمیل یا موبایل</Label>
              <Input
                type="text"
                dir="ltr"
                autoComplete="username"
                value={identity}
                onChange={(e) => setIdentity(e.target.value)}
                required
              />
            </InputGroup>
            <SubmitButton type="submit" disabled={isLoading}>
              {isLoading ? 'در حال ارسال...' : 'ارسال کد تایید'}
            </SubmitButton>
          </form>
        ) : (
          <form onSubmit={handleConfirm}>
            <InputGroup>
              <Label>کد تایید (OTP)</Label>
              <Input
                type="text"
                dir="ltr"
                inputMode="numeric"
                autoComplete="one-time-code"
                pattern="[0-9]{6}"
                minLength={6}
                maxLength={6}
                placeholder="------"
                value={confirmData.code}
                onChange={(e) => setConfirmData({ ...confirmData, code: e.target.value.replace(/\D/g, '').slice(0, 6) })}
                required
              />
            </InputGroup>
            <InputGroup>
              <Label>رمز عبور جدید</Label>
              <Input
                type="password"
                dir="ltr"
                autoComplete="new-password"
                value={confirmData.new_password}
                onChange={(e) => setConfirmData({ ...confirmData, new_password: e.target.value })}
                required
              />
            </InputGroup>
            <InputGroup>
              <Label>تکرار رمز عبور جدید</Label>
              <Input
                type="password"
                dir="ltr"
                autoComplete="new-password"
                value={confirmData.new_password_confirm}
                onChange={(e) => setConfirmData({ ...confirmData, new_password_confirm: e.target.value })}
                required
              />
            </InputGroup>
            <SubmitButton type="submit" disabled={isLoading}>
              {isLoading ? 'در حال پردازش...' : 'تغییر رمز عبور'}
            </SubmitButton>
            <SecondaryButton
              type="button"
              onClick={() => {
                setStep(1);
                setOtpId('');
                setConfirmData({ code: '', new_password: '', new_password_confirm: '' });
              }}
            >
              اصلاح ایمیل یا شماره موبایل
            </SecondaryButton>
          </form>
        )}

        <BottomLink>
          <Link href="/auth/login">بازگشت به صفحه ورود</Link>
        </BottomLink>
      </AuthCard>
    </AuthContainer>
  );
}
