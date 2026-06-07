// src/components/layout/Header.js
'use client';

import { useState } from 'react';
import styled from '@emotion/styled';
import Link from 'next/link';
import { Icon } from '@/components/ui/Icon';
import { Button } from '@/components/ui/Button';
import { ThemeToggle } from '@/components/ui/ThemeToggle';
import { useThemeMode } from '@/lib/ThemeContext';
import {
  faSearch, faUser, faShoppingCart, faHeart,
  faBars, faTimes, faStore, faPhone, faChevronDown
} from '@fortawesome/free-solid-svg-icons';

const HeaderWrapper = styled.header`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: ${props => props.theme.mode === 'dark'
    ? 'rgba(15, 15, 26, 0.9)'
    : 'rgba(255, 255, 255, 0.9)'
  };
  backdrop-filter: blur(20px);
  border-bottom: 1px solid ${props => props.theme.colors.border};
  transition: all 0.3s ease;
`;

const TopBar = styled.div`
  background: ${props => props.theme.colors.primary[700]};
  color: white;
  padding: 8px 0;
  font-size: 0.85rem;
  text-align: center;
`;

const MainHeader = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  padding: 12px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
`;

const Logo = styled(Link)`
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.4rem;
  font-weight: 800;
  color: ${props => props.theme.colors.text.primary};
  text-decoration: none;
  flex-shrink: 0;

  span {
    background: linear-gradient(135deg,
      ${props => props.theme.colors.primary[500]},
      ${props => props.theme.colors.primary[700]}
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
`;

const SearchBar = styled.div`
  flex: 1;
  max-width: 600px;
  position: relative;

  input {
    width: 100%;
    padding: 12px 48px 12px 16px;
    border: 2px solid ${props => props.theme.colors.border};
    border-radius: ${props => props.theme.borderRadius.full};
    font-family: ${props => props.theme.fonts.primary};
    font-size: 0.9rem;
    background: ${props => props.theme.colors.gray[100]};
    color: ${props => props.theme.colors.text.primary};
    outline: none;
    transition: all 0.3s;

    &:focus {
      border-color: ${props => props.theme.colors.primary[500]};
      background: ${props => props.theme.colors.card};
      box-shadow: 0 0 0 4px ${props => props.theme.colors.primary[100]};
    }
  }

  @media (max-width: 768px) {
    display: none;
  }
`;

const SearchIcon = styled.button`
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: ${props => props.theme.colors.primary[500]};
  color: white;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const Actions = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
`;

const ActionButton = styled(Link)`
  position: relative;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: ${props => props.theme.borderRadius.md};
  color: ${props => props.theme.colors.text.primary};
  transition: all 0.2s;
  font-size: 1.2rem;  // ✅ اضافه کن - کنترل سایز آیکون

  // ✅ آیکون داخلش محدود بشه
  .icon-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
  }

  &:hover {
    background: ${props => props.theme.colors.primary[50]};
    color: ${props => props.theme.colors.primary[500]};
  }
`;

const Badge = styled.span`
  position: absolute;
  top: 4px;
  right: 4px;
  background: ${props => props.theme.colors.danger};
  color: white;
  font-size: 0.7rem;
  font-weight: 700;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const Nav = styled.nav`
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px 12px;
  display: flex;
  gap: 8px;
  overflow-x: auto;
  scrollbar-width: none;

  &::-webkit-scrollbar { display: none; }

  @media (max-width: 768px) {
    display: none;
  }
`;

const NavItem = styled(Link)`
  padding: 8px 16px;
  border-radius: ${props => props.theme.borderRadius.full};
  font-size: 0.9rem;
  font-weight: 500;
  color: ${props => props.theme.colors.text.secondary};
  white-space: nowrap;
  transition: all 0.2s;

  &:hover {
    background: ${props => props.theme.colors.primary[50]};
    color: ${props => props.theme.colors.primary[500]};
  }
`;

export const Header = () => {
  const [mobileMenu, setMobileMenu] = useState(false);

  return (
    <>
      <TopBar>
        🚀 ارسال رایگان برای سفارشات بالای ۵ میلیون تومان | 📞 ۰۲۱-۱۲۳۴۵۶۷۸
      </TopBar>
      <HeaderWrapper>
        <MainHeader>
          <Logo href="/">
            <Icon icon={faStore} size="lg" color="#a855f7" />
            <span>XigmaHardware</span>
          </Logo>

          <SearchBar>
            <input type="text" placeholder="جستجوی محصولات... (مثال: سرور HP G10)" />
            <SearchIcon>
              <Icon icon={faSearch} size="sm" />
            </SearchIcon>
          </SearchBar>

          <Actions>
            <ThemeToggle />

            <ActionButton href="/wishlist">
              <span className="icon-wrapper">
                <Icon icon={faHeart} size="md" />
              </span>
              <Badge>3</Badge>
            </ActionButton>

            <ActionButton href="/cart">
              <Icon icon={faShoppingCart} size="md" />
              <Badge>1</Badge>
            </ActionButton>

            <ActionButton href="/auth/login">
              <Icon icon={faUser} size="md" />
            </ActionButton>
          </Actions>
        </MainHeader>

        <Nav>
          <NavItem href="/products">🖥️ سرور</NavItem>
          <NavItem href="/products">💻 لپ‌تاپ</NavItem>
          <NavItem href="/products">🖥️ workstation</NavItem>
          <NavItem href="/products">📡 شبکه</NavItem>
          <NavItem href="/products">💾 ذخیره‌سازی</NavItem>
          <NavItem href="/products">🔧 قطعات</NavItem>
          <NavItem href="/products/featured">⭐ ویژه</NavItem>
          <NavItem href="/products/bestsellers">🔥 پرفروش</NavItem>
        </Nav>
      </HeaderWrapper>
    </>
  );
};