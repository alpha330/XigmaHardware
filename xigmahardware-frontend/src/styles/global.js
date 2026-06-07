// src/styles/global.js
import { css } from '@emotion/react';
import { fontFaces } from './fonts';

export const globalStyles = (theme) => css`
  ${fontFaces}

  *, *::before, *::after {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  html {
    direction: rtl;
    font-size: 16px;
    scroll-behavior: smooth;
  }

  body {
    font-family: ${theme.fonts.primary};
    font-weight: 400;
    color: ${theme.colors.text.primary};
    background-color: ${theme.colors.bg.secondary};
    line-height: 1.8;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    transition: background-color 0.3s ease, color 0.3s ease;
  }

  /* ==================== Scrollbar ==================== */
  ::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }

  ::-webkit-scrollbar-track {
    background: ${theme.colors.gray[100]};
  }

  ::-webkit-scrollbar-thumb {
    background: ${theme.colors.primary[300]};
    border-radius: ${theme.borderRadius.full};
  }

  ::-webkit-scrollbar-thumb:hover {
    background: ${theme.colors.primary[500]};
  }

  /* ==================== Links ==================== */
  a {
    color: ${theme.colors.primary[500]};
    text-decoration: none;
    transition: color ${theme.transitions.fast};
  }

  a:hover {
    color: ${theme.colors.primary[600]};
  }

  /* ==================== Selection ==================== */
  ::selection {
    background-color: ${theme.colors.primary[300]};
    color: ${theme.colors.text.inverse};
  }

  /* ==================== Typography ==================== */
  h1, h2, h3, h4, h5, h6 {
    font-family: ${theme.fonts.primary};
    font-weight: 700;
    line-height: 1.5;
    color: ${theme.colors.text.primary};
  }

  h1 { font-size: ${theme.fontSizes['4xl']}; }
  h2 { font-size: ${theme.fontSizes['3xl']}; }
  h3 { font-size: ${theme.fontSizes['2xl']}; }
  h4 { font-size: ${theme.fontSizes.xl}; }

  p {
    color: ${theme.colors.text.secondary};
    line-height: 1.8;
  }

  .numbers {
    font-family: ${theme.fonts.number};
  }

  /* ==================== Animations ==================== */
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }

  @keyframes slideUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
  }

  @keyframes slideInRight {
    from { opacity: 0; transform: translateX(30px); }
    to { opacity: 1; transform: translateX(0); }
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }

  @keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
  }

  .animate-fade-in {
    animation: fadeIn 0.5s ease-out;
  }

  .animate-slide-up {
    animation: slideUp 0.6s ease-out;
  }

  .animate-slide-in-right {
    animation: slideInRight 0.4s ease-out;
  }

  /* ==================== Utility Classes ==================== */
  .glass {
    background: ${theme.mode === 'dark'
      ? 'rgba(26, 26, 46, 0.8)'
      : 'rgba(255, 255, 255, 0.8)'
    };
    backdrop-filter: blur(10px);
    border: 1px solid ${theme.mode === 'dark'
      ? 'rgba(168, 85, 247, 0.2)'
      : 'rgba(168, 85, 247, 0.1)'
    };
  }

  .gradient-text {
    background: linear-gradient(135deg, ${theme.colors.primary[400]}, ${theme.colors.primary[600]});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .gradient-bg {
    background: linear-gradient(135deg, ${theme.colors.primary[500]}, ${theme.colors.primary[700]});
  }

  .card-hover {
    transition: all ${theme.transitions.normal};
  }

  .card-hover:hover {
    transform: translateY(-4px);
    box-shadow: ${theme.shadows.lg};
  }

  /* ==================== Skeleton Loading ==================== */
  .skeleton {
    background: linear-gradient(90deg,
      ${theme.colors.gray[200]} 25%,
      ${theme.colors.gray[100]} 50%,
      ${theme.colors.gray[200]} 75%
    );
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: ${theme.borderRadius.sm};
  }

  /* ==================== Focus ==================== */
  :focus-visible {
    outline: 2px solid ${theme.colors.primary[500]};
    outline-offset: 2px;
    border-radius: 4px;
  }

  /* ==================== Input Autofill ==================== */
  input:-webkit-autofill,
  input:-webkit-autofill:hover,
  input:-webkit-autofill:focus {
    -webkit-box-shadow: 0 0 0 30px ${theme.colors.bg.primary} inset !important;
    -webkit-text-fill-color: ${theme.colors.text.primary} !important;
    caret-color: ${theme.colors.text.primary};
    transition: background-color 5000s ease-in-out 0s;
  }

  /* ==================== Print ==================== */
  @media print {
    body {
      background: white;
      color: black;
    }

    .no-print {
      display: none !important;
    }
  }

  /* ==================== Responsive ==================== */
  @media (max-width: 768px) {
    html {
      font-size: 14px;
    }
  }

  @media (max-width: 480px) {
    html {
      font-size: 13px;
    }
  }
`;