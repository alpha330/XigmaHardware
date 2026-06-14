// src/components/layout/Header.jsx
'use client';

import React, { useContext, useEffect, useState } from 'react';
import styled from '@emotion/styled';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import Cookies from 'js-cookie';
import { ThemeModeContext } from '../../theme/ThemeRegistry';
import SearchBar from './SearchBar';
import { apiFetch } from '../../utils/apiFetch';

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

const UserMenuWrapper = styled.div`
  position: relative; display: flex; align-items: center; cursor: pointer; padding: 0.5rem 0;
  &:hover > div { opacity: 1; visibility: visible; transform: translateY(0); }
`;

const Avatar = styled.div`
  width: 42px; height: 42px; border-radius: 50%;
  background: linear-gradient(135deg, ${({ theme }) => theme.colors.primary} 0%, ${({ theme }) => theme.colors.secondary} 100%);
  color: #fff; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 1.2rem;
  border: 2px solid ${({ theme }) => theme.colors.border}; box-shadow: 0 4px 10px rgba(0,0,0,0.1); overflow: hidden;
  img { width: 100%; height: 100%; object-fit: cover; }
`;

const DropdownMenu = styled.div`
  position: absolute; top: 100%; left: 0; background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border}; border-radius: 12px; min-width: 240px;
  opacity: 0; visibility: hidden; transform: translateY(15px); transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 10px 30px rgba(0,0,0,0.15); display: flex; flex-direction: column; padding: 0.5rem; z-index: 1001;
`;

const DropdownHeader = styled.div`
  padding: 1rem; border-bottom: 1px solid ${({ theme }) => theme.colors.border}; margin-bottom: 0.5rem;
  strong { display: block; color: ${({ theme }) => theme.colors.textMain}; font-size: 1rem; margin-bottom: 0.2rem; }
  span { color: ${({ theme }) => theme.colors.textMuted}; font-size: 0.8rem; }
`;

const DropdownItem = styled(Link)`
  padding: 0.7rem 1rem; color: ${({ theme }) => theme.colors.textMain}; font-size: 0.9rem; border-radius: 8px;
  display: flex; align-items: center; gap: 0.8rem; transition: background-color 0.2s ease;
  &:hover { background-color: ${({ theme }) => theme.colors.background}; color: ${({ theme }) => theme.colors.primary}; }
`;

const MenuDivider = styled.div`
  height: 1px; background-color: ${({ theme }) => theme.colors.border}; margin: 0.5rem 0;
`;

const MenuBadge = styled.span`
  background-color: ${({ theme, colorType }) => theme.colors[colorType] || theme.colors.primary};
  color: #fff; font-size: 0.7rem; padding: 0.1rem 0.4rem; border-radius: 10px; margin-right: auto;
`;

const LogoutButton = styled.button`
  width: 100%; text-align: right; padding: 0.8rem 1rem; color: ${({ theme }) => theme.colors.error};
  background: none; border: none; font-family: inherit; font-size: 0.95rem; cursor: pointer; border-radius: 8px;
  display: flex; align-items: center; gap: 0.8rem; transition: background-color 0.2s ease;
  margin-top: 0.5rem; border-top: 1px solid ${({ theme }) => theme.colors.border};
  &:hover { background-color: ${({ theme }) => `${theme.colors.error}15`}; }
`;

export default function Header() {
  const router = useRouter();
  const { isDarkMode, toggleTheme } = useContext(ThemeModeContext);
  const [isScrolled, setIsScrolled] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userProfile, setUserProfile] = useState(null);
  const [userData, setUserData] = useState(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setMounted(true);
    const token = Cookies.get('token');

    if (token) {
      setIsLoggedIn(true);
      apiFetch('/api/v1/accounts/me/profile/')
      .then((res) => {
        if (!res.ok) return null;
        return res.json();
      })
      .then(data => {
        if (data) setUserProfile(data.profile);
      })
      .catch((error) => {
        // ارورهای 401 در خود apiFetch هندل شده و کوکی‌ها پاک میشن
        console.error(' مشخصات پروفایل ارتباط با سرور:', error);
      });
      apiFetch('/api/v1/accounts/me/')
      .then((res) => {
        if (!res.ok) return null;
        return res.json();
      })
      .then(data => {
        if (data) setUserData(data.user);
      })
      .catch((error) => {
        // ارورهای 401 در خود apiFetch هندل شده و کوکی‌ها پاک میشن
        console.error('مشخصات کاربر ارتباط با سرور:', error);
      });
    }

    const handleScroll = () => setIsScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleLogout = async () => {
    try {
      const refresh = Cookies.get('refresh');
      if (refresh) {
        // ارسال دقیق کلید refresh به همراه توکن Bearer (توسط apiFetch)
        await apiFetch('/api/v1/accounts/auth/logout/', {
          method: 'POST',
          body: JSON.stringify({ refresh: refresh })
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // در هر صورت (حتی اگر سرور ارور داد) کوکی‌ها پاک شده و کاربر خارج می‌شود
      Cookies.remove('token', { path: '/' });
      Cookies.remove('refresh', { path: '/' });
      setIsLoggedIn(false);
      setUserProfile(null);
      router.push('/');
      router.refresh();
    }
  };

  const displayName = userData?.first_name ? `${userData.first_name} ${userData.last_name || ''}` : 'کاربر سایت';
  const initial = userData?.first_name ? userData.first_name.charAt(0) : 'U';
  // متغیرهای دسترسی (ممکن است بک‌اند شما از is_superuser یا role یا گروه استفاده کند)
  const isSuperuser = userProfile?.is_superuser;
  const role = userProfile?.role || userProfile?.group || 'client'; // فرض می‌کنیم نقش کلاینت معمولی است

  return (
    <HeaderWrapper isScrolled={isScrolled}>
      <Logo href="/"><span>Xigma</span>Hardware</Logo>
      <SearchContainer><SearchBar /></SearchContainer>
      <NavLinks>
        <NavItem href="/market">فروشگاه</NavItem>
        <NavItem href="/market?category=servers">سرورها</NavItem>
        <NavItem href="/support">پشتیبانی</NavItem>
      </NavLinks>
      <Actions>
        <ThemeButton onClick={toggleTheme} title="تغییر تم">
          {mounted && (isDarkMode ? '☀️' : '🌙')}
        </ThemeButton>
        <NavItem href="/basket/cart" style={{ fontSize: '1.2rem' }}>🛒</NavItem>

        {mounted && (
          isLoggedIn ? (
            <UserMenuWrapper>
              <Avatar>
                {userProfile?.avatar ? <img src={userProfile.avatar_url} alt="Avatar" /> : initial}
              </Avatar>
              <DropdownMenu>
                <DropdownHeader>
                  <strong>{displayName}</strong>
                  <span>{userProfile?.email || userProfile?.mobile || ''}</span>
                </DropdownHeader>

                {/* لینک‌های عمومی پروفایل */}
                <DropdownItem href="/accounts/profile">👤 پروفایل کاربری</DropdownItem>
                <DropdownItem href="/accounts/wallet">💰 کیف پول و تراکنش‌ها</DropdownItem>

                {/* لینک‌های مخصوص خریدار معمولی */}
                {role === 'client' && !isSuperuser && (
                  <>
                    <DropdownItem href="/accounts/invoices">💳 سفارشات و فاکتورها</DropdownItem>
                    <DropdownItem href="/support/tickets">🎫 تیکت‌های پشتیبانی</DropdownItem>
                  </>
                )}

                {/* --- لینک‌های مخصوص مدیران و کارمندان --- */}
                {(isSuperuser || role !== 'client') && <MenuDivider />}

                {isSuperuser && (
                  <DropdownItem href="/admin-panel">
                    👑 پنل مدیریت کل <MenuBadge colorType="error">Super</MenuBadge>
                  </DropdownItem>
                )}

                {(isSuperuser || role === 'financial') && (
                  <DropdownItem href="/financial-panel">
                    💳 مدیریت فاکتورها و مالی <MenuBadge colorType="success">Fin</MenuBadge>
                  </DropdownItem>
                )}

                {(isSuperuser || role === 'stock') && (
                  <DropdownItem href="/stock-panel">
                    📦 مدیریت انبار و موجودی <MenuBadge colorType="primary">Stock</MenuBadge>
                  </DropdownItem>
                )}

                {(isSuperuser || role === 'logistic') && (
                  <DropdownItem href="/logistic-panel">
                    🚚 مدیریت ارسال و پیک <MenuBadge colorType="primary">Logis</MenuBadge>
                  </DropdownItem>
                )}

                {(isSuperuser || role === 'support') && (
                  <DropdownItem href="/support-panel">
                    🎧 مدیریت تیکت‌ها و چت <MenuBadge colorType="primary">Supp</MenuBadge>
                  </DropdownItem>
                )}

                <LogoutButton onClick={handleLogout}>🚪 خروج از حساب</LogoutButton>
              </DropdownMenu>
            </UserMenuWrapper>
          ) : (
            <PrimaryButton href="/auth/login">ورود / ثبت‌نام</PrimaryButton>
          )
        )}
      </Actions>
    </HeaderWrapper>
  );
}