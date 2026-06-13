// src/components/website/AboutClient.jsx
'use client';

import React from 'react';
import styled from '@emotion/styled';
import { keyframes } from '@emotion/react';

const fadeInUp = keyframes`
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
`;

const PageWrapper = styled.div`
  max-width: 1000px;
  margin: 0 auto;
  padding: 4rem 2rem;
  animation: ${fadeInUp} 0.8s ease-out forwards;
`;

const HeroSection = styled.div`
  text-align: center;
  margin-bottom: 4rem;
`;

const Title = styled.h1`
  font-size: 2.5rem;
  font-weight: 900;
  color: ${({ theme }) => theme.colors.textMain};
  margin-bottom: 1rem;

  span {
    color: ${({ theme }) => theme.colors.primary};
  }
`;

const Subtitle = styled.p`
  font-size: 1.2rem;
  color: ${({ theme }) => theme.colors.textMuted};
  max-width: 700px;
  margin: 0 auto;
  line-height: 1.6;
`;

const ContentCard = styled.div`
  background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 16px;
  padding: 3rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);

  /* استایل‌دهی به تگ‌های HTML که از بک‌اند می‌آیند */
  & .dynamic-content {
    color: ${({ theme }) => theme.colors.textMain};
    line-height: 2;
    font-size: 1.1rem;

    h2, h3 {
      color: ${({ theme }) => theme.colors.primary};
      margin-top: 2rem;
      margin-bottom: 1rem;
    }

    p {
      margin-bottom: 1.5rem;
      color: ${({ theme }) => theme.colors.textMuted};
    }

    ul, ol {
      margin-right: 2rem;
      margin-bottom: 1.5rem;

      li {
        margin-bottom: 0.5rem;
      }
    }

    strong {
      color: ${({ theme }) => theme.colors.textMain};
    }
  }

  @media (max-width: 768px) {
    padding: 1.5rem;
  }
`;

const FeaturesGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin-top: 4rem;
`;

const FeatureCard = styled.div`
  text-align: center;
  padding: 2rem;
  background-color: transparent;
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 12px;
  transition: all 0.3s ease;

  &:hover {
    border-color: ${({ theme }) => theme.colors.primary};
    background-color: ${({ theme }) => theme.colors.surface};
    transform: translateY(-5px);
  }
`;

const FeatureIcon = styled.div`
  font-size: 2.5rem;
  margin-bottom: 1rem;
`;

const FeatureTitle = styled.h3`
  color: ${({ theme }) => theme.colors.textMain};
  margin-bottom: 0.5rem;
  font-size: 1.1rem;
`;

const FeatureDesc = styled.p`
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 0.9rem;
  line-height: 1.6;
`;

export default function AboutClient({ pageData }) {
  // اگر دیتا وجود نداشت یا در حال لود بود
  if (!pageData) return null;

  return (
    <PageWrapper>
      <HeroSection>
        <Title>درباره <span>Xigma</span>Hardware</Title>
        <Subtitle>
          بزرگترین تامین‌کننده تجهیزات پردازشی، شبکه و دیتاسنتر با تضمین اصالت و بهترین قیمت در خاورمیانه.
        </Subtitle>
      </HeroSection>

      <ContentCard>
        {/* رندر کردن محتوای HTML دریافتی از سرور */}
        <div
          className="dynamic-content"
          dangerouslySetInnerHTML={{ __html: pageData.content || pageData.body || 'محتوایی یافت نشد.' }}
        />
      </ContentCard>

      <FeaturesGrid>
        <FeatureCard>
          <FeatureIcon>🛡️</FeatureIcon>
          <FeatureTitle>ضمانت اصالت کالا</FeatureTitle>
          <FeatureDesc>تمامی قطعات و سرورها با گارانتی معتبر و هولوگرام اصلی شرکت ارائه می‌شوند.</FeatureDesc>
        </FeatureCard>

        <FeatureCard>
          <FeatureIcon>⚡</FeatureIcon>
          <FeatureTitle>ارسال سریع</FeatureTitle>
          <FeatureDesc>ارسال فوری تجهیزات به سراسر کشور با بسته‌بندی کاملاً ایمن و بیمه حمل و نقل.</FeatureDesc>
        </FeatureCard>

        <FeatureCard>
          <FeatureIcon>👨‍💻</FeatureIcon>
          <FeatureTitle>پشتیبانی ۲۴ ساعته</FeatureTitle>
          <FeatureDesc>تیم فنی ما در تمام روزهای هفته آماده ارائه مشاوره تخصصی و رفع مشکلات شماست.</FeatureDesc>
        </FeatureCard>
      </FeaturesGrid>
    </PageWrapper>
  );
}