'use client';
import styled from '@emotion/styled';
import { keyframes } from '@emotion/react';

const spin = keyframes`
  to { transform: rotate(360deg); }
`;

const pulse = keyframes`
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
`;

const LoaderContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 80vh;
  gap: 1.5rem;
`;

const Spinner = styled.div`
  width: 60px;
  height: 60px;
  border: 4px solid ${({ theme }) => theme.colors.border};
  border-top-color: ${({ theme }) => theme.colors.primary};
  border-radius: 50%;
  animation: ${spin} 0.8s linear infinite;
`;

const Text = styled.div`
  color: ${({ theme }) => theme.colors.primary};
  font-size: 1.2rem;
  animation: ${pulse} 1.5s ease-in-out infinite;
`;

export default function Loading() {
  return (
    <LoaderContainer>
      <Spinner />
      <Text>در حال بارگذاری...</Text>
    </LoaderContainer>
  );
}