'use client';
import { Global } from '@emotion/react';
import { ThemeProvider as EmotionThemeProvider } from '@emotion/react';
import { theme } from '@/styles/theme';
import { globalStyles } from '@/styles/global';
import { AuthProvider } from '@/context/AuthContext';
import { CartProvider } from '@/context/CartContext';
import Header from './Header';
import Footer from './Footer';
import { ToastContainerStyled } from '@/components/ui/Toast';

export default function Providers({ children }) {
  return (
    <EmotionThemeProvider theme={theme}>
      <Global styles={globalStyles} />
      <AuthProvider>
        <CartProvider>
          <Header />
          {children}
          <Footer />
          <ToastContainerStyled />
        </CartProvider>
      </AuthProvider>
    </EmotionThemeProvider>
  );
}