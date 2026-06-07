// src/lib/ThemeContext.js
'use client';

import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { ThemeProvider as EmotionThemeProvider } from '@emotion/react';
import { lightTheme, darkTheme } from '@/styles/theme';

const ThemeModeContext = createContext(null);

export const useThemeMode = () => {
  const context = useContext(ThemeModeContext);
  // ✅ فقط warning به جای throw
  if (!context) {
    if (typeof window !== 'undefined') {
      console.warn('useThemeMode must be used within ThemeModeProvider');
    }
    return {
      mode: 'light',
      toggleTheme: () => {},
      isDark: false,
      isLight: true,
      setLightTheme: () => {},
      setDarkTheme: () => {},
    };
  }
  return context;
};

export const ThemeModeProvider = ({ children }) => {
  const [mode, setMode] = useState('light');
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    try {
      const saved = localStorage.getItem('xigma-theme-mode');
      if (saved) {
        setMode(saved);
      } else {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        setMode(prefersDark ? 'dark' : 'light');
      }
    } catch {
      // localStorage در دسترس نیست
    }
    setMounted(true);
  }, []);

  useEffect(() => {
    if (mounted) {
      try {
        localStorage.setItem('xigma-theme-mode', mode);
      } catch {}
    }
  }, [mode, mounted]);

  const toggleTheme = useCallback(() => {
    setMode(prev => prev === 'light' ? 'dark' : 'light');
  }, []);

  const setLightTheme = useCallback(() => setMode('light'), []);
  const setDarkTheme = useCallback(() => setMode('dark'), []);

  const currentTheme = mode === 'dark' ? darkTheme : lightTheme;

  return (
    <ThemeModeContext.Provider
      value={{
        mode,
        toggleTheme,
        setLightTheme,
        setDarkTheme,
        isDark: mode === 'dark',
        isLight: mode === 'light',
      }}
    >
      <EmotionThemeProvider theme={currentTheme}>
        {children}
      </EmotionThemeProvider>
    </ThemeModeContext.Provider>
  );
};