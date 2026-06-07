// src/app/layout.js
'use client';

import { Global, useTheme } from '@emotion/react';
import { globalStyles } from '@/styles/global';
import { ThemeModeProvider, useThemeMode } from '@/lib/ThemeContext';
import { ToastProvider } from '@/components/ui/Toast';
import '@/lib/fontawesome';

// ✅ همه چی توی Provider باشه
function LayoutContent({ children }) {
  const theme = useTheme();
  return (
    <>
      <Global styles={globalStyles(theme)} />
      {children}
    </>
  );
}

export default function RootLayout({ children }) {
  return (
    <html lang="fa" dir="rtl" suppressHydrationWarning>
      <head>
        <title>XigmaHardware</title>
        <meta name="description" content="marketplace سخت‌افزارهای سازمانی" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      </head>
      <body>
        <ThemeModeProvider>
          <ToastProvider>
            <LayoutContent>{children}</LayoutContent>
          </ToastProvider>
        </ThemeModeProvider>
      </body>
    </html>
  );
}