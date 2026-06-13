// src/components/layout/Header.jsx
'use client';

import React, { useContext, useEffect, useState } from 'react';
import styled from '@emotion/styled';
import Link from 'next/link';
import { ThemeModeContext } from '../../theme/ThemeRegistry';
import SearchBar from './SearchBar'; // ایمپورت کامپوننت سرچ

const HeaderWrapper = styled.header`
  position: sticky;
  top: 0;
  z-index: 1000;
  background-color: ${({ theme, isScrolled }) =>
    isScrolled ? theme.colors.surface : theme.colors.background};
  box-shadow: ${({ isScrolled }) =>
    isScrolled ? '0 4px 6px -1px rgba(0, 0, 0, 0.1)' : 'none'};
  transition: all 0.3s ease;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid ${({ theme }) => theme.colors.border};
  gap: 2rem;

  @media (max-width: 768px) {
    flex-wrap: wrap;
    gap: 1rem;
    padding: 1rem;
  }
`;

const Logo = styled(Link)`
  font-size: 1.5rem;
  font-weight: bold;
  color: ${({ theme }) => theme.colors.primary};
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
`;

const NavLinks = styled.nav`
  display: flex;
  gap: 1.5rem;

  @media (max-width: 1024px) {
    display: none;
  }
`;

const NavItem = styled(Link)`
  color: ${({ theme }) => theme.colors.textMain};
  font-weight: 500;
  transition: color 0.2s ease;
  white-space: nowrap;

  &:hover {
    color: ${({ theme }) => theme.colors.primary};
  }
`;

const Actions = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;

  @media (max-width: 768px) {
    width: 100%;
    justify-content: space-between;
    order: 3;
  }
`;

const SearchContainer = styled.div`
  flex: 1;
  max-width: 500px;

  @media (max-width: 768px) {
    order: 2;
    max-width: 100%;
    min-width: 200px;
  }
`;

const ThemeButton = styled.button`
  background: none;
  border: 1px solid ${({ theme }) => theme.colors.border};
  color: ${({ theme }) => theme.colors.textMain};
  padding: 0.5rem;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;

  &:hover {
    background-color: ${({ theme }) => theme.colors.surface};
  }
`;

const PrimaryButton = styled(Link)`
  background-color: ${({ theme }) => theme.colors.primary};
  color: #fff !important;
  padding: 0.5rem 1.2rem;
  border-radius: 8px;
  font-weight: bold;
  transition: background-color 0.2s ease;
  white-space: nowrap;

  &:hover {
    background-color: ${({ theme }) => theme.colors.secondary};
  }
`;

export default function Header() {
  const { isDarkMode, toggleTheme } = useContext(ThemeModeContext);
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <HeaderWrapper isScrolled={isScrolled}>
      <Logo href="/">
        <span>Xigma</span>Hardware
      </Logo>



      <NavLinks>
        <NavItem href="/market">فروشگاه</NavItem>
        <NavItem href="/news">اخبار و مقالات</NavItem>
        <NavItem href="/expert-reviews">بررسی ها</NavItem>
        <NavItem href="/market?category=servers">سرورها</NavItem>
        <NavItem href="/about">درباره ما</NavItem>
        <NavItem href="/contact">ارتباط با ما</NavItem>
        <NavItem href="/support">پشتیبانی</NavItem>
      </NavLinks>

      {/* کامپوننت جستجوی زنده در هدر */}
      <SearchContainer>
        <SearchBar />
      </SearchContainer>

      <Actions>
        <ThemeButton onClick={toggleTheme} title="تغییر تم">
          {isDarkMode ? '☀️' : '🌙'}
        </ThemeButton>
        <NavItem href="/basket/cart">🛒</NavItem>
        <PrimaryButton href="/auth/login">ورود / ثبت‌نام</PrimaryButton>
      </Actions>


    </HeaderWrapper>
  );
}