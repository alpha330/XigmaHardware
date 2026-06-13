// src/components/ui/ToastProvider.jsx
'use client';

import React, { createContext, useContext, useState, useCallback } from 'react';
import styled from '@emotion/styled';
import { keyframes } from '@emotion/react';

const ToastContext = createContext();

export const useToast = () => useContext(ToastContext);

// انیمیشن ورود و خروج نرم
const slideIn = keyframes`
  0% { transform: translateX(100%); opacity: 0; }
  10% { transform: translateX(0); opacity: 1; }
  90% { transform: translateX(0); opacity: 1; }
  100% { transform: translateX(100%); opacity: 0; }
`;

const ToastContainer = styled.div`
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 12px;
  pointer-events: none; /* تا مزاحم کلیک‌های صفحه نشود */
`;

const ToastMessage = styled.div`
  min-width: 280px;
  max-width: 400px;
  padding: 1rem 1.2rem;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
  background-color: ${({ theme }) => theme.colors.surface};
  color: ${({ theme }) => theme.colors.textMain};
  /* حاشیه رنگی سمت راست بر اساس نوع پیام */
  border-right: 4px solid ${({ type, theme }) => type === 'success' ? theme.colors.success : theme.colors.error};
  border-left: 1px solid ${({ theme }) => theme.colors.border};
  border-top: 1px solid ${({ theme }) => theme.colors.border};
  border-bottom: 1px solid ${({ theme }) => theme.colors.border};
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  animation: ${slideIn} 4s ease-in-out forwards;
  pointer-events: auto;
`;

const Icon = styled.span`
  font-size: 1.2rem;
`;

export default function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  // تابع اضافه کردن Toast جدید
  const showToast = useCallback((message, type = 'success') => {
    const id = Math.random().toString(36).substr(2, 9);
    setToasts((prev) => [...prev, { id, message, type }]);

    // حذف خودکار بعد از 4 ثانیه (همگام با انیمیشن)
    setTimeout(() => {
      setToasts((prev) => prev.filter((toast) => toast.id !== id));
    }, 4000);
  }, []);

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      <ToastContainer>
        {toasts.map((toast) => (
          <ToastMessage key={toast.id} type={toast.type}>
            <Icon>{toast.type === 'success' ? '✅' : '❌'}</Icon>
            <span style={{ fontSize: '0.95rem', fontWeight: 'bold' }}>{toast.message}</span>
          </ToastMessage>
        ))}
      </ToastContainer>
    </ToastContext.Provider>
  );
}