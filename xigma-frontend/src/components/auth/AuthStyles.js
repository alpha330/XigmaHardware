// src/components/auth/AuthStyles.js
import styled from '@emotion/styled';
import { keyframes } from '@emotion/react';
import Link from 'next/link';

const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
`;

export const AuthContainer = styled.div`
  position: relative;
  isolation: isolate;
  min-height: calc(100dvh - 80px);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  padding: clamp(1.25rem, 4vw, 3.5rem) 1rem;
  background:
    radial-gradient(circle at 15% 15%, ${({ theme }) => `${theme.colors.primary}24`} 0, transparent 34%),
    radial-gradient(circle at 85% 82%, ${({ theme }) => `${theme.colors.primary}16`} 0, transparent 30%),
    ${({ theme }) => theme.colors.background};

  &::before {
    position: absolute;
    z-index: -1;
    inset: 0;
    content: '';
    opacity: ${({ theme }) => theme.mode === 'dark' ? 0.22 : 0.32};
    background-image:
      linear-gradient(${({ theme }) => `${theme.colors.border}55`} 1px, transparent 1px),
      linear-gradient(90deg, ${({ theme }) => `${theme.colors.border}55`} 1px, transparent 1px);
    background-size: 38px 38px;
    mask-image: linear-gradient(to bottom, transparent, #000 18%, #000 82%, transparent);
    -webkit-mask-image: linear-gradient(to bottom, transparent, #000 18%, #000 82%, transparent);
  }
`;

export const AuthCard = styled.div`
  position: relative;
  background: linear-gradient(
    145deg,
    ${({ theme }) => theme.colors.surfaceElevated},
    ${({ theme }) => theme.colors.surface}
  );
  border: 1px solid ${({ theme }) => theme.colors.borderStrong};
  border-radius: 24px;
  padding: clamp(1.5rem, 4vw, 3rem);
  width: 100%;
  max-width: 520px;
  box-shadow: ${({ theme }) => theme.mode === 'dark'
    ? '0 24px 70px rgba(0, 0, 0, 0.42)'
    : '0 24px 70px rgba(15, 23, 42, 0.13)'};
  animation: ${fadeIn} 0.5s ease-out;
  color: ${({ theme }) => theme.colors.textMain};

  &::before {
    position: absolute;
    inset: 0 auto auto 12%;
    width: 76%;
    height: 2px;
    border-radius: 999px;
    content: '';
    background: linear-gradient(90deg, transparent, ${({ theme }) => theme.colors.primary}, transparent);
    opacity: 0.7;
  }
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
  line-height: 1.9;
`;

export const AuthGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;

  @media (max-width: 520px) {
    grid-template-columns: 1fr;
    gap: 0;
  }
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
  font-weight: 700;
`;

export const LabelRow = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
`;

export const Input = styled.input`
  width: 100%;
  box-sizing: border-box;
  background-color: ${({ theme }) => theme.colors.inputBackground};
  border: 1px solid ${({ theme }) => theme.colors.border};
  color: ${({ theme }) => theme.colors.textMain};
  min-height: 48px;
  padding: 0.8rem 1rem;
  border-radius: 12px;
  font-family: inherit;
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
  direction: ${({ dir }) => dir || 'rtl'};

  &::placeholder {
    color: ${({ theme }) => theme.colors.textMuted};
  }

  &:hover:not(:disabled) {
    border-color: ${({ theme }) => theme.colors.borderStrong};
  }

  &:focus {
    border-color: ${({ theme }) => theme.colors.primary};
    box-shadow: 0 0 0 4px ${({ theme }) => theme.colors.focusRing};
  }

  &:-webkit-autofill,
  &:-webkit-autofill:hover,
  &:-webkit-autofill:focus {
    -webkit-text-fill-color: ${({ theme }) => theme.colors.textMain};
    -webkit-box-shadow: 0 0 0 1000px ${({ theme }) => theme.colors.inputBackground} inset;
    caret-color: ${({ theme }) => theme.colors.primary};
  }
`;

export const SubmitButton = styled.button`
  width: 100%;
  background-color: ${({ theme }) => theme.colors.primary};
  color: ${({ theme }) => theme.colors.onPrimary};
  border: 1px solid ${({ theme }) => theme.colors.primary};
  padding: 1rem;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 800;
  cursor: pointer;
  margin-top: 1rem;
  box-shadow: 0 10px 24px ${({ theme }) => `${theme.colors.primary}2E`};
  transition: transform 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;

  &:hover:not(:disabled) {
    background-color: ${({ theme }) => theme.colors.secondary};
    transform: translateY(-1px);
    box-shadow: 0 14px 30px ${({ theme }) => `${theme.colors.primary}3D`};
  }

  &:active:not(:disabled) {
    transform: translateY(0);
  }

  &:disabled {
    color: ${({ theme }) => theme.colors.textMuted};
    background-color: ${({ theme }) => theme.colors.hover};
    border-color: ${({ theme }) => theme.colors.border};
    box-shadow: none;
    cursor: not-allowed;
  }
`;

export const SecondaryButton = styled.button`
  width: 100%;
  margin-top: 0.75rem;
  padding: 0.8rem 1rem;
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 12px;
  color: ${({ theme }) => theme.colors.textMain};
  background: ${({ theme }) => theme.colors.inputBackground};
  cursor: pointer;
  font-weight: 700;
  transition: background-color 0.2s ease, border-color 0.2s ease;

  &:hover {
    border-color: ${({ theme }) => theme.colors.primary};
    background: ${({ theme }) => theme.colors.hover};
  }
`;

export const AuthInlineLink = styled(Link)`
  color: ${({ theme }) => theme.colors.primary};
  font-size: 0.82rem;
  font-weight: 700;

  &:hover {
    color: ${({ theme }) => theme.colors.secondary};
    text-decoration: underline;
  }
`;

export const AuthActionLink = styled(Link)`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: 52px;
  margin-top: 1rem;
  padding: 0.85rem 1rem;
  border: 1px solid ${({ theme }) => theme.colors.primary};
  border-radius: 12px;
  color: ${({ theme }) => theme.colors.onPrimary};
  background: ${({ theme }) => theme.colors.primary};
  box-shadow: 0 10px 24px ${({ theme }) => `${theme.colors.primary}2E`};
  font-weight: 800;
  transition: transform 0.2s ease, background-color 0.2s ease;

  &:hover {
    background: ${({ theme }) => theme.colors.secondary};
    transform: translateY(-1px);
  }

  &[data-variant='secondary'] {
    color: ${({ theme }) => theme.colors.textMain};
    border-color: ${({ theme }) => theme.colors.border};
    background: ${({ theme }) => theme.colors.inputBackground};
    box-shadow: none;

    &:hover {
      border-color: ${({ theme }) => theme.colors.primary};
      background: ${({ theme }) => theme.colors.hover};
    }
  }
`;

export const StatusIcon = styled.div`
  margin: 2rem 0;
  color: ${({ 'data-status': status, theme }) => {
    if (status === 'success') return theme.colors.success;
    if (status === 'error') return theme.colors.error;
    return theme.colors.primary;
  }};
  font-size: 3rem;
  line-height: 1;
  text-align: center;
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
  padding: 0.3rem;
  gap: 0.3rem;
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 14px;
  background: ${({ theme }) => theme.colors.inputBackground};
`;

export const Tab = styled.button`
  flex: 1;
  min-height: 42px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 10px;
  padding: 0.65rem 0.5rem;
  font-family: inherit;
  font-size: 0.88rem;
  font-weight: 800;
  cursor: pointer;
  color: ${({ theme }) => theme.colors.textMuted};
  transition: color 0.2s ease, background-color 0.2s ease, border-color 0.2s ease;

  &:hover {
    color: ${({ theme }) => theme.colors.textMain};
    background: ${({ theme }) => theme.colors.hover};
  }

  &[aria-pressed='true'] {
    color: ${({ theme }) => theme.colors.primary};
    border-color: ${({ theme }) => `${theme.colors.primary}4D`};
    background: ${({ theme }) => theme.colors.primaryLight};
  }
`;
