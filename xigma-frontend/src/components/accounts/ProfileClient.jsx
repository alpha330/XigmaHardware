'use client';

import React, { useState ,useContext} from 'react';
import styled from '@emotion/styled';
import { ThemeModeContext } from '../../theme/ThemeRegistry';

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

  @media (max-width: 768px) {
    gap: 4px;
  }
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
  position: relative;

  &:hover {
    color: ${({ theme }) => theme.colors?.primary || '#3b82f6'};
  }

  @media (max-width: 768px) {
    padding: 12px 20px;
    font-size: 14px;
  }
`;

const TabContent = styled.div`
  animation: fadeIn 0.3s ease forwards;
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }
`;

const SectionCard = styled.div`
  background: ${({ theme }) => theme.colors?.surface || '#fff'};
  border: 1px solid ${({ theme }) => theme.colors?.border || '#e5e7eb'};
  border-radius: 16px;
  padding: 2rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05);
`;

// ==================== MAIN COMPONENT ====================
export default function ProfileClient() {
  const [activeTab, setActiveTab] = useState('personal');
  const { isDarkMode, toggleTheme } = useContext(ThemeModeContext);

  const tabs = [
    { id: 'personal', label: 'اطلاعات شخصی' },
    { id: 'account-type', label: 'نوع حساب' },
    { id: 'security', label: 'امنیت' },
    { id: 'contact', label: 'تماس و تأیید' },
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'personal':
        return <PersonalInfoSection />;
      case 'account-type':
        return <AccountTypeSection />;
      case 'security':
        return <SecuritySection />;
      case 'contact':
        return <ContactVerificationSection />;
      default:
        return <PersonalInfoSection />;
    }
  };

  return (
    <Container>
      <Header>
        <Title>پروفایل کاربری</Title>
        <Subtitle>اطلاعات حساب خود را مدیریت کنید</Subtitle>
      </Header>

      {/* Tabs */}
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

      {/* Tab Content with Animation */}
      <TabContent key={activeTab}>
        {renderTabContent()}
      </TabContent>
    </Container>
  );
}

// ==================== SECTION COMPONENTS (ساده شده برای نمایش) ====================

function PersonalInfoSection() {
  return (
    <SectionCard>
      <h3 style={{ marginBottom: '1.5rem', fontSize: '1.3rem' }}>اطلاعات شخصی</h3>
      {/* فرم اطلاعات شخصی اینجا قرار می‌گیرد */}
      <p>فرم نام، نام خانوادگی، تاریخ تولد، آدرس و ...</p>
    </SectionCard>
  );
}

function AccountTypeSection() {
  return (
    <SectionCard>
      <h3 style={{ marginBottom: '1.5rem', fontSize: '1.3rem' }}>نوع حساب</h3>
      <p>انتخاب حقیقی یا حقوقی + فیلدهای مربوطه</p>
    </SectionCard>
  );
}

function SecuritySection() {
  return (
    <SectionCard>
      <h3 style={{ marginBottom: '1.5rem', fontSize: '1.3rem' }}>امنیت</h3>
      <p>فرم تغییر رمز عبور</p>
    </SectionCard>
  );
}

function ContactVerificationSection() {
  return (
    <SectionCard>
      <h3 style={{ marginBottom: '1.5rem', fontSize: '1.3rem' }}>تماس و تأیید</h3>
      <p>ایمیل، موبایل و تأیید با OTP</p>
    </SectionCard>
  );
}
