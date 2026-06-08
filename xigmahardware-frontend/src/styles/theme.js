// src/styles/theme.js

// ============================================================
// پالت رنگی مشترک برای هر دو تم
// ============================================================
const palette = {
  brand: {
    50: '#faf5ff',
    100: '#f3e8ff',
    200: '#e9d5ff',
    300: '#d8b4fe',
    400: '#c084fc',
    500: '#8b5cf6',   // Main
    600: '#7c3aed',
    700: '#6d28d9',
    800: '#5b21b6',
    900: '#4c1d95',
  },
  success: '#10b981',
  warning: '#f59e0b',
  danger:  '#ef4444',
  info:    '#3b82f6',
};

// ============================================================
// مقادیر پایه که بین دو تم مشترک هستند
// ============================================================
const base = {
  fonts: {
    primary: "'Vazirmatn', sans-serif",
    number:  "'Vazirmatn', sans-serif",
  },
  fontSizes: {
    xs:   '0.75rem',
    sm:   '0.875rem',
    base: '1rem',
    lg:   '1.125rem',
    xl:   '1.25rem',
    '2xl':'1.5rem',
    '3xl':'1.875rem',
    '4xl':'2.25rem',
    '5xl':'3rem',
    '6xl':'3.75rem',
  },
  spacing: {
    0:  '0',
    1:  '4px',
    2:  '8px',
    3:  '12px',
    4:  '16px',
    5:  '20px',
    6:  '24px',
    8:  '32px',
    10: '40px',
    12: '48px',
    16: '64px',
    20: '80px',
  },
  borderRadius: {
    none: '0',
    sm:   '4px',
    md:   '8px',
    lg:   '12px',
    xl:   '16px',
    '2xl':'24px',
    full: '9999px',
  },
  shadows: {
    none: 'none',
    sm:   '0 1px 2px rgba(0,0,0,0.04)',
    md:   '0 4px 6px rgba(0,0,0,0.06)',
    lg:   '0 10px 25px rgba(0,0,0,0.08)',
    xl:   '0 20px 50px rgba(0,0,0,0.12)',
    glow: '0 0 30px rgba(139, 92, 246, 0.3)',
  },
  transitions: {
    fast:   '150ms cubic-bezier(0.4, 0, 0.2, 1)',
    normal: '250ms cubic-bezier(0.4, 0, 0.2, 1)',
    slow:   '400ms cubic-bezier(0.4, 0, 0.2, 1)',
  },
  breakpoints: {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl':'1536px',
  },
};

// ============================================================
// تم روشن
// ============================================================
export const lightTheme = {
  ...base,
  mode: 'light',
  colors: {
    // نام‌های مستعار برای حفظ سازگاری با کامپوننت‌های قدیمی
    primary: palette.brand,
    brand:   palette.brand,
    gray: {
      50: '#f8fafc', 100: '#f1f5f9', 200: '#e2e8f0',
      300: '#cbd5e1', 400: '#94a3b8', 500: '#64748b',
      600: '#475569', 700: '#334155', 800: '#1e293b', 900: '#0f172a',
    },
    steel: {
      50: '#f8fafc', 100: '#f1f5f9', 200: '#e2e8f0',
      300: '#cbd5e1', 400: '#94a3b8', 500: '#64748b',
      600: '#475569', 700: '#334155', 800: '#1e293b', 900: '#0f172a',
    },
    success: palette.success,
    warning: palette.warning,
    danger:  palette.danger,
    info:    palette.info,

    bg: {
      primary:   '#ffffff',
      secondary: '#f8fafc',
      tertiary:  '#f1f5f9',
      dark:      '#0f172a',
    },
    text: {
      primary:   '#0f172a',
      secondary: '#475569',
      muted:     '#94a3b8',
      inverse:   '#ffffff',
    },
    surface: {
      card:    '#ffffff',
      elevated:'#ffffff',
      overlay: 'rgba(15, 23, 42, 0.5)',
    },
    border: {
      light:  '#e2e8f0',
      medium: '#cbd5e1',
      dark:   '#94a3b8',
    },
  },
};

// ============================================================
// تم تاریک
// ============================================================
export const darkTheme = {
  ...base,
  mode: 'dark',
  colors: {
    primary: palette.brand,
    brand:   palette.brand,
    gray: {
      50: '#0f172a', 100: '#1e293b', 200: '#334155',
      300: '#475569', 400: '#64748b', 500: '#94a3b8',
      600: '#cbd5e1', 700: '#e2e8f0', 800: '#f1f5f9', 900: '#f8fafc',
    },
    steel: {
      50: '#0f172a', 100: '#1e293b', 200: '#334155',
      300: '#475569', 400: '#64748b', 500: '#94a3b8',
      600: '#cbd5e1', 700: '#e2e8f0', 800: '#f1f5f9', 900: '#f8fafc',
    },
    success: palette.success,
    warning: palette.warning,
    danger:  palette.danger,
    info:    palette.info,

    bg: {
      primary:   '#0f172a',
      secondary: '#1e293b',
      tertiary:  '#334155',
      dark:      '#020617',
    },
    text: {
      primary:   '#f1f5f9',
      secondary: '#cbd5e1',
      muted:     '#64748b',
      inverse:   '#0f172a',
    },
    surface: {
      card:     '#1e293b',
      elevated: '#334155',
      overlay:  'rgba(2, 6, 23, 0.7)',
    },
    border: {
      light:  '#334155',
      medium: '#475569',
      dark:   '#64748b',
    },
  },
};