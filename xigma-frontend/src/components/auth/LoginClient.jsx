// src/components/auth/LoginClient.jsx
'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { AuthContainer, AuthCard, AuthTitle, AuthSubtitle, InputGroup, Label, Input, SubmitButton, BottomLink } from './AuthStyles';
import { useToast } from '../ui/ToastProvider'; // ایمپورت هوک
import Cookies from 'js-cookie';
import { apiFetch } from '../../utils/apiFetch';

export default function LoginClient() {
  const router = useRouter();
  const { showToast } = useToast(); // استفاده از هوک
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const res = await apiFetch('/api/v1/accounts/auth/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      const data = await res.json();

      if (!res.ok) throw new Error(data.detail || 'ایمیل یا رمز عبور اشتباه است.');

      // 🎯 اصلاح مسیر دریافت توکن‌ها بر اساس لاگ شما
      const accessToken = data.tokens?.access;
      const refreshToken = data.tokens?.refresh;

      if (!accessToken) {
        throw new Error('توکن در پاسخ سرور یافت نشد!');
      }

      // ذخیره کوکی‌ها با مقادیر صحیح
      Cookies.set('token', accessToken, { expires: 1 / 24, path: '/' });
      if (refreshToken) {
        Cookies.set('refresh', refreshToken, { expires: 7, path: '/' });
      }

      showToast('با موفقیت وارد شدید! خوش آمدید.', 'success');
      setTimeout(() => router.push('/accounts/profile'), 1500);

    } catch (error) {
      showToast(error.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthContainer>
      <AuthCard>
        <AuthTitle>ورود به حساب کاربری</AuthTitle>
        <AuthSubtitle>برای دسترسی به پنل کاربری و سبد خرید، وارد شوید.</AuthSubtitle>

        <form onSubmit={handleSubmit}>
          {/* تگ AlertMessage حذف شد */}
          <InputGroup>
            <Label htmlFor="email">ایمیل</Label>
            <Input id="email" type="email" dir="ltr" value={formData.email} onChange={(e) => setFormData({ ...formData, email: e.target.value })} required />
          </InputGroup>

          <InputGroup>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <Label htmlFor="password">رمز عبور</Label>
              <Link href="/auth/forgot-password" style={{ fontSize: '0.8rem', color: 'var(--primary)' }}>فراموشی رمز؟</Link>
            </div>
            <Input id="password" type="password" dir="ltr" value={formData.password} onChange={(e) => setFormData({ ...formData, password: e.target.value })} required />
          </InputGroup>

          <SubmitButton type="submit" disabled={loading}>
            {loading ? 'در حال ورود...' : 'ورود'}
          </SubmitButton>
        </form>

        <BottomLink>حساب کاربری ندارید؟ <Link href="/auth/register">ثبت‌نام کنید</Link></BottomLink>
      </AuthCard>
    </AuthContainer>
  );
}