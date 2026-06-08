'use client';

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
  faMicrochip
} from '@fortawesome/free-solid-svg-icons';
import { useState } from 'react';

const Layout = styled.div`
  display: flex;
  min-height: 100vh;
  background: ${p => p.theme.colors.bg.secondary};
`;

const Sidebar = styled.aside`
  width: 260px;
  background: ${p => p.theme.colors.surface.card};
  border-left: 1px solid ${p => p.theme.colors.border.light};
  padding: 24px 16px;
  display: flex;
  flex-direction: column;
  position: fixed;
  right: 0;
  top: 0;
  bottom: 0;
  z-index: 100;
  transition: transform 0.3s;

  @media (max-width: 1024px) {
    transform: ${p => p.$open ? 'translateX(0)' : 'translateX(100%)'};
  }
`;

const SidebarHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  padding-bottom: 24px;
  border-bottom: 1px solid ${p => p.theme.colors.border.light};
  margin-bottom: 24px;
  font-weight: 800;
  font-size: 1.2rem;
  color: ${p => p.theme.colors.text.primary};
`;

const NavSection = styled.div`
  margin-bottom: 24px;
`;

const NavTitle = styled.p`
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: ${p => p.theme.colors.text.muted};
  margin-bottom: 8px;
  padding: 0 12px;
`;

const NavItem = styled(Link)`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: ${p => p.theme.borderRadius.md};
  color: ${p => p.$active ? p.theme.colors.brand[600] : p.theme.colors.text.secondary};
  background: ${p => p.$active ? p.theme.colors.brand[50] : 'transparent'};
  font-weight: ${p => p.$active ? 600 : 400};
  font-size: 0.9rem;
  text-decoration: none;
  transition: all 0.15s;
  margin-bottom: 2px;

  &:hover {
    background: ${p => p.theme.colors.brand[50]};
    color: ${p => p.theme.colors.brand[600]};
  }
`;

const MainContent = styled.main`
  flex: 1;
  margin-right: 260px;
  padding: 32px;
  @media (max-width: 1024px) { margin-right: 0; }
`;

const MobileToggle = styled.button`
  display: none;
  position: fixed;
  top: 16px;
  right: 16px;
  z-index: 110;
  width: 40px; height: 40px;
  border-radius: ${p => p.theme.borderRadius.md};
  border: 1px solid ${p => p.theme.colors.border.light};
  background: ${p => p.theme.colors.surface.card};
  cursor: pointer;
  @media (max-width: 1024px) { display: flex; align-items: center; justify-content: center; }
`;

// تعریف منوها بر اساس نقش
const menuConfig = {
  client: [
    { icon: faHome, label: 'پیشخوان', href: '/dashboard' },
    { icon: faFileInvoice, label: 'سفارشات', href: '/dashboard/orders' },
    { icon: faWallet, label: 'کیف پول', href: '/dashboard/wallet' },
    { icon: faMapMarkerAlt, label: 'آدرس‌ها', href: '/dashboard/addresses' },
    { icon: faHeart, label: 'علاقه‌مندی‌ها', href: '/dashboard/wishlist' },
    { icon: faStar, label: 'نظرات من', href: '/dashboard/reviews' },
    { icon: faTicketAlt, label: 'تیکت‌ها', href: '/dashboard/tickets' },
    { icon: faUser, label: 'پروفایل', href: '/dashboard/profile' },
  ],
  accountant: [
    { icon: faHome, label: 'پیشخوان', href: '/dashboard' },
    { icon: faFileInvoice, label: 'فاکتورها', href: '/dashboard/invoices' },
    { icon: faChartLine, label: 'تراکنش‌ها', href: '/dashboard/transactions' },
    { icon: faChartLine, label: 'گزارش‌ها', href: '/dashboard/reports' },
    { icon: faTags, label: 'تخفیف‌ها', href: '/dashboard/discounts' },
    { icon: faTicketAlt, label: 'تیکت‌ها', href: '/dashboard/tickets' },
    { icon: faQuestionCircle, label: 'FAQ', href: '/dashboard/faq' },
    { icon: faShieldAlt, label: 'گارانتی', href: '/dashboard/warranty' },
  ],
  stock_keeper: [
    { icon: faHome, label: 'پیشخوان', href: '/dashboard' },
    { icon: faWarehouse, label: 'انبارها', href: '/dashboard/warehouses' },
    { icon: faBoxes, label: 'موجودی', href: '/dashboard/inventory' },
    { icon: faTruck, label: 'محموله‌ها', href: '/dashboard/shipments' },
    { icon: faMotorcycle, label: 'پیک‌ها', href: '/dashboard/couriers' },
  ],
  courier: [
    { icon: faHome, label: 'پیشخوان', href: '/dashboard' },
    { icon: faTruck, label: 'محموله‌های من', href: '/dashboard/shipments' },
    { icon: faMotorcycle, label: 'وضعیت من', href: '/dashboard/couriers' },
  ],
  super_admin: [
    { icon: faHome, label: 'پیشخوان', href: '/dashboard' },
    { icon: faUsers, label: 'کاربران', href: '/dashboard/users' },
    { icon: faFileInvoice, label: 'فاکتورها', href: '/dashboard/invoices' },
    { icon: faChartLine, label: 'تراکنش‌ها', href: '/dashboard/transactions' },
    { icon: faChartLine, label: 'گزارش‌ها', href: '/dashboard/reports' },
    { icon: faWarehouse, label: 'انبارها', href: '/dashboard/warehouses' },
    { icon: faBoxes, label: 'موجودی', href: '/dashboard/inventory' },
    { icon: faTruck, label: 'محموله‌ها', href: '/dashboard/shipments' },
    { icon: faMotorcycle, label: 'پیک‌ها', href: '/dashboard/couriers' },
    { icon: faTicketAlt, label: 'تیکت‌ها', href: '/dashboard/tickets' },
    { icon: faHeadset, label: 'چت', href: '/dashboard/chat' },
    { icon: faQuestionCircle, label: 'FAQ', href: '/dashboard/faq' },
    { icon: faShieldAlt, label: 'گارانتی', href: '/dashboard/warranty' },
    { icon: faCreditCard, label: 'درگاه‌ها', href: '/dashboard/gateways' },
  ],
};

export const DashboardShell = ({ user, children }) => {
  const pathname = usePathname();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const menu = menuConfig[user.role] || menuConfig.client;

  const handleLogout = async () => {
    const { clearAuthCookies } = await import('@/lib/auth-actions');
    await clearAuthCookies();
    window.location.href = '/auth/login';
  };

  return (
    <Layout>
      <MobileToggle onClick={() => setSidebarOpen(!sidebarOpen)}>
        <Icon icon={sidebarOpen ? faTimes : faBars} />
      </MobileToggle>

      <Sidebar $open={sidebarOpen}>
        <SidebarHeader>
          <Icon icon={faMicrochip} size="lg" color="#8b5cf6" />
          XigmaHardware
        </SidebarHeader>

        <NavSection>
          <NavTitle>منو</NavTitle>
          {menu.map(item => (
            <NavItem key={item.href} href={item.href} $active={pathname === item.href}>
              <Icon icon={item.icon} size="sm" />
              {item.label}
            </NavItem>
          ))}
        </NavSection>

        <div style={{ marginTop: 'auto' }}>
          <div style={{ padding: '12px', borderTop: '1px solid #e2e8f0', fontSize: '0.85rem' }}>
            <div style={{ fontWeight: 600 }}>{user.name}</div>
            <div style={{ color: '#94a3b8' }}>{user.role}</div>
          </div>
          <NavItem href="#" onClick={handleLogout} style={{ color: '#ef4444' }}>
            <Icon icon={faSignOutAlt} size="sm" />
            خروج
          </NavItem>
        </div>
      </Sidebar>

      <MainContent onClick={() => setSidebarOpen(false)}>
        {children}
      </MainContent>
    </Layout>
  );
};