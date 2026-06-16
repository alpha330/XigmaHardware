// src/components/shared/PageLoader.jsx
'use client';

import React from 'react';
import styled from '@emotion/styled';
import { keyframes } from '@emotion/react';


// ================= ANIMATIONS =================
const spin = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`;

const pulse = keyframes`
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
`;

// ================= STYLES =================
const LoaderWrapper = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  /* اگر fullHeight پاس داده شود، کل ارتفاع صفحه را می‌گیرد، در غیر این صورت یک ارتفاع حداقلی دارد */
  min-height: ${({ fullHeight }) => (fullHeight ? '70vh' : '300px')};
  gap: 1.5rem;
`;

const SpinnerRing = styled.div`
  width: 50px;
  height: 50px;
  border: 4px solid ${({ theme }) => theme.colors.border};
  border-top: 4px solid ${({ theme }) => theme.colors.primary};
  border-radius: 50%;
  animation: ${spin} 1s linear infinite;

  /* افکت سایه برای جذابیت بیشتر */
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
`;

const LoadingText = styled.p`
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 1.1rem;
  font-weight: bold;
  letter-spacing: 0.5px;
  animation: ${pulse} 1.5s ease-in-out infinite;
`;

// ================= COMPONENT =================
export default function PageLoader({ text = 'در حال دریافت اطلاعات...', fullHeight = false }) {
  return (
    <LoaderWrapper fullHeight={fullHeight}>
      <SpinnerRing />
      <LoadingText>{text}</LoadingText>
    </LoaderWrapper>
  );
}