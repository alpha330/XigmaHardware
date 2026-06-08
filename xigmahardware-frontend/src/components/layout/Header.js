// src/components/layout/Header.js
'use client';

import { useState, useEffect } from 'react';
import styled from '@emotion/styled';
import Link from 'next/link';
import { Icon } from '@/components/ui/Icon';
import { Button } from '@/components/ui/Button';
import { ThemeToggle } from '@/components/ui/ThemeToggle';
import {
  faSearch, faUser, faCartShopping, faHeart,
  faBars, faXmark, faMicrochip, faPhone,
} from '@fortawesome/free-solid-svg-icons';

const HEADER_HEIGHT = 72;

const HeaderWrapper = styled.header`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  height: ${HEADER_HEIGHT}px;
  background: ${props => props.theme.mode === 'dark'
    ? 'rgba(15, 23, 42, 0.92)'
    : 'rgba(255, 255, 255, 0.92)'
  };
  backdrop-filter: blur(16px) saturate(180%);
  border-bottom: 1px solid ${props => props.theme.colors.border.light};
  transition: all 0.3s ease;
`;

const HeaderInner = styled.div`
  max-width: 1440px;
  margin: 0 auto;
  height: 100%;
  padding: 0 24px;
  display: flex;
  align-items: center;
  gap: 24px;
`;

const Logo = styled(Link)`
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.35rem;
  font-weight: 800;
  color: ${props => props.theme.colors.text.primary};
  text-decoration: none;
  flex-shrink: 0;
  letter-spacing: -0.5px;

  .logo-icon {
    width: 40px;
    height: 40px;
    background: ${props => props.theme.colors.brand[500]};
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
  }

  .logo-text {
    background: linear-gradient(135deg,
      ${props => props.theme.colors.text.primary},
      ${props => props.theme.colors.brand[500]}
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  @media (max-width: 640px) {
    .logo-text { display: none; }
  }
`;

const SearchBar = styled.div`
  flex: 1;
  max-width: 520px;
  position: relative;

  @media (max-width: 768px) {
    display: ${props => props.$mobileSearch ? 'block' : 'none'};
    position: fixed;
    top: ${HEADER_HEIGHT}px;
    left: 0;
    right: 0;
    max-width: 100%;
    padding: 12px 16px;
    background: ${props => props.theme.colors.bg.primary};
    border-bottom: 1px solid ${props => props.theme.colors.border.light};
  }
`;

const SearchInput = styled.input`
  width: 100%;
  height: 44px;
  padding: 0 48px 0 16px;
  border: 1.5px solid ${props => props.theme.colors.border.light};
  border-radius: ${props => props.theme.borderRadius.full};
  font-family: ${props => props.theme.fonts.primary};
  font-size: 0.9rem;
  background: ${props => props.theme.colors.bg.tertiary};
  color: ${props => props.theme.colors.text.primary};
  outline: none;
  transition: all 0.2s;

  &:focus {
    border-color: ${props => props.theme.colors.brand[500]};
    box-shadow: 0 0 0 3px ${props => props.theme.colors.brand[100]};
    background: ${props => props.theme.colors.bg.primary};
  }

  &::placeholder {
    color: ${props => props.theme.colors.text.muted};
  }
`;

const SearchButton = styled.button`
  position: absolute;
  right: 4px;
  top: 50%;
  transform: translateY(-50%);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background: ${props => props.theme.colors.brand[500]};
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;

  &:hover { background: ${props => props.theme.colors.brand[600]}; }
`;

const Actions = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
`;

const IconButton = styled(Link)`
  position: relative;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: ${props => props.theme.borderRadius.md};
  color: ${props => props.theme.colors.text.secondary};
  transition: all 0.15s;

  &:hover {
    background: ${props => props.theme.colors.brand[50]};
    color: ${props => props.theme.colors.brand[600]};
  }
`;

const Badge = styled.span`
  position: absolute;
  top: 2px;
  right: 2px;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  background: ${props => props.theme.colors.danger};
  color: white;
  font-size: 0.65rem;
  font-weight: 700;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid ${props => props.theme.colors.surface.card};
`;

const MobileMenuButton = styled.button`
  display: none;
  width: 40px;
  height: 40px;
  align-items: center;
  justify-content: center;
  border: none;
  background: none;
  color: ${props => props.theme.colors.text.primary};
  cursor: pointer;
  border-radius: ${props => props.theme.borderRadius.md};

  @media (max-width: 768px) {
    display: flex;
  }
`;

const Nav = styled.nav`
  display: flex;
  align-items: center;
  gap: 4px;

  @media (max-width: 1024px) {
    display: none;
  }
`;

const NavLink = styled(Link)`
  padding: 8px 14px;
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: 0.875rem;
  font-weight: 500;
  color: ${props => props.theme.colors.text.secondary};
  white-space: nowrap;
  transition: all 0.15s;

  &:hover {
    background: ${props => props.theme.colors.brand[50]};
    color: ${props => props.theme.colors.brand[600]};
  }
`;

export const Header = () => {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 10);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <HeaderWrapper style={scrolled ? { boxShadow: '0 1px 3px rgba(0,0,0,0.08)' } : {}}>
      <HeaderInner>
        <Logo href="/">
          <span className="logo-icon">
            <Icon icon={faMicrochip} size="md" />
          </span>
          <span className="logo-text">XigmaHardware</span>
        </Logo>

        <Nav>
          <NavLink href="/products/servers">🖥️ سرور</NavLink>
          <NavLink href="/products/workstations">💻 Workstation</NavLink>
          <NavLink href="/products/networking">📡 شبکه</NavLink>
          <NavLink href="/products/storage">💾 ذخیره‌سازی</NavLink>
          <NavLink href="/products/parts">🔧 قطعات</NavLink>
        </Nav>

        <SearchBar>
          <SearchInput placeholder="جستجوی محصول، برند، مدل..." />
          <SearchButton>
            <Icon icon={faSearch} size="sm" />
          </SearchButton>
        </SearchBar>

        <Actions>
          <ThemeToggle />

          <IconButton href="/wishlist" aria-label="علاقه‌مندی‌ها">
            <Icon icon={faHeart} size="md" />
            <Badge>3</Badge>
          </IconButton>

          <IconButton href="/cart" aria-label="سبد خرید">
            <Icon icon={faCartShopping} size="md" />
            <Badge>1</Badge>
          </IconButton>

          <IconButton href="/auth/login" aria-label="ورود">
            <Icon icon={faUser} size="md" />
          </IconButton>

          <MobileMenuButton>
            <Icon icon={faBars} size="md" />
          </MobileMenuButton>
        </Actions>
      </HeaderInner>
    </HeaderWrapper>
  );
};