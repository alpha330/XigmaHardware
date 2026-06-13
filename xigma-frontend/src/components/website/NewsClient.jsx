// src/components/website/NewsClient.jsx
'use client';

import React, { useState } from 'react';
import styled from '@emotion/styled';
import { keyframes } from '@emotion/react';
import ArticleCard from '../shared/ArticleCard';

const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
`;

const PageWrapper = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 4rem 2rem;
`;

const HeaderSection = styled.div`
  text-align: center;
  margin-bottom: 3rem;
`;

const Title = styled.h1`
  font-size: 2.5rem;
  font-weight: 900;
  color: ${({ theme }) => theme.colors.textMain};
  margin-bottom: 1rem;
`;

const Subtitle = styled.p`
  font-size: 1.1rem;
  color: ${({ theme }) => theme.colors.textMuted};
  max-width: 600px;
  margin: 0 auto;
`;

const TabsContainer = styled.div`
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 3rem;
  border-bottom: 1px solid ${({ theme }) => theme.colors.border};
  padding-bottom: 1rem;
`;

const TabButton = styled.button`
  background-color: ${({ active, theme }) => active ? theme.colors.primary : 'transparent'};
  color: ${({ active, theme }) => active ? '#fff' : theme.colors.textMain};
  border: 1px solid ${({ active, theme }) => active ? theme.colors.primary : theme.colors.border};
  padding: 0.8rem 2rem;
  border-radius: 30px;
  font-size: 1.1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: inherit;

  &:hover {
    background-color: ${({ active, theme }) => active ? theme.colors.primary : theme.colors.surface};
  }
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
  animation: ${fadeIn} 0.5s ease-out;
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 4rem;
  color: ${({ theme }) => theme.colors.textMuted};
  background-color: ${({ theme }) => theme.colors.surface};
  border-radius: 16px;
  border: 1px dashed ${({ theme }) => theme.colors.border};
`;

export default function NewsClient({ articles, news }) {
  // مدیریت تب فعال (پیش‌فرض روی مقالات)
  const [activeTab, setActiveTab] = useState('articles');

  // داده‌ای که باید نمایش داده شود بر اساس تب انتخابی
  const currentData = activeTab === 'articles' ? articles : news;

  return (
    <PageWrapper>
      <HeaderSection>
        <Title>مجله تخصصی XigmaHardware</Title>
        <Subtitle>
          جدیدترین اخبار دنیای سخت‌افزار، راهنمای خرید قطعات و مقالات تخصصی دیتاسنتر را اینجا بخوانید.
        </Subtitle>
      </HeaderSection>

      <TabsContainer>
        <TabButton
          active={activeTab === 'articles'}
          onClick={() => setActiveTab('articles')}
        >
          📚 مقالات آموزشی
        </TabButton>
        <TabButton
          active={activeTab === 'news'}
          onClick={() => setActiveTab('news')}
        >
          📰 اخبار روز
        </TabButton>
      </TabsContainer>

      {currentData && currentData.length > 0 ? (
        <Grid key={activeTab}> {/* اضافه کردن key برای اجرای مجدد انیمیشن هنگام تغییر تب */}
          {currentData.map((item) => (
            <ArticleCard key={item.id} article={item} />
          ))}
        </Grid>
      ) : (
        <EmptyState>
          <h3>محتوایی یافت نشد!</h3>
          <p>به زودی مطالب جدیدی در این بخش قرار خواهد گرفت.</p>
        </EmptyState>
      )}
    </PageWrapper>
  );
}