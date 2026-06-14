// src/components/accounts/ProfileClient.jsx
'use client';

import React, { useState, useEffect, useRef ,useContext} from 'react';
import styled from '@emotion/styled';
import { apiFetch } from '../../utils/apiFetch';
import { ThemeModeContext } from '../../theme/ThemeRegistry';
import { useToast } from '../ui/ToastProvider';
import DatePicker from "react-multi-date-picker";
import persian from "react-date-object/calendars/persian";
import persian_fa from "react-date-object/locales/persian_fa";
import gregorian from "react-date-object/calendars/gregorian";
import gregorian_en from "react-date-object/locales/gregorian_en";
import "react-multi-date-picker/styles/backgrounds/bg-dark.css";
import Cookies from 'js-cookie';

// ==================== DICTIONARY ====================
const fieldTranslations = {
  national_code: 'کد ملی ۱۰ رقمی',
  company_name: 'نام شرکت/سازمان',
  national_id: 'شناسه ملی شرکت',
  economic_code: 'کد اقتصادی ۱۲ رقمی',
  birth_date: 'تاریخ تولد',
  address: 'آدرس دقیق پستی',
  postal_code: 'کد پستی ۱۰ رقمی',
  tel: 'تلفن ثابت',
  avatar: 'تصویر پروفایل'
};

// ==================== STYLES ====================
const PageWrapper = styled.div`
  max-width: 950px;
  margin: 2rem auto;
  padding: 0 2rem;
`;

const ProfileCard = styled.div`
  background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 16px;
  padding: 2.5rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  margin-bottom: 2rem;
`;

const ProgressContainer = styled.div`
  background-color: ${({ theme }) => theme.colors.background};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
`;

const ProgressHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  font-weight: bold;
`;

const ProgressBarWrapper = styled.div`
  width: 100%;
  height: 10px;
  background-color: ${({ theme }) => theme.colors.border};
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 1rem;
`;

const ProgressBarFill = styled.div`
  height: 100%;
  background-color: ${({ percentage, theme }) => percentage === 100 ? theme.colors.success : theme.colors.primary};
  width: ${({ percentage }) => percentage}%;
  transition: width 0.8s ease-out;
`;

const MissingFieldsList = styled.div`
  font-size: 0.85rem;
  color: ${({ theme }) => theme.colors.textMuted};
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  align-items: center;

  span {
    background-color: ${({ theme }) => `${theme.colors.error}15`};
    color: ${({ theme }) => theme.colors.error};
    padding: 0.2rem 0.6rem;
    border-radius: 20px;
    border: 1px solid ${({ theme }) => `${theme.colors.error}30`};
  }
`;

const HeaderSection = styled.div`
  display: flex;
  align-items: center;
  gap: 2rem;
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid ${({ theme }) => theme.colors.border};

  @media (max-width: 600px) {
    flex-direction: column;
    text-align: center;
  }`;

const AvatarWrapper = styled.div`
position: relative;
width: 120px;
height: 120px;
border-radius: 50%;
background: linear-gradient(135deg, ${({ theme }) => theme.colors.primary} 0%, ${({ theme }) => theme.colors.secondary} 100%);
display: flex;
align-items: center;
justify-content: center;
font-size: 3rem;
color: #fff;
overflow: hidden;
border: 4px solid ${({ theme }) => theme.colors.surface};
box-shadow: 0 10px 25px rgba(0,0,0,0.1);
cursor: pointer;

img { width: 100%; height: 100%; object-fit: cover; }
.overlay {
  position: absolute; inset: 0; background: rgba(0,0,0,0.5);
  display: flex; align-items: center; justify-content: center;
  opacity: 0; transition: opacity 0.3s ease; font-size: 1.5rem;
}
&:hover .overlay { opacity: 1; }
`;

const FormGrid = styled.div`
display: grid;
grid-template-columns: 1fr 1fr;
gap: 1.5rem;

@media (max-width: 600px) {
  grid-template-columns: 1fr;
}
`;

const InputGroup = styled.div`
display: flex;
flex-direction: column;
gap: 0.5rem;
grid-column: ${({ fullWidth }) => fullWidth ? '1 / -1' : 'auto'};
`;

const Label = styled.label`
color: ${({ theme }) => theme.colors.textMain};
font-size: 0.9rem;
font-weight: bold;
`;

const Input = styled.input`
background-color: ${({ theme, disabled }) => disabled ? `${theme.colors.border}22` : theme.colors.background};
border: 1px solid ${({ theme }) => theme.colors.border};
color: ${({ theme }) => theme.colors.textMain};
padding: 0.8rem 1rem;
border-radius: 8px;
font-family: inherit;
outline: none;
width: 100%;
box-sizing: border-box;
transition: border-color 0.2s;

&:focus {
  border-color: ${({ theme, disabled }) => disabled ? theme.colors.border : theme.colors.primary};
}
`;

const TextArea = styled.textarea`
background-color: ${({ theme }) => theme.colors.background};
border: 1px solid ${({ theme }) => theme.colors.border};
color: ${({ theme }) => theme.colors.textMain};
padding: 0.8rem 1rem;
border-radius: 8px;
font-family: inherit;
outline: none;
width: 100%;
box-sizing: border-box;
min-height: 80px;
resize: vertical;
`;

const TypeTabs = styled.div`
display: flex;
gap: 1rem;
margin-bottom: 2rem;
background-color: ${({ theme }) => theme.colors.background};
padding: 0.4rem;
border-radius: 10px;
border: 1px solid ${({ theme }) => theme.colors.border};
`;

const TypeTab = styled.button`
flex: 1;
background-color: ${({ active, theme }) => active ? theme.colors.surface : 'transparent'};
color: ${({ active, theme }) => active ? theme.colors.primary : theme.colors.textMuted};
border: ${({ active, theme }) => active ? `1px solid ${theme.colors.border}` : 'none'};
padding: 0.7rem;
border-radius: 8px;
font-family: inherit;
font-weight: bold;
cursor: pointer;
display: flex;
align-items: center;
justify-content: center;
gap: 0.5rem;
box-shadow: ${({ active }) => active ? '0 4px 10px rgba(0,0,0,0.05)' : 'none'};
transition: all 0.2s;
`;

const ActionButton = styled.button`
background-color: ${({ theme, variant }) => variant === 'primary' ? theme.colors.primary : theme.colors.surface};
color: ${({ theme, variant }) => variant === 'primary' ? '#fff' : theme.colors.textMain};
border: 1px solid ${({ theme, variant }) => variant === 'primary' ? theme.colors.primary : theme.colors.border};
padding: 0.8rem 1.8rem;
border-radius: 8px;
font-weight: bold;
cursor: pointer;
font-family: inherit;
transition: all 0.2s ease;

&:hover {
  background-color: ${({ theme, variant }) => variant === 'primary' ? theme.colors.secondary : theme.colors.background};
}
&:disabled { opacity: 0.6; cursor: not-allowed; }
`;

const HiddenInput = styled.input`
  display: none;
`;

const Title = styled.h2`
  font-size: 1.5rem;
  font-weight: bold;
  color: ${({ theme }) => theme.colors.textMain};
  margin-bottom: 0.4rem;
`;

const Subtitle = styled.p`
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 0.95rem;
`;

export default function ProfileClient() {
const { showToast } = useToast();
const fileInputRef = useRef(null);

const [loading, setLoading] = useState(true);
const [savingBase, setSavingBase] = useState(false);
const [savingRole, setSavingRole] = useState(false);

const { isDarkMode } = useContext(ThemeModeContext);

// دیتای دریافتی از مدل User
const [userData, setUserData] = useState({ first_name: '', last_name: '', email: '', mobile: '' });

// دیتای فیلدهای عمومی مدل Profile
const [generalProfile, setGeneralProfile] = useState({
  avatar: null, birth_date: '', tel: '', address: '', postal_code: ''
});

// فیلدهای حقوقی و حقیقی (برای ارسال به سوییچ)
const [profileType, setProfileType] = useState('individual'); // نوع فعلی در دیتابیس
const [selectedTab, setSelectedTab] = useState('individual'); // تبی که کاربر کلیک کرده
const [identityFields, setIdentityFields] = useState({
  national_code: '', company_name: '', national_id: '', economic_code: ''
});

const [completionStatus, setCompletionStatus] = useState({ percentage: 0, missing_fields: [] });
// استیت مربوط به تغییر رمز عبور
const [passwordData, setPasswordData] = useState({ old_password: '', new_password: '', new_password_confirm: '' });
const [passLoading, setPassLoading] = useState(false);
const handleDateChange = (date) => {
  if (!date) {
    setGeneralProfile({ ...generalProfile, birth_date: '' });
    return;
  }
  // تقویم دیتابیس ما میلادی است، پس تاریخ انتخاب شده را به YYYY-MM-DD تبدیل می‌کنیم
  const gregorianDate = date.convert(gregorian, gregorian_en).format("YYYY-MM-DD");
  setGeneralProfile({ ...generalProfile, birth_date: gregorianDate });
};

// ۱. دریافت اطلاعات اولیه پروفایل
useEffect(() => {
  const fetchProfileData = async () => {
    try {
      const [userRes, profileRes] = await Promise.all([
        apiFetch('/api/v1/accounts/me/'),
        apiFetch('/api/v1/accounts/me/profile/')
      ]);

      if (userRes.ok) {
        const user = await userRes.ok ? await userRes.json() : {};
        setUserData({
          first_name: user.user.first_name || '',
          last_name: user.user.last_name || '',
          email: user.user.email || '',
          mobile: user.user.mobile || ''
        });
      }

      if (profileRes.ok) {
        const resData = await profileRes.json();
        const profile = resData.profile || resData;
        const completion = resData.completion_status;

        setProfileType(profile.profile_type);
        setSelectedTab(profile.profile_type);

        setGeneralProfile({
          avatar: profile.avatar || null,
          birth_date: profile.birth_date || '',
          tel: profile.tel || '',
          address: profile.address || '',
          postal_code: profile.postal_code || ''
        });

        setIdentityFields({
          national_code: profile.national_code || '',
          company_name: profile.company_name || '',
          national_id: profile.national_id || '',
          economic_code: profile.economic_code || ''
        });

        if (completion) {
          setCompletionStatus({
            percentage: completion.percentage || 0,
            missing_fields: completion.missing_fields || []
          });
        }
      }
    } catch (error) {
      showToast('خطا در دریافت اطلاعات پروفایل', 'error');
    } finally {
      setLoading(false);
    }
  };

  fetchProfileData();
}, [showToast]);

// ۲. بروزرسانی فیلدهای عمومی و مشترک (ProfileUpdateSerializer)
const handleSaveGeneralInfo = async (e) => {
  e.preventDefault();
  setSavingBase(true);

  try {
    // ابتدا ذخیره نام در تگ کاربری
    await apiFetch('/api/v1/accounts/me/', {
      method: 'PATCH',
      body: JSON.stringify({ first_name: userData.first_name, last_name: userData.last_name })
    });

    // ذخیره فیلدهای عمومی پروفایل
    const res = await apiFetch('/api/v1/accounts/me/profile/', {
      method: 'PATCH',
      body: JSON.stringify({
        birth_date: generalProfile.birth_date || null,
        tel: generalProfile.tel,
        address: generalProfile.address,
        postal_code: generalProfile.postal_code
      })
    });

    if (!res.ok) {
      const errors = await res.json();
      throw new Error(Object.values(errors)[0] || 'خطا در اعتبارسنجی اطلاعات پستی.');
    }

    showToast('اطلاعات عمومی با موفقیت ثبت شد.', 'success');
    setTimeout(() => window.location.reload(), 1200);
  } catch (error) {
    showToast(error.message, 'error');
  } finally {
    setSavingBase(false);
  }
};

// ۳. ثبت اطلاعات هویتی و تغییر نوع پروفایل (Switch Actions)
const handleIdentitySubmit = async (e) => {
  e.preventDefault();
  setSavingRole(true);

  try {
    // 🟢 حالت اول: کاربر می‌خواهد نوع حسابش را تغییر دهد (سوییچ کند)
    if (profileType !== selectedTab) {
      const isLegalAction = selectedTab === 'legal';
      const endpoint = isLegalAction
        ? '/api/v1/accounts/me/profile/switch-to-legal/'
        : '/api/v1/accounts/me/profile/switch-to-individual/';

      const bodyPayload = isLegalAction
        ? { company_name: identityFields.company_name, national_id: identityFields.national_id, economic_code: identityFields.economic_code }
        : { national_code: identityFields.national_code };

      const res = await apiFetch(endpoint, {
        method: 'POST',
        body: JSON.stringify(bodyPayload)
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.error || Object.values(data)[0] || 'خطا در تایید هویت. اطلاعات را بررسی کنید.');

      showToast(isLegalAction ? 'حساب شما به حقوقی تغییر یافت.' : 'حساب شما به حقیقی تغییر یافت.', 'success');
      setProfileType(selectedTab);
    }
    // 🔵 حالت دوم: کاربر فقط می‌خواهد فیلدهای هویتی (مثل کد ملی) حساب فعلی‌اش را بروزرسانی کند
    else {
      const bodyPayload = selectedTab === 'legal'
        ? { company_name: identityFields.company_name, national_id: identityFields.national_id, economic_code: identityFields.economic_code }
        : { national_code: identityFields.national_code };

      const res = await apiFetch('/api/v1/accounts/me/profile/', {
        method: 'PATCH', // استفاده از متد آپدیت به جای سوییچ
        body: JSON.stringify(bodyPayload)
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || Object.values(data)[0] || 'خطا در بروزرسانی اطلاعات هویتی.');
      }

      showToast('اطلاعات هویتی با موفقیت بروزرسانی شد.', 'success');
    }

    // رفرش صفحه برای آپدیت شدن درصد تکمیل پروفایل
    setTimeout(() => window.location.reload(), 1200);

  } catch (error) {
    showToast(error.message, 'error');
  } finally {
    setSavingRole(false);
  }
};

// ۴. مدیریت آپلود فایل آواتار
const handleAvatarChange = async (e) => {
  const file = e.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append('avatar', file);

  try {
    const res = await apiFetch('/api/v1/accounts/me/profile/', {
      method: 'PATCH',
      body: formData
    });

    if (!res.ok) throw new Error();
    const data = await res.json();
    const updatedProfile = data.profile || data;

    setGeneralProfile(prev => ({ ...prev, avatar: updatedProfile.avatar }));
    showToast('تصویر پروفایل با موفقیت تغییر کرد.', 'success');
    setTimeout(() => window.location.reload(), 800);
  } catch (error) {
    showToast('حجم فایل باید کمتر از ۵ مگابایت و فرمت تصویر معتبر باشد.', 'error');
  }
};

if (loading) return <PageWrapper><h3 style={{ textAlign: 'center', marginTop: '4rem' }}>در حال بارگذاری اطلاعات...</h3></PageWrapper>;

const initialLetter = userData.first_name ? userData.first_name.charAt(0) : 'U';

const handleChangePassword = async (e) => {
  e.preventDefault();

  if (passwordData.new_password !== passwordData.new_password_confirm) {
    return showToast('رمز عبور جدید و تکرار آن یکسان نیستند.', 'error');
  }
  if (passwordData.new_password.length < 8) {
    return showToast('رمز عبور جدید باید حداقل ۸ کاراکتر باشد.', 'error');
  }

  setPassLoading(true);
  try {
    const res = await apiFetch('/api/v1/accounts/auth/password/change/', {
      method: 'POST',
      body: JSON.stringify({
        old_password: passwordData.old_password,
        new_password: passwordData.new_password,
        new_password_confirm: passwordData.new_password_confirm
      })
    });

    // دیتا را در هر صورت پارس می‌کنیم تا توکن‌ها یا ارورها را بگیریم
    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || data.old_password?.[0] || data.error || 'رمز عبور فعلی اشتباه است.');
    }

    // 🎯 آپدیت کوکی‌ها با توکن‌های جدید برای جلوگیری از بیرون پریدن کاربر
    if (data.tokens) {
      Cookies.set('token', data.tokens.access, { expires: 1 / 24, path: '/' });
      Cookies.set('refresh', data.tokens.refresh, { expires: 7, path: '/' });
    }

    showToast('رمز عبور شما با موفقیت تغییر کرد.', 'success');
    setPasswordData({ old_password: '', new_password: '', new_password_confirm: '' });

  } catch (error) {
    showToast(error.message, 'error');
  } finally {
    setPassLoading(false);
  }
};

return (
  <PageWrapper>
    {/* سکتور درصد تکمیل اطلاعات پروفایل */}
    <ProgressContainer>
      <ProgressHeader>
        <span>تکمیل مدارک و مشخصات حساب کاربری</span>
        <span style={{ color: completionStatus.percentage === 100 ? 'var(--success)' : 'var(--primary)' }}>
          {completionStatus.percentage}%
        </span>
      </ProgressHeader>
      <ProgressBarWrapper>
        <ProgressBarFill percentage={completionStatus.percentage} />
      </ProgressBarWrapper>

      {completionStatus.missing_fields.length > 0 ? (
        <MissingFieldsList>
          فیلدهای باقیمانده جهت تکمیل پیش‌فاکتور رسمی:
          {completionStatus.missing_fields.map((field, idx) => (
            <span key={idx}>{fieldTranslations[field] || field}</span>
          ))}
        </MissingFieldsList>
      ) : (
        <p style={{ fontSize: '0.85rem', color: 'var(--success)', fontWeight: 'bold' }}>
          🎉 مشخصات شما تکمیل است و فاکتورهای خرید رسمی صادر خواهند شد.
        </p>
      )}
    </ProgressContainer>

    {/* بخش اول: اطلاعات عمومی و پستی */}
    <ProfileCard>
      <HeaderSection>
        <AvatarWrapper onClick={() => fileInputRef.current.click()}>
          {generalProfile.avatar ? <img src={generalProfile.avatar} alt="Avatar" /> : initialLetter}
          <div className="overlay">📷</div>
        </AvatarWrapper>
        <HiddenInput type="file" accept="image/*" ref={fileInputRef} onChange={handleAvatarChange} />

        <div>
          <Title>{userData.first_name ? `${userData.first_name} ${userData.last_name}` : 'کاربر زیگما'}</Title>
          <Subtitle>نوع حساب فعال: {profileType === 'legal' ? '🏢 شخصیت حقوقی / شرکتی' : '👤 شخصیت حقیقی'}</Subtitle>
        </div>
      </HeaderSection>

      <form onSubmit={handleSaveGeneralInfo}>
        <FormGrid>
          <InputGroup>
            <Label>نام</Label>
            <Input value={userData.first_name} onChange={(e) => setUserData({ ...userData, first_name: e.target.value })} required />
          </InputGroup>

          <InputGroup>
            <Label>نام خانوادگی</Label>
            <Input value={userData.last_name} onChange={(e) => setUserData({ ...userData, last_name: e.target.value })} required />
          </InputGroup>

          <InputGroup>
          <Label>تاریخ تولد (شمسی)</Label>
            <DatePicker
              calendar={persian}
              locale={persian_fa}
              // اگر از قبل تاریخی در دیتابیس بود، آن را به عنوان آبجکت Date پاس می‌دهیم تا خودش شمسی‌اش کند
              value={generalProfile.birth_date ? new Date(generalProfile.birth_date) : null}
              onChange={handleDateChange}
              className={isDarkMode ? "bg-dark" : ""} // تغییر رنگ پاپ‌آپ تقویم بر اساس تم سایت
              containerStyle={{ width: '100%' }}
              // 🎯 رندر کردن تقویم درون اینپوت اختصاصی خودمان تا استایل‌ها یکپارچه بماند
              render={<Input placeholder="انتخاب تاریخ..." style={{ cursor: 'pointer' }} readOnly />}
            />
          </InputGroup>

          <InputGroup>
            <Label>تلفن ثابت (همراه با کد شهر)</Label>
            <Input type="tel" dir="ltr" placeholder="02112345678" value={generalProfile.tel} onChange={(e) => setGeneralProfile({ ...generalProfile, tel: e.target.value })} />
          </InputGroup>

          <InputGroup>
            <Label>کد پستی (۱۰ رقمی)</Label>
            <Input type="text" dir="ltr" maxLength={10} placeholder="1234567890" value={generalProfile.postal_code} onChange={(e) => setGeneralProfile({ ...generalProfile, postal_code: e.target.value })} />
          </InputGroup>

          <InputGroup fullWidth>
            <Label>آدرس کامل جهت تحویل کالا / سرور</Label>
            <TextArea value={generalProfile.address} onChange={(e) => setGeneralProfile({ ...generalProfile, address: e.target.value })} placeholder="استان، شهر، خیابان اصلی، کوچه، پلاک، واحد" />
          </InputGroup>

          <div style={{ marginTop: '1rem' }}>
            <ActionButton type="submit" variant="primary" disabled={savingBase}>
              {savingBase ? 'در حال ثبت...' : 'ذخیره مشخصات عمومی'}
            </ActionButton>
          </div>
        </FormGrid>
      </form>
    </ProfileCard>

    {/* بخش دوم: اطلاعات مالی و هویتی (حقیقی / حقوقی) */}
    <ProfileCard>
      <Title style={{ marginBottom: '1.5rem' }}>اطلاعات هویتی و نوع فاکتور مالی</Title>
      <Subtitle style={{ marginBottom: '2rem' }}>
        نوع حساب خود را انتخاب کنید. تغییر حساب فیلدهای مالیاتی مربوطه را جهت صدور فاکتور رسمی تغییر می‌دهد.
      </Subtitle>

      <TypeTabs>
        <TypeTab type="button" active={selectedTab === 'individual'} onClick={() => setSelectedTab('individual')}>
          👤 شخص حقیقی
        </TypeTab>
        <TypeTab type="button" active={selectedTab === 'legal'} onClick={() => setSelectedTab('legal')}>
          🏢 شخص حقوقی (شرکت / سازمان)
        </TypeTab>
      </TypeTabs>

      <form onSubmit={handleIdentitySubmit}>
        <FormGrid>
          {selectedTab === 'individual' ? (
            <InputGroup>
              <Label>کد ملی خریدار</Label>
              <Input
                type="text"
                dir="ltr"
                maxLength={10}
                placeholder="0012345678"
                value={identityFields.national_code}
                onChange={(e) => setIdentityFields({ ...identityFields, national_code: e.target.value })}
                required
              />
            </InputGroup>
          ) : (
            <>
              <InputGroup>
                <Label>نام کامل شرکت (حقوقی)</Label>
                <Input
                  type="text"
                  placeholder="پیشگامان سخت‌افزار زیگما"
                  value={identityFields.company_name}
                  onChange={(e) => setIdentityFields({ ...identityFields, company_name: e.target.value })}
                  required
                />
              </InputGroup>

              <InputGroup>
                <Label>شناسه ملی شرکت (۱۱ رقمی)</Label>
                <Input
                  type="text"
                  dir="ltr"
                  maxLength={11}
                  placeholder="14001234567"
                  value={identityFields.national_id}
                  onChange={(e) => setIdentityFields({ ...identityFields, national_id: e.target.value })}
                  required
                />
              </InputGroup>

              <InputGroup>
                <Label>کد اقتصادی (۱۲ رقمی)</Label>
                <Input
                  type="text"
                  dir="ltr"
                  maxLength={12}
                  placeholder="411123456789"
                  value={identityFields.economic_code}
                  onChange={(e) => setIdentityFields({ ...identityFields, economic_code: e.target.value })}
                  required
                />
              </InputGroup>
            </>
          )}

          <div style={{ gridColumn: '1 / -1', marginTop: '1.5rem' }}>
            <ActionButton
              type="submit"
              variant="primary"
              disabled={savingRole || (profileType === selectedTab && completionStatus.percentage > 40 && !completionStatus.missing_fields.includes('national_code') && !completionStatus.missing_fields.includes('company_name'))}
            >
              {savingRole ? 'در حال ثبت در سامانه...' : profileType !== selectedTab ? 'ارتقا و سوییچ نوع حساب' : 'بروزرسانی مشخصات هویتی'}
            </ActionButton>
          </div>
        </FormGrid>
      </form>
    </ProfileCard>
    <ProfileCard>
        <Title style={{ marginBottom: '1.5rem', color: 'var(--error)' }}>امنیت و کلمه عبور</Title>
        <Subtitle style={{ marginBottom: '2rem' }}>
          برای حفظ امنیت حساب کاربری خود، پیشنهاد می‌شود رمز عبورتان را به‌صورت دوره‌ای تغییر دهید.
        </Subtitle>

        <form onSubmit={handleChangePassword}>
          <FormGrid>
            <InputGroup fullWidth>
              <Label>رمز عبور فعلی</Label>
              <Input
                type="password"
                dir="ltr"
                placeholder="••••••••"
                value={passwordData.old_password}
                onChange={(e) => setPasswordData({ ...passwordData, old_password: e.target.value })}
                required
              />
            </InputGroup>

            <InputGroup>
              <Label>رمز عبور جدید</Label>
              <Input
                type="password"
                dir="ltr"
                placeholder="••••••••"
                value={passwordData.new_password}
                onChange={(e) => setPasswordData({ ...passwordData, new_password: e.target.value })}
                required
              />
            </InputGroup>

            <InputGroup>
              <Label>تکرار رمز عبور جدید</Label>
              <Input
                type="password"
                dir="ltr"
                placeholder="••••••••"
                value={passwordData.new_password_confirm}
                onChange={(e) => setPasswordData({ ...passwordData, new_password_confirm: e.target.value })}
                required
              />
            </InputGroup>

            <div style={{ marginTop: '1rem', gridColumn: '1 / -1' }}>
              <ActionButton
                variant="primary"
                type="submit"
                // style={{ backgroundColor: 'var(--error)', borderColor: 'var(--error)', color: '#fff' }}
                disabled={passLoading}
              >
                {passLoading ? 'در حال پردازش...' : 'تغییر رمز عبور'}
              </ActionButton>
            </div>
          </FormGrid>
        </form>
      </ProfileCard>
  </PageWrapper>
);
}