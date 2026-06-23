'use client';

import React, { useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import DatePicker from 'react-multi-date-picker';
import persian from 'react-date-object/calendars/persian';
import persian_fa from 'react-date-object/locales/persian_fa';
import styled from '@emotion/styled';

// ==================== STYLED COMPONENTS (بهبود یافته برای دارک مود) ====================
const Container = styled.div`
  max-width: 1100px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
`;

const TabContainer = styled.div`
  display: flex;
  gap: 8px;
  border-bottom: 1px solid ${({ theme }) => theme.colors?.border || '#334155'};
  margin-bottom: 2rem;
  overflow-x: auto;
  scrollbar-width: none;
`;

const TabButton = styled.button`
  padding: 14px 28px;
  font-size: 15px;
  font-weight: 600;
  color: ${({ active, theme }) => 
    active 
      ? (theme.colors?.primary || '#60a5fa') 
      : (theme.colors?.textSecondary || '#94a3b8')};
  background: none;
  border: none;
  border-bottom: 3px solid ${({ active, theme }) => 
    active 
      ? (theme.colors?.primary || '#60a5fa') 
      : 'transparent'};
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.25s ease;

  &:hover {
    color: ${({ theme }) => theme.colors?.primary || '#60a5fa'};
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
  color: ${({ theme }) => theme.colors?.textSecondary || '#cbd5e1'};
`;

const StyledInput = styled.input`
  padding: 12px 16px;
  border: 1px solid ${({ theme }) => theme.colors?.border || '#475569'};
  border-radius: 10px;
  font-size: 15px;
  background: ${({ theme }) => theme.colors?.surface || '#1e293b'};
  color: ${({ theme }) => theme.colors?.textPrimary || '#f1f5f9'};
  transition: all 0.2s ease;

  &:focus {
    outline: none;
    border-color: ${({ theme }) => theme.colors?.primary || '#60a5fa'};
    box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.15);
  }

  &::placeholder {
    color: ${({ theme }) => theme.colors?.textMuted || '#64748b'};
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
        return <div>نوع حساب - در حال توسعه</div>;
      case 'security':
        return <div>امنیت - در حال توسعه</div>;
      case 'contact':
        return <div>تماس و تأیید - در حال توسعه</div>;
      default:
        return <PersonalInfoForm />;
    }
  };

  return (
    <Container>
      <div style={{ marginBottom: '2rem' }}>
        <Title>پروفایل کاربری</Title>
        <Subtitle>اطلاعات حساب خود را مدیریت کنید</Subtitle>
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
    </Container>
  );
}

// ==================== PERSONAL INFO FORM ====================
function PersonalInfoForm() {
  const { control, register, handleSubmit, formState: { errors, isSubmitting } } = useForm({
    defaultValues: {
      first_name: '',
      last_name: '',
      birth_date: null,
      phone: '',
      postal_code: '',
      address: '',
    }
  });

  const onSubmit = async (data) => {
    console.log('Form Data:', data);
    alert('اطلاعات ذخیره شد (موقت)');
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <FormGrid>
        <FormGroup>
          <Label>نام</Label>
          <StyledInput {...register('first_name', { required: 'نام الزامی است' })} placeholder="نام" />
        </FormGroup>

        <FormGroup>
          <Label>نام خانوادگی</Label>
          <StyledInput {...register('last_name', { required: 'نام خانوادگی الزامی است' })} placeholder="نام خانوادگی" />
        </FormGroup>

        {/* تاریخ تولد شمسی */}
        <FormGroup>
          <Label>تاریخ تولد (شمسی)</Label>
          <Controller
            name="birth_date"
            control={control}
            render={({ field }) => (
              <DatePicker
                value={field.value}
                onChange={field.onChange}
                calendar={persian}
                locale={persian_fa}
                inputClass="custom-date-input"
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  borderRadius: '10px',
                  border: '1px solid #475569',
                  background: '#1e293b',
                  color: '#f1f5f9',
                  fontSize: '15px'
                }}
              />
            )}
          />
        </FormGroup>

        <FormGroup>
          <Label>شماره تلفن</Label>
          <StyledInput {...register('phone')} placeholder="0912xxxxxxx" />
        </FormGroup>

        <FormGroup>
          <Label>کد پستی</Label>
          <StyledInput {...register('postal_code')} placeholder="کد پستی" />
        </FormGroup>

        <FormGroup style={{ gridColumn: '1 / -1' }}>
          <Label>آدرس کامل</Label>
          <StyledInput
            as="textarea"
            {...register('address')}
            placeholder="آدرس کامل"
            style={{ minHeight: '100px', resize: 'vertical' }}
          />
        </FormGroup>
      </FormGrid>

      <Button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'در حال ذخیره...' : 'ذخیره تغییرات'}
      </Button>
    </form>
  );
}
