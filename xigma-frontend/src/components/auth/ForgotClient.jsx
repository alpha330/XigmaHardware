// src/components/auth/ForgotClient.jsx
'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  AuthContainer, AuthCard, AuthTitle, AuthSubtitle,
  InputGroup, Label, Input, SubmitButton, BottomLink
} from './AuthStyles'; // AlertMessage حذف شد
import Link from 'next/link';
import { useToast } from '../ui/ToastProvider';

export default function ForgotClient() {
  const router = useRouter();
  const [step, setStep] = useState(1); // 1: Request, 2: Confirm
  const { showToast } = useToast();
  const [identity, setIdentity] = useState(''); // email_or_mobile
  const [confirmData, setConfirmData] = useState({ code: '', new_password: '', new_password_confirm: '' });
  const [otpId, setOtpId] = useState(''); // دریافت شده از سرور در مرحله اول

  const [isLoading, setIsLoading] = useState(false); // ساده‌سازی State وضعیت

  // مرحله اول: درخواست بازیابی
  const handleRequest = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const res = await fetch('http://localhost:8000/api/v1/accounts/auth/password/reset/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email_or_mobile: identity })
      });
      const data = await res.json();

      if (!res.ok) throw new Error(data.detail || 'کاربری با این مشخصات یافت نشد.');

      setOtpId(data.otp_id || 'dummy_id');
      setStep(2);
      showToast('کد تایید برای شما ارسال شد.', 'success');

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
      const res = await fetch('http://localhost:8000/api/v1/accounts/auth/password/reset/confirm/', {
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
      if (!res.ok) throw new Error(data.detail || 'کد وارد شده اشتباه است یا منقضی شده.');

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
          {step === 1 ? 'ایمیل یا شماره موبایل خود را وارد کنید.' : 'کد تایید ارسال شده و رمز عبور جدید را وارد کنید.'}
        </AuthSubtitle>

        {step === 1 ? (
          <form onSubmit={handleRequest}>
            <InputGroup>
              <Label>ایمیل یا موبایل</Label>
              <Input
                type="text"
                dir="ltr"
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
                value={confirmData.code}
                onChange={(e) => setConfirmData({ ...confirmData, code: e.target.value })}
                required
              />
            </InputGroup>
            <InputGroup>
              <Label>رمز عبور جدید</Label>
              <Input
                type="password"
                dir="ltr"
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
                value={confirmData.new_password_confirm}
                onChange={(e) => setConfirmData({ ...confirmData, new_password_confirm: e.target.value })}
                required
              />
            </InputGroup>
            <SubmitButton type="submit" disabled={isLoading}>
              {isLoading ? 'در حال پردازش...' : 'تغییر رمز عبور'}
            </SubmitButton>
          </form>
        )}

        <BottomLink>
          <Link href="/auth/login">بازگشت به صفحه ورود</Link>
        </BottomLink>
      </AuthCard>
    </AuthContainer>
  );
}