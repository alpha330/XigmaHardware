// src/components/dashboard/DashboardShell.js
'use client';

import { useState } from 'react';
import styled from '@emotion/styled';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Icon } from '@/components/ui/Icon';
import { ThemeToggle } from '@/components/ui/ThemeToggle';
import {
  faHome, faUser, faWallet, faMapMarkerAlt, faHeart, faStar,
  faTicketAlt, faFileInvoice, faChartLine, faTags, faWarehouse,
  faBoxes, faTruck, faMotorcycle, faHeadset, faQuestionCircle,
  faShieldAlt, faUsers, faCreditCard, faSignOutAlt, faBars, faTimes,
  faMicrochip, faChevronLeft, faBell, faBox
} from '@fortawesome/free-solid-svg-icons';

// ==================== Styled Components ====================

const Layout = styled.div`
  display: flex;
  min-height: 100vh;
  background: ${p => p.theme.colors.bg.secondary};
`;

const SidebarOverlay = styled.div`
  @media (max-width: 1024px) {
    display: ${p => p.$open ? 'block' : 'none'};
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.5);
    z-index: 99;
  }
`;

const Sidebar = styled.aside`
  width: 260px;
  background: ${p => p.theme.colors.surface.card};
  border-left: 1px solid ${p => p.theme.colors.border.light};
  display: flex;
  flex-direction: column;
  position: fixed;
  right: 0;
  top: 0;
  bottom: 0;
  z-index: 100;
  overflow-y: auto;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  @media (max-width: 1024px) {
    transform: ${p => p.$open ? 'translateX(0)' : 'translateX(100%)'};
  }

  @media (min-width: 1025px) {
    transform: translateX(0);
  }
`;

const SidebarHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 24px 16px;
  border-bottom: 1px solid ${p => p.theme.colors.border.light};
  margin-bottom: 16px;
`;

const LogoBox = styled.div`
  width: 38px;
  height: 38px;
  background: ${p => p.theme.colors.brand[500]};
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
`;

const LogoText = styled.div`
  font-weight: 800;
  font-size: 1.1rem;
  color: ${p => p.theme.colors.text.primary};
  line-height: 1.2;
`;

const LogoSub = styled.div`
  font-size: 0.7rem;
  color: ${p => p.theme.colors.text.muted};
  font-weight: 400;
`;

const NavSection = styled.div`
  margin-bottom: 16px;
  flex: 1;
`;

const NavTitle = styled.p`
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: ${p => p.theme.colors.text.muted};
  margin-bottom: 8px;
  padding: 0 16px;
  font-weight: 600;
`;

const NavItem = styled(Link)`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  margin: 0 8px 2px;
  border-radius: ${p => p.theme.borderRadius.md};
  color: ${p => p.$active ? p.theme.colors.brand[600] : p.theme.colors.text.secondary};
  background: ${p => p.$active ? p.theme.colors.brand[50] : 'transparent'};
  font-weight: ${p => p.$active ? 600 : 400};
  font-size: 0.9rem;
  text-decoration: none;
  transition: all 0.15s;

  &:hover {
    background: ${p => p.theme.colors.brand[50]};
    color: ${p => p.theme.colors.brand[600]};
  }
`;

const NavIcon = styled.span`
  width: 20px;
  display: flex;
  justify-content: center;
  flex-shrink: 0;
`;

const Badge = styled.span`
  margin-right: auto;
  background: ${p => p.theme.colors.danger};
  color: white;
  font-size: 0.65rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 50px;
`;

const SidebarFooter = styled.div`
  padding: 16px;
  border-top: 1px solid ${p => p.theme.colors.border.light};
`;

const UserInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
`;

const UserAvatar = styled.div`
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: ${p => p.theme.colors.brand[100]};
  color: ${p => p.theme.colors.brand[700]};
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.9rem;
`;

const UserName = styled.div`
  font-weight: 600;
  font-size: 0.9rem;
  color: ${p => p.theme.colors.text.primary};
`;

const UserRole = styled.div`
  font-size: 0.75rem;
  color: ${p => p.theme.colors.text.muted};
`;

const LogoutButton = styled.button`
  width: 100%;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border: none;
  border-radius: ${p => p.theme.borderRadius.md};
  background: transparent;
  color: ${p => p.theme.colors.danger};
  cursor: pointer;
  font-family: ${p => p.theme.fonts.primary};
  font-size: 0.85rem;
  transition: all 0.15s;

  &:hover {
    background: ${p => p.theme.colors.danger}10;
  }
`;

const MainContent = styled.main`
  flex: 1;
  margin-right: 260px;
  padding: 32px;
  min-height: 100vh;

  @media (max-width: 1024px) {
    margin-right: 0;
    padding: 24px 16px;
  }
`;

const TopBar = styled.div`
  display: none;
  position: sticky;
  top: 0;
  z-index: 50;
  background: ${p => p.theme.colors.bg.secondary};
  padding: 12px 0;
  margin-bottom: 16px;

  @media (max-width: 1024px) {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
`;

const MobileMenuBtn = styled.button`
  width: 40px;
  height: 40px;
  border-radius: ${p => p.theme.borderRadius.md};
  border: 1px solid ${p => p.theme.colors.border.light};
  background: ${p => p.theme.colors.surface.card};
  color: ${p => p.theme.colors.text.primary};
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
`;

// ==================== Menu Config ====================

const roleLabels = {
  client: 'مشتری',
  accountant: 'مدیر مالی',
  stock_keeper: 'انباردار',
  courier: 'پیک',
  super_admin: 'سوپر ادمین',
};

const allMenus = {
  // مشتری
  client: [
    { section: 'اصلی', items: [
      { icon: faHome, label: 'پیشخوان', href: '/dashboard' },
      { icon: faBox, label: 'سفارشات من', href: '/dashboard/orders' },
    ]},
    { section: 'مالی', items: [
      { icon: faWallet, label: 'کیف پول', href: '/dashboard/wallet' },
    ]},
    { section: 'حساب کاربری', items: [
      { icon: faMapMarkerAlt, label: 'آدرس‌ها', href: '/dashboard/addresses' },
      { icon: faHeart, label: 'علاقه‌مندی‌ها', href: '/dashboard/wishlist' },
      { icon: faStar, label: 'نظرات من', href: '/dashboard/reviews' },
      { icon: faUser, label: 'پروفایل', href: '/dashboard/profile' },
    ]},
    { section: 'پشتیبانی', items: [
      { icon: faTicketAlt, label: 'پشتیبانی', href: '/dashboard/support' },
      { icon: faTicketAlt, label: 'تیکت‌ها', href: '/dashboard/tickets' },
    ]},
  ],

  // مدیر مالی
  accountant: [
    { section: 'اصلی', items: [
      { icon: faHome, label: 'پیشخوان', href: '/dashboard' },
    ]},
    { section: 'مالی', items: [
      { icon: faFileInvoice, label: 'فاکتورها', href: '/dashboard/invoices' },
      { icon: faChartLine, label: 'تراکنش‌ها', href: '/dashboard/transactions' },
      { icon: faChartLine, label: 'گزارش‌ها', href: '/dashboard/reports' },
      { icon: faTags, label: 'تخفیف‌ها', href: '/dashboard/discounts' },
    ]},
    { section: 'پشتیبانی', items: [
      { icon: faHeadset, label: 'پشتیبانی', href: '/dashboard/support' },
      { icon: faTicketAlt, label: 'تیکت‌ها', href: '/dashboard/tickets' },
      { icon: faQuestionCircle, label: 'FAQ', href: '/dashboard/faq' },
      { icon: faShieldAlt, label: 'گارانتی', href: '/dashboard/warranty' },
      { icon: faHeadset, label: 'چت', href: '/dashboard/chat' },
    ]},
  ],

  // انباردار
  stock_keeper: [
    { section: 'اصلی', items: [
      { icon: faHome, label: 'پیشخوان', href: '/dashboard' },
    ]},
    { section: 'لجستیک', items: [
      { icon: faWarehouse, label: 'انبارها', href: '/dashboard/warehouses' },
      { icon: faBoxes, label: 'موجودی', href: '/dashboard/inventory' },
      { icon: faTruck, label: 'محموله‌ها', href: '/dashboard/shipments' },
      { icon: faMotorcycle, label: 'پیک‌ها', href: '/dashboard/couriers' },
    ]},
  ],

  // پیک
  courier: [
    { section: 'اصلی', items: [
      { icon: faHome, label: 'پیشخوان', href: '/dashboard' },
    ]},
    { section: 'لجستیک', items: [
      { icon: faTruck, label: 'محموله‌های من', href: '/dashboard/shipments' },
    ]},
  ],

  // سوپر ادمین (همه چیز)
  super_admin: [
    { section: 'اصلی', items: [
      { icon: faHome, label: 'پیشخوان', href: '/dashboard' },
    ]},
    { section: 'مدیریت', items: [
      { icon: faUsers, label: 'کاربران', href: '/dashboard/users' },
      { icon: faCreditCard, label: 'درگاه‌ها', href: '/dashboard/gateways' },
    ]},
    { section: 'مالی', items: [
      { icon: faFileInvoice, label: 'فاکتورها', href: '/dashboard/invoices' },
      { icon: faChartLine, label: 'تراکنش‌ها', href: '/dashboard/transactions' },
      { icon: faChartLine, label: 'گزارش‌ها', href: '/dashboard/reports' },
      { icon: faTags, label: 'تخفیف‌ها', href: '/dashboard/discounts' },
    ]},
    { section: 'لجستیک', items: [
      { icon: faWarehouse, label: 'انبارها', href: '/dashboard/warehouses' },
      { icon: faBoxes, label: 'موجودی', href: '/dashboard/inventory' },
      { icon: faTruck, label: 'محموله‌ها', href: '/dashboard/shipments' },
      { icon: faMotorcycle, label: 'پیک‌ها', href: '/dashboard/couriers' },
    ]},
    { section: 'پشتیبانی', items: [
      { icon: faHeadset, label: 'پشتیبانی', href: '/dashboard/support' },
      { icon: faTicketAlt, label: 'تیکت‌ها', href: '/dashboard/tickets' },
      { icon: faHeadset, label: 'چت', href: '/dashboard/chat' },
      { icon: faQuestionCircle, label: 'FAQ', href: '/dashboard/faq' },
      { icon: faShieldAlt, label: 'گارانتی', href: '/dashboard/warranty' },
    ]},
  ],
};

// ==================== Component ====================

export const DashboardShell = ({ user, children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const pathname = usePathname();
  const menus = allMenus[user.role] || allMenus.client;
  const roleLabel = roleLabels[user.role] || 'کاربر';

  const handleLogout = async () => {
    try {
      const { clearAuthCookies } = await import('@/lib/auth-actions');
      await clearAuthCookies();
      window.location.href = '/auth/login';
    } catch {
      window.location.href = '/auth/login';
    }
  };

  const userInitial = (user.name || user.email || 'U')[0].toUpperCase();

  return (
    <Layout>
      {/* Overlay mobile */}
      <SidebarOverlay $open={sidebarOpen} onClick={() => setSidebarOpen(false)} />

      {/* Sidebar */}
      <Sidebar $open={sidebarOpen}>
        <SidebarHeader>
          <LogoBox>
            <Icon icon={faMicrochip} size="sm" />
          </LogoBox>
          <div>
            <LogoText>XigmaHardware</LogoText>
            <LogoSub>{roleLabel}</LogoSub>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            style={{
              marginRight: 'auto',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              color: 'inherit',
              display: 'none',
            }}
            className="close-sidebar-mobile"
          >
            <Icon icon={faTimes} size="sm" />
          </button>
        </SidebarHeader>

        <NavSection>
          {menus.map((section, idx) => (
            <div key={idx} style={{ marginBottom: 16 }}>
              <NavTitle>{section.section}</NavTitle>
              {section.items.map(item => (
                <NavItem
                  key={item.href}
                  href={item.href}
                  $active={pathname === item.href}
                  onClick={() => setSidebarOpen(false)}
                >
                  <NavIcon>
                    <Icon icon={item.icon} size="sm" />
                  </NavIcon>
                  {item.label}
                  {item.badge && <Badge>{item.badge}</Badge>}
                </NavItem>
              ))}
            </div>
          ))}
        </NavSection>

        <SidebarFooter>
          <UserInfo>
            <UserAvatar>{userInitial}</UserAvatar>
            <div>
              <UserName>{user.name || user.email}</UserName>
              <UserRole>{roleLabel}</UserRole>
            </div>
            <ThemeToggle />
          </UserInfo>
          <LogoutButton onClick={handleLogout}>
            <Icon icon={faSignOutAlt} size="sm" />
            خروج از حساب
          </LogoutButton>
        </SidebarFooter>
      </Sidebar>

      {/* Main Content */}
      <MainContent>
        <TopBar>
          <MobileMenuBtn onClick={() => setSidebarOpen(true)}>
            <Icon icon={faBars} />
          </MobileMenuBtn>
          <ThemeToggle />
        </TopBar>
        {children}
      </MainContent>
    </Layout>
  );
};