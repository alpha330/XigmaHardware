// src/components/auth/AuthStyles.js
import styled from '@emotion/styled';
import { keyframes } from '@emotion/react';
import Link from 'next/link';

const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
`;

export const AuthContainer = styled.div`
  min-height: calc(100vh - 80px); /* منهای ارتفاع هدر */
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: radial-gradient(circle at center, ${({ theme }) => theme.colors.surface} 0%, ${({ theme }) => theme.colors.background} 100%);
`;

export const AuthCard = styled.div`
  background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 20px;
  padding: 3rem;
  width: 100%;
  max-width: 450px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  animation: ${fadeIn} 0.5s ease-out;
`;

export const AuthTitle = styled.h1`
  font-size: 1.8rem;
  color: ${({ theme }) => theme.colors.textMain};
  margin-bottom: 0.5rem;
  text-align: center;
  font-weight: 900;
`;

export const AuthSubtitle = styled.p`
  color: ${({ theme }) => theme.colors.textMuted};
  text-align: center;
  margin-bottom: 2rem;
  font-size: 0.95rem;
`;

export const InputGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1.2rem;
`;

export const Label = styled.label`
  color: ${({ theme }) => theme.colors.textMain};
  font-size: 0.9rem;
  font-weight: bold;
`;

export const Input = styled.input`
  width: 100%; /* این خط مشکل بیرون‌زدگی را حل می‌کند */
  box-sizing: border-box; /* اطمینان از محاسبه درست پدینگ‌ها */
  background-color: ${({ theme }) => theme.colors.background};
  border: 1px solid ${({ theme }) => theme.colors.border};
  color: ${({ theme }) => theme.colors.textMain};
  padding: 0.8rem 1rem;
  border-radius: 8px;
  font-family: inherit;
  outline: none;
  transition: all 0.2s ease;
  direction: ${({ dir }) => dir || 'rtl'};

  &:focus {
    border-color: ${({ theme }) => theme.colors.primary};
    box-shadow: 0 0 0 3px ${({ theme }) => `${theme.colors.primary}33`};
  }
`;

export const SubmitButton = styled.button`
  width: 100%;
  background-color: ${({ theme }) => theme.colors.primary};
  color: #fff;
  border: none;
  padding: 1rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  margin-top: 1rem;
  transition: all 0.2s ease;

  &:hover {
    background-color: ${({ theme }) => theme.colors.secondary};
  }

  &:disabled {
    background-color: ${({ theme }) => theme.colors.border};
    cursor: not-allowed;
  }
`;

export const BottomLink = styled.div`
  text-align: center;
  margin-top: 2rem;
  font-size: 0.9rem;
  color: ${({ theme }) => theme.colors.textMuted};

  a {
    color: ${({ theme }) => theme.colors.primary};
    font-weight: bold;
    margin-right: 0.5rem;
    &:hover {
      text-decoration: underline;
    }
  }
`;

export const AlertMessage = styled.div`
  padding: 0.8rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
  text-align: center;
  background-color: ${({ type, theme }) => type === 'success' ? `${theme.colors.success}20` : `${theme.colors.error}20`};
  color: ${({ type, theme }) => type === 'success' ? theme.colors.success : theme.colors.error};
  border: 1px solid ${({ type, theme }) => type === 'success' ? theme.colors.success : theme.colors.error};
`;

export const Tabs = styled.div`
  display: flex;
  margin-bottom: 2rem;
  border-bottom: 1px solid ${({ theme }) => theme.colors.border};
`;

export const Tab = styled.button`
  flex: 1;
  background: none;
  border: none;
  padding: 0.8rem;
  font-family: inherit;
  font-weight: bold;
  cursor: pointer;
  color: ${({ active, theme }) => active ? theme.colors.primary : theme.colors.textMuted};
  border-bottom: 2px solid ${({ active, theme }) => active ? theme.colors.primary : 'transparent'};
  transition: all 0.2s ease;
`;