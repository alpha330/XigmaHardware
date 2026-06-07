// src/components/ui/Toast.js
'use client';

import { createContext, useContext, useState, useCallback } from 'react';
import styled from '@emotion/styled';
import { keyframes } from '@emotion/react';

// ==================== Context ====================

const ToastContext = createContext(null);

export const useToast = () => useContext(ToastContext);

// ==================== Animations ====================

const slideIn = keyframes`
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
`;

const slideOut = keyframes`
  from { transform: translateX(0); opacity: 1; }
  to { transform: translateX(100%); opacity: 0; }
`;

// ==================== Styled Components ====================

const ToastContainer = styled.div`
  position: fixed;
  top: 20px;
  left: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 400px;
`;

const getToastColors = (type, theme) => {
  const isDark = theme.mode === 'dark';

  const colors = {
    success: {
      bg: isDark ? '#064e3b' : '#ecfdf5',
      border: isDark ? '#10b981' : '#10b981',
      text: isDark ? '#d1fae5' : '#064e3b',
      icon: '✅',
    },
    error: {
      bg: isDark ? '#7f1d1d' : '#fef2f2',
      border: isDark ? '#ef4444' : '#ef4444',
      text: isDark ? '#fee2e2' : '#7f1d1d',
      icon: '❌',
    },
    warning: {
      bg: isDark ? '#78350f' : '#fffbeb',
      border: isDark ? '#f59e0b' : '#f59e0b',
      text: isDark ? '#fef3c7' : '#78350f',
      icon: '⚠️',
    },
    info: {
      bg: isDark ? '#1e3a5f' : '#eff6ff',
      border: isDark ? '#3b82f6' : '#3b82f6',
      text: isDark ? '#dbeafe' : '#1e3a5f',
      icon: 'ℹ️',
    },
    purple: {
      bg: isDark ? '#3b0764' : '#faf5ff',
      border: isDark ? '#a855f7' : '#a855f7',
      text: isDark ? '#e9d5ff' : '#3b0764',
      icon: '🛒',
    },
  };

  return colors[type] || colors.info;
};

const ToastItem = styled.div`
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px 20px;
  background: ${props => getToastColors(props.$type, props.theme).bg};
  border: 1px solid ${props => getToastColors(props.$type, props.theme).border};
  border-right: 4px solid ${props => getToastColors(props.$type, props.theme).border};
  border-radius: ${props => props.theme.borderRadius.md};
  color: ${props => getToastColors(props.$type, props.theme).text};
  font-size: ${props => props.theme.fontSizes.sm};
  box-shadow: ${props => props.theme.shadows.lg};
  animation: ${props => props.$exiting ? slideOut : slideIn} 0.3s ease-out;
  min-width: 300px;
  backdrop-filter: blur(10px);
`;

const ToastIcon = styled.span`
  font-size: 1.2rem;
  flex-shrink: 0;
`;

const ToastContent = styled.div`
  flex: 1;
`;

const ToastTitle = styled.div`
  font-weight: 600;
  margin-bottom: 2px;
`;

const ToastMessage = styled.div`
  font-weight: 400;
  opacity: 0.9;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  cursor: pointer;
  color: inherit;
  opacity: 0.5;
  padding: 4px;
  font-size: 1rem;
  transition: opacity 0.2s;

  &:hover {
    opacity: 1;
  }
`;

// ==================== Toast Provider ====================

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((message, type = 'info', title = '', duration = 4000) => {
    const id = Date.now() + Math.random();

    setToasts(prev => [...prev, { id, message, type, title, exiting: false }]);

    setTimeout(() => {
      setToasts(prev => prev.map(t => t.id === id ? { ...t, exiting: true } : t));
      setTimeout(() => {
        setToasts(prev => prev.filter(t => t.id !== id));
      }, 300);
    }, duration);
  }, []);

  const success = useCallback((message, title = 'موفق') => addToast(message, 'success', title), [addToast]);
  const error = useCallback((message, title = 'خطا') => addToast(message, 'error', title, 6000), [addToast]);
  const warning = useCallback((message, title = 'هشدار') => addToast(message, 'warning', title), [addToast]);
  const info = useCallback((message, title = 'اطلاع') => addToast(message, 'info', title), [addToast]);
  const purple = useCallback((message, title = 'Xigma') => addToast(message, 'purple', title), [addToast]);

  return (
    <ToastContext.Provider value={{ success, error, warning, info, purple }}>
      {children}
      <ToastContainer>
        {toasts.map(toast => (
          <ToastItem key={toast.id} $type={toast.type} $exiting={toast.exiting}>
            <ToastIcon>{getToastColors(toast.type, { mode: 'light' }).icon}</ToastIcon>
            <ToastContent>
              {toast.title && <ToastTitle>{toast.title}</ToastTitle>}
              <ToastMessage>{toast.message}</ToastMessage>
            </ToastContent>
            <CloseButton onClick={() => {
              setToasts(prev => prev.map(t => t.id === toast.id ? { ...t, exiting: true } : t));
              setTimeout(() => setToasts(prev => prev.filter(t => t.id !== toast.id)), 300);
            }}>
              ✕
            </CloseButton>
          </ToastItem>
        ))}
      </ToastContainer>
    </ToastContext.Provider>
  );
};