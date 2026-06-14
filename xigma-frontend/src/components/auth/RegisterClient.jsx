// src/components/auth/RegisterClient.jsx
'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  AuthContainer, AuthCard, AuthTitle, AuthSubtitle,
  InputGroup, Label, Input, SubmitButton, BottomLink, Tabs, Tab
} from './AuthStyles'; // AlertMessage حذف شد
import { useToast } from '../ui/ToastProvider';
import { apiFetch } from '../../utils/apiFetch';

export default function RegisterClient() {
  const router = useRouter();
  const { showToast } = useToast();
  const [activeTab, setActiveTab] = useState('email'); // 'email' | 'mobile'

  const [formData, setFormData] = useState({
    email: '', mobile: '', password: '', password_confirm: '', first_name: '', last_name: ''
  });

  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    // بررسی تطابق رمز عبور قبل از ارسال به سرور
    if (formData.password !== formData.password_confirm) {
      showToast('رمز عبور و تکرار آن یکسان نیستند.', 'error');
      setIsLoading(false);
      return;
    }

    const endpoint = activeTab === 'email'
      ? '/api/v1/accounts/auth/register/email/'
      : '/api/v1/accounts/auth/register/mobile/';

    const payload = activeTab === 'email'
      ? { email: formData.email, password: formData.password, password_confirm: formData.password_confirm, first_name: formData.first_name, last_name: formData.last_name }
      : { mobile: formData.mobile, password: formData.password };

    try {
      const res = await apiFetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || Object.values(data)[0] || 'خطا در ثبت نام. لطفا اطلاعات را بررسی کنید.');

      setIsSuccess(true);
      showToast('ثبت‌نام با موفقیت انجام شد. در حال انتقال...', 'success');

      // انتقال به صفحه لاگین پس از ۲ ثانیه
      setTimeout(() => router.push('/auth/login'), 2000);

    } catch (error) {
      showToast(error.message, 'error');
      setIsLoading(false); // فقط در صورت ارور لودینگ را متوقف می‌کنیم تا کاربر بتواند دوباره تلاش کند
    }
  };

  return (
    <AuthContainer>
      <AuthCard>
        <AuthTitle>ایجاد حساب کاربری</AuthTitle>
        <AuthSubtitle>به خانواده بزرگ XigmaHardware بپیوندید.</AuthSubtitle>

        <Tabs>
          <Tab active={activeTab === 'email'} onClick={() => setActiveTab('email')}>ثبت‌نام با ایمیل</Tab>
          <Tab active={activeTab === 'mobile'} onClick={() => setActiveTab('mobile')}>ثبت‌نام با موبایل</Tab>
        </Tabs>

        <form onSubmit={handleSubmit}>

          {activeTab === 'email' ? (
            <>
              {/* استفاده از Grid ریسپانسیو برای جلوگیری از بیرون‌زدگی اینپوت‌ها */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem' }}>
                <InputGroup>
                  <Label>نام</Label>
                  <Input name="first_name" value={formData.first_name} onChange={handleChange} required />
                </InputGroup>
                <InputGroup>
                  <Label>نام خانوادگی</Label>
                  <Input name="last_name" value={formData.last_name} onChange={handleChange} required />
                </InputGroup>
              </div>
              <InputGroup>
                <Label>ایمیل</Label>
                <Input name="email" type="email" dir="ltr" value={formData.email} onChange={handleChange} required />
              </InputGroup>
            </>
          ) : (
            <InputGroup>
              <Label>شماره موبایل</Label>
              <Input name="mobile" type="tel" dir="ltr" placeholder="09123456789" value={formData.mobile} onChange={handleChange} required />
            </InputGroup>
          )}

          <InputGroup>
            <Label>رمز عبور</Label>
            <Input name="password" type="password" dir="ltr" value={formData.password} onChange={handleChange} required />
          </InputGroup>

          <InputGroup>
            <Label>تکرار رمز عبور</Label>
            <Input name="password_confirm" type="password" dir="ltr" value={formData.password_confirm} onChange={handleChange} required />
          </InputGroup>

          {/* اگر ثبت نام موفق بود دکمه کلا غیرفعال می‌شود تا ریدایرکت انجام شود */}
          <SubmitButton type="submit" disabled={isLoading || isSuccess}>
            {isLoading ? 'در حال پردازش...' : 'ثبت نام'}
          </SubmitButton>
        </form>

        <BottomLink>
          از قبل حساب دارید؟ <Link href="/auth/login">وارد شوید</Link>
        </BottomLink>
      </AuthCard>
    </AuthContainer>
  );
}