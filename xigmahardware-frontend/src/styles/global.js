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
    line-height: 1.7;
    -webkit-font-smoothing: antialiased;
    transition: background-color 0.3s ease, color 0.3s ease;
  }

  /* Scrollbar Industrial */
  ::-webkit-scrollbar { width: 6px; height: 6px; }
  ::-webkit-scrollbar-track { background: ${theme.colors.bg.tertiary}; }
  ::-webkit-scrollbar-thumb {
    background: ${theme.colors.steel[400]};
    border-radius: 3px;
  }
  ::-webkit-scrollbar-thumb:hover { background: ${theme.colors.brand[500]}; }

  /* Selection */
  ::selection {
    background: ${theme.colors.brand[200]};
    color: ${theme.colors.brand[900]};
  }

  /* Typography */
  h1, h2, h3, h4, h5, h6 {
    font-weight: 700;
    line-height: 1.4;
    color: ${theme.colors.text.primary};
  }
  h1 { font-size: 2.5rem; }
  h2 { font-size: 2rem; }
  h3 { font-size: 1.5rem; }
  h4 { font-size: 1.25rem; }

  p { color: ${theme.colors.text.secondary}; line-height: 1.8; }

  /* Links */
  a {
    color: ${theme.colors.brand[600]};
    text-decoration: none;
    transition: color ${theme.transitions.fast};
  }
  a:hover { color: ${theme.colors.brand[700]}; }

  /* Focus */
  :focus-visible {
    outline: 2px solid ${theme.colors.brand[500]};
    outline-offset: 2px;
    border-radius: 2px;
  }

  /* Animations */
  @keyframes fadeInUp {
    from { opacity: 0; transform: translateY(16px); }
    to { opacity: 1; transform: translateY(0); }
  }
  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }
  @keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
  }

  .animate-fade-in { animation: fadeIn 0.4s ease-out; }
  .animate-fade-in-up { animation: fadeInUp 0.5s ease-out; }

  /* Skeleton */
  .skeleton {
    background: linear-gradient(90deg,
      ${theme.colors.steel[200]} 25%,
      ${theme.colors.steel[100]} 50%,
      ${theme.colors.steel[200]} 75%
    );
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: ${theme.borderRadius.sm};
  }

  /* Numbers */
  .numbers { font-family: ${theme.fonts.number}; }

  /* Responsive */
  @media (max-width: 768px) { html { font-size: 14px; } }
  @media (max-width: 480px) { html { font-size: 13px; } }
`;