'use client';

import React, { useState, useEffect, useContext } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import styled from '@emotion/styled';

import { ThemeModeContext } from '../../theme/ThemeRegistry';
import { useCart } from '../../context/CartContext';
import Cookies from 'js-cookie';

// Font Awesome
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faShoppingCart, faUser, faSun, faMoon } from '@fortawesome/free-solid-svg-icons';

// ==================== STYLED COMPONENTS ====================
const HeaderWrapper = styled.header`
  position: sticky;
  top: 0;
  z-index: 1000;
  background: ${({ theme, isScrolled }) => 
    isScrolled 
      ? (theme.colors?.surface || '#ffffff') 
      : (theme.colors?.background || '#ffffff')};
  border-bottom: 1px solid ${({ theme }) => theme.colors?.border || '#e5e7eb'};
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: ${({ isScrolled }) => isScrolled ? '0 4px 6px -1px rgb(0 0 0 / 0.1)' : 'none'};
`;

const HeaderContent = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
`;

const Logo = styled(Link)`
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  transition: transform 0.2s ease;
  &:hover { transform: scale(1.02); }
`;

const LogoImage = styled.img`
  width: 42px;
  height: 42px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid ${({ theme }) => theme.colors?.primary || '#3b82f6'};
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2);
`;

const LogoText = styled.span`
  font-size: 22px;
  font-weight: 800;
  color: ${({ theme }) => theme.colors?.textPrimary || '#111827'};
  letter-spacing: -0.5px;
`;

const Nav = styled.nav`
  display: flex;
  align-items: center;
  gap: 8px;
  @media (max-width: 1024px) { display: none; }
`;

const NavItem = styled(Link)`
  padding: 10px 18px;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  color: ${({ theme }) => theme.colors?.textSecondary || '#4b5563'};
  text-decoration: none;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;

  &:hover {
    color: ${({ theme }) => theme.colors?.textPrimary || '#111827'};
    background: ${({ theme }) => theme.colors?.hover || '#f3f4f6'};
  }

  &[data-active='true'] {
    color: ${({ theme }) => theme.colors?.primary || '#3b82f6'};
    background: ${({ theme }) => theme.colors?.primaryLight || '#eff6ff'};
  }
`;

const ShopDropdown = styled.div`
  position: relative;
  display: inline-block;
`;

const DropdownContent = styled.div`
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  min-width: 620px;
  background: ${({ theme }) => theme.colors?.surface || '#fff'};
  border: 1px solid ${({ theme }) => theme.colors?.border || '#e5e7eb'};
  border-radius: 16px;
  box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
  padding: 24px;
  display: ${({ isOpen }) => (isOpen ? 'grid' : 'none')};
  grid-template-columns: 1fr 1fr;
  gap: 32px;
  z-index: 100;
  opacity: ${({ isOpen }) => (isOpen ? 1 : 0)};
  transform: ${({ isOpen }) => (isOpen ? 'translateY(0)' : 'translateY(10px)')};
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
`;

const DropdownSection = styled.div``;

const DropdownTitle = styled.div`
  font-size: 13px;
  font-weight: 700;
  color: ${({ theme }) => theme.colors?.textMuted || '#6b7280'};
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid ${({ theme }) => theme.colors?.border || '#e5e7eb'};
`;

const DropdownLink = styled(Link)`
  display: block;
  padding: 8px 0;
  font-size: 14.5px;
  color: ${({ theme }) => theme.colors?.textSecondary || '#4b5563'};
  text-decoration: none;
  transition: color 0.15s ease;
  &:hover { color: ${({ theme }) => theme.colors?.primary || '#3b82f6'}; }
`;

const Actions = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const IconButton = styled.button`
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  border-radius: 12px;
  color: ${({ theme }) => theme.colors?.textSecondary || '#4b5563'};
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;

  &:hover {
    background: ${({ theme }) => theme.colors?.hover || '#f3f4f6'};
    color: ${({ theme }) => theme.colors?.textPrimary || '#111827'};
    transform: translateY(-1px);
  }
`;

const CartBadge = styled.span`
  position: absolute;
  top: 6px;
  right: 6px;
  background: ${({ theme }) => theme.colors?.primary || '#3b82f6'};
  color: white;
  font-size: 11px;
  font-weight: 700;
  min-width: 18px;
  height: 18px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 5px;
`;

const ThemeToggle = styled(IconButton)`
  font-size: 20px;
`;

// ==================== HEADER COMPONENT ====================
export default function Header() {
  const pathname = usePathname();
  const { isDarkMode, toggleTheme } = useContext(ThemeModeContext);
  const { cart } = useCart();

  const [isScrolled, setIsScrolled] = useState(false);
  const [isShopOpen, setIsShopOpen] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    const token = Cookies.get('token');
    setIsLoggedIn(!!token);
  }, []);

  const cartCount = cart?.items?.length || 0;

  const isActive = (path) => pathname === path || pathname.startsWith(path + '/');

  const mainNav = [
    { label: 'خانه', href: '/' },
    { label: 'فروشگاه', href: '/market', hasDropdown: true },
    { label: 'اخبار و مقالات', href: '/news' },
    { label: 'بررسی‌های تخصصی', href: '/expert-reviews' },
    { label: 'پشتیبانی', href: '/support' },
  ];

  const categories = [
    { id: 1, name: 'سرور و تجهیزات دیتاسنتر', href: '/market?category=1' },
    { id: 2, name: 'تجهیزات شبکه', href: '/market?category=2' },
    { id: 3, name: 'قطعات کامپیوتر', href: '/market?category=3' },
  ];

  const brands = [
    { id: 1, name: 'HP', href: '/market?brand=1' },
    { id: 2, name: 'Cisco', href: '/market?brand=2' },
    { id: 3, name: 'Dell', href: '/market?brand=3' },
  ];

  return (
    <HeaderWrapper isScrolled={isScrolled}>
      <HeaderContent>
        <Logo href="/">
          <LogoImage 
            src="/images/logos/xigma-logo.png" 
            alt="XigmaHardware" 
            onError={(e) => { e.target.src = 'https://via.placeholder.com/42/3b82f6/ffffff?text=XH'; }}
          />
          <LogoText>XigmaHardware</LogoText>
        </Logo>

        <Nav>
          {mainNav.map((item) => 
            item.hasDropdown ? (
              <ShopDropdown 
                key={item.label}
                onMouseEnter={() => setIsShopOpen(true)}
                onMouseLeave={() => setIsShopOpen(false)}
              >
                <NavItem href={item.href} data-active={isActive(item.href)}>
                  {item.label}
                </NavItem>

                <DropdownContent isOpen={isShopOpen}>
                  <DropdownSection>
                    <DropdownTitle>دسته‌بندی‌ها</DropdownTitle>
                    {categories.map(cat => (
                      <DropdownLink key={cat.id} href={cat.href}>{cat.name}</DropdownLink>
                    ))}
                    <DropdownLink href="/market" style={{ marginTop: '8px', fontWeight: 600 }}>
                      مشاهده همه دسته‌ها →
                    </DropdownLink>
                  </DropdownSection>

                  <DropdownSection>
                    <DropdownTitle>برندهای محبوب</DropdownTitle>
                    {brands.map(brand => (
                      <DropdownLink key={brand.id} href={brand.href}>{brand.name}</DropdownLink>
                    ))}
                    <DropdownLink href="/market" style={{ marginTop: '8px', fontWeight: 600 }}>
                      همه برندها →
                    </DropdownLink>
                  </DropdownSection>
                </DropdownContent>
              </ShopDropdown>
            ) : (
              <NavItem 
                key={item.label}
                href={item.href} 
                data-active={isActive(item.href)}
              >
                {item.label}
              </NavItem>
            )
          )}
        </Nav>

        <Actions>
          {/* Theme Toggle - حالا با Font Awesome */}
          <ThemeToggle onClick={toggleTheme} title={isDarkMode ? 'تم روشن' : 'تم تیره'}>
            <FontAwesomeIcon icon={isDarkMode ? faSun : faMoon} />
          </ThemeToggle>

          {/* Cart */}
          <IconButton as={Link} href="/basket/cart" title="سبد خرید">
            <FontAwesomeIcon icon={faShoppingCart} />
            {cartCount > 0 && <CartBadge>{cartCount}</CartBadge>}
          </IconButton>

          {/* User */}
          {isLoggedIn ? (
            <IconButton as={Link} href="/accounts/profile" title="حساب کاربری">
              <FontAwesomeIcon icon={faUser} />
            </IconButton>
          ) : (
            <Link href="/auth/login">
              <button style={{
                padding: '10px 20px',
                background: '#3b82f6',
                color: 'white',
                border: 'none',
                borderRadius: '10px',
                fontWeight: 600,
                cursor: 'pointer'
              }}>
                ورود / ثبت‌نام
              </button>
            </Link>
          )}
        </Actions>
      </HeaderContent>
    </HeaderWrapper>
  );
}
