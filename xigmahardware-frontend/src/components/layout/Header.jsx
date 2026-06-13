'use client';
import { useState, useEffect } from 'react';
import styled from '@emotion/styled';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSun, faMoon, faUser, faShoppingCart } from '@fortawesome/free-solid-svg-icons';
import { useThemeMode } from '@/lib/ThemeContext';
import { toJalaliDateTime } from '@/lib/dateUtils';
import Link from 'next/link';

const HeaderContainer = styled.header`
  background: ${({ theme }) => theme.colors.headerBg};
  color: white;
  padding: 0.5rem 1rem;
  position: sticky;
  top: 0;
  z-index: 1000;
  box-shadow: ${({ theme }) => theme.shadows.md};
`;

const TopBar = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  padding-bottom: 0.3rem;
  margin-bottom: 0.5rem;
`;

const MainNav = styled.nav`
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
`;

const Logo = styled(Link)`
  font-size: 1.6rem;
  font-weight: bold;
  color: ${({ theme }) => theme.colors.primary};
`;

const MenuList = styled.ul`
  display: flex;
  list-style: none;
  gap: 1.5rem;
  @media (max-width: 768px) {
    display: none;
  }
`;

const Actions = styled.div`
  display: flex;
  gap: 1rem;
  align-items: center;
`;

const IconButton = styled.button`
  background: transparent;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 1.2rem;
  transition: color 0.2s;
  &:hover { color: ${({ theme }) => theme.colors.primary}; }
`;

export default function Header() {
  const { isDark, toggleTheme } = useThemeMode();
  const [currentTime, setCurrentTime] = useState('');

  useEffect(() => {
    setCurrentTime(toJalaliDateTime(new Date()));
    const timer = setInterval(() => setCurrentTime(toJalaliDateTime(new Date())), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <HeaderContainer>
      <TopBar>
        <span>📞 ۰۲۱-۱۲۳۴۵۶۷۸ | ✉️ info@xigmahardware.com</span>
        <span>{currentTime}</span>
      </TopBar>
      <MainNav>
        <Logo href="/">XigmaHardware</Logo>
        <MenuList>
          <li><Link href="/categories/datacenter">دیتاسنتر</Link></li>
          <li><Link href="/categories/office">اداری</Link></li>
          <li><Link href="/categories/home">خانگی</Link></li>
          <li><Link href="/categories/workstation">ورک‌استیشن</Link></li>
          <li><Link href="/news">اخبار</Link></li>
          <li><Link href="/reviews">نظرات</Link></li>
          <li><Link href="/about">درباره ما</Link></li>
          <li><Link href="/contact">تماس با ما</Link></li>
        </MenuList>
        <Actions>
          <IconButton onClick={toggleTheme}>
            <FontAwesomeIcon icon={isDark ? faSun : faMoon} />
          </IconButton>
          <Link href="/cart" passHref>
            <IconButton as="a"><FontAwesomeIcon icon={faShoppingCart} /></IconButton>
          </Link>
          <Link href="/auth/login" passHref>
            <IconButton as="a"><FontAwesomeIcon icon={faUser} /></IconButton>
          </Link>
        </Actions>
      </MainNav>
    </HeaderContainer>
  );
}