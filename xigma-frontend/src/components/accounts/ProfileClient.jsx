'use client';

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import styled from '@emotion/styled';

// ==================== STYLED COMPONENTS ====================
const Container = styled.div`
  max-width: 1100px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
`;

const Header = styled.div`
  margin-bottom: 2rem;
`;

const Title = styled.h1`
  font-size: 2rem;
  font-weight: 700;
  color: ${({ theme }) => theme.colors?.textPrimary || '#111827'};
  margin-bottom: 0.5rem;
`;

const Subtitle = styled.p`
  color: ${({ theme }) => theme.colors?.textMuted || '#6b7280'};
  font-size: 1rem;
`;

const TabContainer = styled.div`
  display: flex;
  gap: 8px;
  border-bottom: 1px solid ${({ theme }) => theme.colors?.border || '#e5e7eb'};
  margin-bottom: 2rem;
  overflow-x: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
  &::-webkit-scrollbar { display: none; }
`;

const TabButton = styled.button`
  padding: 14px 28px;
  font-size: 15px;
  font-weight: 600;
  color: ${({ active, theme }) => 
    active 
      ? (theme.colors?.primary || '#3b82f6') 
      : (theme.colors?.textSecondary || '#4b5563')};
  background: none;
  border: none;
  border-bottom: 3px solid ${({ active, theme }) => 
    active 
      ? (theme.colors?.primary || '#3b82f6') 
      : 'transparent'};
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);

  &:hover {
    color: ${({ theme }) => theme.colors?.primary || '#3b82f6'};
  }
`;

const TabContent = styled.div`
  animation: fadeIn 0.3s ease forwards;
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
  }
`;

const FormGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
`;

const Label = styled.label`
  font-size: 14px;
  font-weight: 600;
  color: ${({ theme }) => theme.colors?.textSecondary || '#4b5563'};
`;

const Input = styled.input`
  padding: 12px 16px;
  border: 1px solid ${({ theme }) => theme.colors?.border || '#e5e7eb'};
  border-radius: 10px;
  font-size: 15px;
  background: ${({ theme }) => theme.colors?.background || '#fff'};
  color: ${({ theme }) => theme.colors?.textPrimary || '#111827'};
  transition: all 0.2s ease;

  &:focus {
    outline: none;
    border-color: ${({ theme }) => theme.colors?.primary || '#3b82f6'};
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
`;

const Button = styled.button`
  padding: 14px 32px;
  background: ${({ theme }) => theme.colors?.primary || '#3b82f6'};
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-top: 1.5rem;

  &:hover {
    opacity: 0.9;
    transform: translateY(-1px);
  }
`;

// ==================== MAIN COMPONENT ====================
export default function ProfileClient() {
  const [activeTab, setActiveTab] = useState('personal');

  const tabs = [
    { id: 'personal', label: 'اطلاعات شخصی' },
    { id: 'account-type', label: 'نوع حساب' },
    { id: 'security', label: 'امنیت' },
    { id: 'contact', label: 'تماس و تأیید' },
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'personal':
        return <PersonalInfoForm />;
      case 'account-type':
        return <AccountTypeSection />;
      case 'security':
        return <SecuritySection />;
      case 'contact':
        return <ContactVerificationSection />;
      default:
        return <PersonalInfoForm />;
    }
  };

  return (
    <div style={{ maxWidth: '1100px', margin: '0 auto', padding: '2rem 1.5rem' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '0.5rem' }}>پروفایل کاربری</h1>
        <p style={{ color: '#6b7280' }}>اطلاعات حساب خود را مدیریت کنید</p>
      </div>

      <TabContainer>
        {tabs.map((tab) => (
          <TabButton
            key={tab.id}
            active={activeTab === tab.id}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </TabButton>
        ))}
      </TabContainer>

      <TabContent key={activeTab}>
        {renderTabContent()}
      </TabContent>
    </div>
  );
}

// ==================== PERSONAL INFO FORM (با react-hook-form) ====================
function PersonalInfoForm() {
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm({
    defaultValues: {
      first_name: '',
      last_name: '',
      birth_date: '',
      phone: '',
      postal_code: '',
      address: '',
    }
  });

  const onSubmit = async (data) => {
    console.log('Submitting:', data);
    // TODO: ارسال به API
    alert('اطلاعات با موفقیت ذخیره شد (موقت)');
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <FormGrid>
        <FormGroup>
          <Label>نام</Label>
          <Input {...register('first_name', { required: 'نام الزامی است' })} placeholder="نام" />
          {errors.first_name && <span style={{ color: 'red', fontSize: '13px' }}>{errors.first_name.message}</span>}
        </FormGroup>

        <FormGroup>
          <Label>نام خانوادگی</Label>
          <Input {...register('last_name', { required: 'نام خانوادگی الزامی است' })} placeholder="نام خانوادگی" />
          {errors.last_name && <span style={{ color: 'red', fontSize: '13px' }}>{errors.last_name.message}</span>}
        </FormGroup>

        <FormGroup>
          <Label>تاریخ تولد</Label>
          <Input type="date" {...register('birth_date')} />
        </FormGroup>

        <FormGroup>
          <Label>شماره تلفن</Label>
          <Input {...register('phone')} placeholder="0912xxxxxxx" />
        </FormGroup>

        <FormGroup>
          <Label>کد پستی</Label>
          <Input {...register('postal_code')} placeholder="کد پستی" />
        </FormGroup>

        <FormGroup style={{ gridColumn: '1 / -1' }}>
          <Label>آدرس کامل</Label>
          <Input as="textarea" {...register('address')} placeholder="آدرس کامل" style={{ minHeight: '100px', resize: 'vertical' }} />
        </FormGroup>
      </FormGrid>

      <Button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'در حال ذخیره...' : 'ذخیره تغییرات'}
      </Button>
    </form>
  );
}

// Placeholder sections for other tabs
function AccountTypeSection() {
  return <div>نوع حساب (حقیقی / حقوقی) - در حال توسعه</div>;
}

function SecuritySection() {
  return <div>تغییر رمز عبور - در حال توسعه</div>;
}

function ContactVerificationSection() {
  return <div>ایمیل و موبایل + OTP - در حال توسعه</div>;
}
