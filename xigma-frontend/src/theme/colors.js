// src/theme/colors.js

const sharedColors = {
  white: '#FFFFFF',
};

export const lightTheme = {
  mode: 'light',
  colors: {
    ...sharedColors,
    background: '#F8FAFC',
    surface: '#FFFFFF',
    surfaceElevated: '#FFFFFF',
    surfaceTranslucent: 'rgba(255, 255, 255, 0.88)',
    inputBackground: '#FFFFFF',
    hover: '#EFF6FF',
    primary: '#0056D2',
    primaryLight: '#DBEAFE',
    secondary: '#003B8E',
    textMain: '#111827',
    textPrimary: '#111827',
    textSecondary: '#475569',
    textMuted: '#64748B',
    border: '#E2E8F0',
    borderStrong: '#CBD5E1',
    error: '#EF4444',
    errorSurface: '#FEF2F2',
    success: '#10B981',
    warning: '#D97706',
    focusRing: 'rgba(0, 86, 210, 0.22)',
    overlay: 'rgba(15, 23, 42, 0.58)',
  }
};

export const darkTheme = {
  mode: 'dark',
  colors: {
    ...sharedColors,
    background: '#0B1120',
    surface: '#111827',
    surfaceElevated: '#182235',
    surfaceTranslucent: 'rgba(17, 24, 39, 0.9)',
    inputBackground: '#0F172A',
    hover: '#1E293B',
    primary: '#60A5FA',
    primaryLight: '#172554',
    secondary: '#93C5FD',
    textMain: '#F8FAFC',
    textPrimary: '#F8FAFC',
    textSecondary: '#CBD5E1',
    textMuted: '#94A3B8',
    border: '#334155',
    borderStrong: '#475569',
    error: '#F87171',
    errorSurface: '#3F1D24',
    success: '#34D399',
    warning: '#FBBF24',
    focusRing: 'rgba(96, 165, 250, 0.28)',
    overlay: 'rgba(2, 6, 23, 0.76)',
  }
};
