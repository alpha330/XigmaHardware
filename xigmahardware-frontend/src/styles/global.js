'use client';
import { Global, css } from '@emotion/react';
import Vazirmatn from 'vazirmatn';

export const GlobalStyles = () => (
  <Global
    styles={css`
      @font-face {
        font-family: 'Vazirmatn';
        src: url(${Vazirmatn}) format('woff2');
        font-weight: 100 900;
        font-style: normal;
        font-display: swap;
      }

      * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }

      body {
        font-family: 'Vazirmatn', sans-serif;
        background-color: ${({ theme }) => theme.colors.background};
        color: ${({ theme }) => theme.colors.text};
        transition: background-color 0.3s, color 0.3s;
        direction: rtl;
      }

      a {
        text-decoration: none;
        color: inherit;
      }

      /* Scrollbar */
      ::-webkit-scrollbar { width: 6px; }
      ::-webkit-scrollbar-track { background: transparent; }
      ::-webkit-scrollbar-thumb {
        background: ${({ theme }) => theme.colors.primary};
        border-radius: 3px;
      }
    `}
  />
);