// src/styles/theme.js

const baseTheme = {
  fonts: {
    primary: "'Vazirmatn', sans-serif",
    number: "'Vazirmatn', sans-serif",
  },
  fontSizes: {
    xs: '0.75rem', sm: '0.875rem', base: '1rem', lg: '1.125rem',
    xl: '1.25rem', '2xl': '1.5rem', '3xl': '1.875rem', '4xl': '2.25rem', '5xl': '3rem',
  },
  borderRadius: { sm: '8px', md: '12px', lg: '16px', xl: '24px', full: '9999px' },
  shadows: {
    sm: '0 1px 2px rgba(0,0,0,0.05)',
    md: '0 4px 6px rgba(0,0,0,0.1)',
    lg: '0 10px 25px rgba(147, 51, 234, 0.15)',
    xl: '0 20px 50px rgba(147, 51, 234, 0.2)',
    glow: '0 0 20px rgba(168, 85, 247, 0.4)',
  },
  transitions: { fast: '150ms', normal: '250ms', slow: '350ms' },
};

export const lightTheme = {
  ...baseTheme,
  mode: 'light',
  colors: {
    primary: {
      50: '#faf5ff', 100: '#f3e8ff', 200: '#e9d5ff', 300: '#d8b4fe',
      400: '#c084fc', 500: '#a855f7', 600: '#9333ea', 700: '#7e22ce',
      800: '#6b21a8', 900: '#581c87',
    },
    gray: {
      50: '#fafafa', 100: '#f5f5f5', 200: '#e5e5e5', 300: '#d4d4d4',
      400: '#a3a3a3', 500: '#737373', 600: '#525252', 700: '#404040',
      800: '#262626', 900: '#171717',
    },
    success: '#10b981', warning: '#f59e0b', danger: '#ef4444', info: '#3b82f6',
    bg: { primary: '#ffffff', secondary: '#fafafa', dark: '#1a1a2e' },
    text: { primary: '#171717', secondary: '#525252', muted: '#a3a3a3', inverse: '#ffffff' },
    card: '#ffffff',
    border: '#e5e5e5',
  },
};

export const darkTheme = {
  ...baseTheme,
  mode: 'dark',
  colors: {
    primary: {
      50: '#3b0764', 100: '#4c1d95', 200: '#5b21b6', 300: '#6d28d9',
      400: '#7c3aed', 500: '#a855f7', 600: '#c084fc', 700: '#d8b4fe',
      800: '#e9d5ff', 900: '#f3e8ff',
    },
    gray: {
      50: '#171717', 100: '#262626', 200: '#404040', 300: '#525252',
      400: '#737373', 500: '#a3a3a3', 600: '#d4d4d4', 700: '#e5e5e5',
      800: '#f5f5f5', 900: '#fafafa',
    },
    success: '#34d399', warning: '#fbbf24', danger: '#f87171', info: '#60a5fa',
    bg: { primary: '#0f0f1a', secondary: '#1a1a2e', dark: '#0a0a15' },
    text: { primary: '#fafafa', secondary: '#d4d4d4', muted: '#737373', inverse: '#171717' },
    card: '#1a1a2e',
    border: '#262640',
  },
};