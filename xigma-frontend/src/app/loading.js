// src/app/loading.js
'use client';

import styled from '@emotion/styled';
import { keyframes } from '@emotion/react';

// انیمیشن چرخش و پالس
const spinAndPulse = keyframes`
  0% { transform: scale(0.8) rotate(0deg); opacity: 0.5; }
  50% { transform: scale(1.1) rotate(180deg); opacity: 1; }
  100% { transform: scale(0.8) rotate(360deg); opacity: 0.5; }
`;

const textPulse = keyframes`
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
`;

const LoaderContainer = styled.div`
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
  width: 100vw;
  background-color: ${({ theme }) => theme.colors.background};
  position: fixed;
  top: 0;
  left: 0;
  z-index: 9999;
`;

const LoaderCircle = styled.div`
  width: 60px;
  height: 60px;
  border: 4px solid ${({ theme }) => theme.colors.border};
  border-top: 4px solid ${({ theme }) => theme.colors.primary};
  border-radius: 50%;
  animation: ${spinAndPulse} 1.5s cubic-bezier(0.4, 0, 0.2, 1) infinite;
  margin-bottom: 20px;
`;

const LoaderText = styled.h2`
  color: ${({ theme }) => theme.colors.primary};
  font-size: 1.2rem;
  letter-spacing: 2px;
  animation: ${textPulse} 1.5s ease-in-out infinite;
`;

export default function Loading() {
  return (
    <LoaderContainer>
      <LoaderCircle />
      <LoaderText>XigmaHardware</LoaderText>
    </LoaderContainer>
  );
}