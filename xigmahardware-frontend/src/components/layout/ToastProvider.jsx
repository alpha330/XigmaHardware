'use client';
import { createContext, useContext, useState, useCallback } from 'react';
import styled from '@emotion/styled';
import { keyframes } from '@emotion/react';

const ToastContext = createContext();
export const useToast = () => useContext(ToastContext);

const slideIn = keyframes`
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
`;

const ToastContainer = styled.div`
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
`;

const ToastMessage = styled.div`
  background: ${({ type, theme }) =>
    type === 'success' ? theme.colors.success :
    type === 'error' ? theme.colors.error : theme.colors.primary};
  color: white;
  padding: 1rem 1.5rem;
  border-radius: ${({ theme }) => theme.radius};
  box-shadow: ${({ theme }) => theme.shadows.lg};
  animation: ${slideIn} 0.4s ease-out;
  font-size: 0.9rem;
`;

export default function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((message, type = 'info', duration = 4000) => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, duration);
  }, []);

  return (
    <ToastContext.Provider value={{ addToast }}>
      {children}
      <ToastContainer>
        {toasts.map(toast => (
          <ToastMessage key={toast.id} type={toast.type}>
            {toast.message}
          </ToastMessage>
        ))}
      </ToastContainer>
    </ToastContext.Provider>
  );
}