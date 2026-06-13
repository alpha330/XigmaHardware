// src/components/layout/Footer.jsx
'use client';

import React from 'react';
import styled from '@emotion/styled';
import Link from 'next/link';

const FooterWrapper = styled.footer`
  background-color: ${({ theme }) => theme.colors.surface};
  border-top: 1px solid ${({ theme }) => theme.colors.border};
  padding: 3rem 2rem 1rem;
  margin-top: auto;
`;

const FooterGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
`;

const FooterCol = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const Title = styled.h3`
  color: ${({ theme }) => theme.colors.primary};
  margin-bottom: 0.5rem;
`;

const FooterLink = styled(Link)`
  color: ${({ theme }) => theme.colors.textMuted};
  transition: color 0.2s ease;

  &:hover {
    color: ${({ theme }) => theme.colors.primary};
  }
`;

const Copyright = styled.div`
  text-align: center;
  margin-top: 3rem;
  padding-top: 1rem;
  border-top: 1px solid ${({ theme }) => theme.colors.border};
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 0.9rem;
`;

export default function Footer() {
  return (
    <FooterWrapper>
      <FooterGrid>
        <FooterCol>
          <Title>XigmaHardware</Title>
          <p style={{ color: 'var(--textMuted)' }}>
            بزرگترین مرجع تخصصی فروش سرور، تجهیزات دیتاسنتر و قطعات کامپیوتری در ایران.
          </p>
        </FooterCol>

        <FooterCol>
          <Title>دسترسی سریع</Title>
          <FooterLink href="/market">محصولات</FooterLink>
          <FooterLink href="/about">درباره ما</FooterLink>
          <FooterLink href="/terms">قوانین و مقررات</FooterLink>
        </FooterCol>

        <FooterCol>
          <Title>پشتیبانی</Title>
          <FooterLink href="/support/faq">سوالات متداول</FooterLink>
          <FooterLink href="/support/tickets">تیکت پشتیبانی</FooterLink>
          <FooterLink href="/support/warranties">استعلام گارانتی</FooterLink>
        </FooterCol>
      </FooterGrid>

      <Copyright>
        © {new Date().getFullYear()} تمامی حقوق برای XigmaHardware محفوظ است.
      </Copyright>
    </FooterWrapper>
  );
}