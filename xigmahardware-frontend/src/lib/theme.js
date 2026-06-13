export const lightTheme = {
  colors: {
    primary: '#1a56db',      // آبی
    secondary: '#1e293b',    // مشکی مایل به آبی
    background: '#ffffff',
    surface: '#f8fafc',
    text: '#0f172a',
    textSecondary: '#64748b',
    border: '#e2e8f0',
    success: '#10b981',
    error: '#ef4444',
    warning: '#f59e0b',
    headerBg: '#0f172a',
    footerBg: '#1e293b',
  },
  shadows: {
    sm: '0 1px 3px rgba(0,0,0,0.1)',
    md: '0 4px 6px rgba(0,0,0,0.1)',
    lg: '0 10px 30px rgba(0,0,0,0.15)',
  },
  radius: '8px',
  font: "'Vazirmatn', sans-serif",
};

export const darkTheme = {
  ...lightTheme,
  colors: {
    ...lightTheme.colors,
    background: '#0f172a',
    surface: '#1e293b',
    text: '#f1f5f9',
    textSecondary: '#94a3b8',
    border: '#334155',
    headerBg: '#020617',
    footerBg: '#020617',
  },
};