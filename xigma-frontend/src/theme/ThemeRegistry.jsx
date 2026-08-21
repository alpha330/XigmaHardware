// src/theme/ThemeRegistry.jsx
'use client';

import React, { useState, useEffect, createContext } from 'react';
import { useServerInsertedHTML } from 'next/navigation';
import { CacheProvider, ThemeProvider, Global, css } from '@emotion/react';
import createCache from '@emotion/cache';
import { lightTheme, darkTheme } from './colors';
import ToastProvider from '../components/ui/ToastProvider'; // اضافه شد

export const ThemeModeContext = createContext({
  isDarkMode: false,
  toggleTheme: () => {},
});


export default function ThemeRegistry({ children }) {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [mounted, setMounted] = useState(false);

  const [{ cache, flush }] = useState(() => {
    const cache = createCache({ key: 'xigma' });
    cache.compat = true;
    const prevInsert = cache.insert;
    let inserted = [];
    cache.insert = (...args) => {
      const serialized = args[1];
      if (cache.inserted[serialized.name] === undefined) {
        inserted.push(serialized.name);
      }
      return prevInsert(...args);
    };
    const flush = () => {
      const prevInserted = inserted;
      inserted = [];
      return prevInserted;
    };
    return { cache, flush };
  });

  useServerInsertedHTML(() => {
    const names = flush();
    if (names.length === 0) return null;
    let styles = '';
    for (const name of names) {
      styles += cache.inserted[name];
    }
    return (
      <style
        key={cache.key}
        data-emotion={`${cache.key} ${names.join(' ')}`}
        dangerouslySetInnerHTML={{ __html: styles }}
      />
    );
  });

  useEffect(() => {
    const storedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia?.('(prefers-color-scheme: dark)').matches;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setIsDarkMode(storedTheme ? storedTheme === 'dark' : Boolean(prefersDark));
    setMounted(true);
  }, []);

  useEffect(() => {
    document.documentElement.dataset.theme = isDarkMode ? 'dark' : 'light';
    document.documentElement.style.colorScheme = isDarkMode ? 'dark' : 'light';
  }, [isDarkMode]);

  const toggleTheme = () => {
    setIsDarkMode((prev) => {
      const newTheme = !prev;
      localStorage.setItem('theme', newTheme ? 'dark' : 'light');
      return newTheme;
    });
  };

  const theme = isDarkMode ? darkTheme : lightTheme;

  const globalStyles = css`
    :root {
      color-scheme: ${theme.mode};
      --background: ${theme.colors.background};
      --surface: ${theme.colors.surface};
      --surface-elevated: ${theme.colors.surfaceElevated};
      --input-background: ${theme.colors.inputBackground};
      --hover: ${theme.colors.hover};
      --primary: ${theme.colors.primary};
      --on-primary: ${theme.colors.onPrimary};
      --primary-light: ${theme.colors.primaryLight};
      --textMain: ${theme.colors.textMain};
      --textMuted: ${theme.colors.textMuted};
      --border: ${theme.colors.border};
      --error: ${theme.colors.error};
      --success: ${theme.colors.success};
      --warning: ${theme.colors.warning};
      --focus-ring: ${theme.colors.focusRing};
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    html {
      scroll-behavior: smooth;
      background-color: ${theme.colors.background};
    }
    body {
      background-color: ${theme.colors.background};
      color: ${theme.colors.textMain};
      transition: background-color 0.3s ease, color 0.3s ease;
      overflow-x: hidden;
      min-height: 100vh;
    }
    a {
      text-decoration: none;
      color: inherit;
    }

    button,
    input,
    textarea,
    select {
      color: ${theme.colors.textMain};
      font: inherit;
    }

    input,
    textarea,
    select {
      background-color: ${theme.colors.inputBackground};
      border-color: ${theme.colors.border};
      caret-color: ${theme.colors.primary};
    }

    input::placeholder,
    textarea::placeholder {
      color: ${theme.colors.textMuted};
      opacity: 1;
    }

    select option {
      background-color: ${theme.colors.surface};
      color: ${theme.colors.textMain};
    }

    *:focus-visible {
      outline: 2px solid ${theme.colors.primary};
      outline-offset: 2px;
    }

    ::selection {
      background: ${theme.colors.primaryLight};
      color: ${theme.colors.textMain};
    }
  `;

  // ۲. بخش return اصلاح شد تا Providerها همیشه children را رندر کنند
  return (
    <ThemeModeContext.Provider value={{ isDarkMode, toggleTheme }}>
      <CacheProvider value={cache}>
        <ThemeProvider theme={theme}>
          <Global styles={globalStyles} />

          <ToastProvider>
              {/* محتوا با یک opacity ملایم لود می‌شود تا پرش استایل نامرئی بماند */}
              <div style={{ opacity: mounted ? 1 : 0, transition: 'opacity 0.3s ease' }}>
                {children}
              </div>
          </ToastProvider>
        </ThemeProvider>
      </CacheProvider>
    </ThemeModeContext.Provider>
  );
}
