// components/ui/Toast.js
'use client';
import { ToastContainer, toast } from 'react-toastify';

export function showToast(message, type = 'success') {
  toast[type](message, {
    position: 'top-left',
    autoClose: 3000,
    hideProgressBar: false,
    closeOnClick: true,
    pauseOnHover: true,
    draggable: true,
    rtl: true,
  });
}

export function ToastContainerStyled() {
  return (
    <ToastContainer
      toastStyle={{
        fontFamily: 'Vazirmatn, sans-serif',
        background: '#fff',
        color: '#1a1a2e',
        boxShadow: '0 4px 16px rgba(0,0,0,0.12)',
        borderRadius: '12px',
        borderRight: '4px solid #e94560',
      }}
    />
  );
}