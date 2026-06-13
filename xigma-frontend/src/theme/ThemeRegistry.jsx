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
    // خواندن تم از مرورگر کاربر پس از لود شدن
    const storedTheme = localStorage.getItem('theme');
    if (storedTheme === 'dark') {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setIsDarkMode(true);
    }
    setMounted(true);
  }, []);

  const toggleTheme = () => {
    setIsDarkMode((prev) => {
      const newTheme = !prev;
      localStorage.setItem('theme', newTheme ? 'dark' : 'light');
      return newTheme;
    });
  };

  const theme = isDarkMode ? darkTheme : lightTheme;

  const globalStyles = css`
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    html {
      scroll-behavior: smooth;
    }
    body {
      background-color: ${theme.colors.background};
      color: ${theme.colors.textMain};
      transition: background-color 0.3s ease, color 0.3s ease;
      overflow-x: hidden;
    }
    a {
      text-decoration: none;
      color: inherit;
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