'use client';

import styled from '@emotion/styled';
import Link from 'next/link';
import { Icon } from '@/components/ui/Icon';
import { Button } from '@/components/ui/Button';
import {
  faTicketAlt, faHeadset, faQuestionCircle,
  faShieldAlt, faPlus, faArrowLeft, faClock, faCheckCircle,
  faTimesCircle
} from '@fortawesome/free-solid-svg-icons';

// ==================== Styled Components ====================

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
`;

const HubCard = styled(Link)`
  background: ${p => p.theme.colors.surface.card};
  border: 1px solid ${p => p.theme.colors.border.light};
  border-radius: ${p => p.theme.borderRadius.lg};
  padding: 28px 24px;
  text-decoration: none;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 12px;

  &:hover {
    transform: translateY(-4px);
    box-shadow: ${p => p.theme.shadows.lg};
    border-color: ${p => p.theme.colors.brand[400]};
  }
`;

const HubIcon = styled.div`
  width: 60px;
  height: 60px;
  border-radius: 16px;
  background: ${p => p.$bg || p.theme.colors.brand[50]};
  color: ${p => p.$color || p.theme.colors.brand[600]};
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
`;

const HubTitle = styled.h3`
  font-size: 1.1rem;
  font-weight: 700;
  color: ${p => p.theme.colors.text.primary};
`;

const HubDesc = styled.p`
  font-size: 0.85rem;
  color: ${p => p.theme.colors.text.muted};
  line-height: 1.6;
`;

const RecentTickets = styled.div`
  margin-top: 32px;
`;

const SectionHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
`;

const SectionTitle = styled.h2`
  font-size: 1.3rem;
  font-weight: 700;
`;

const TicketList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const TicketItem = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: ${p => p.theme.colors.surface.card};
  border: 1px solid ${p => p.theme.colors.border.light};
  border-radius: ${p => p.theme.borderRadius.md};
  transition: all 0.15s;

  &:hover {
    border-color: ${p => p.theme.colors.brand[300]};
    background: ${p => p.theme.colors.brand[50]}20;
  }
`;

const TicketStatusIcon = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: ${p => p.$bg};
  color: ${p => p.$color};
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
`;

const TicketInfo = styled.div`
  flex: 1;
  min-width: 0;
`;

const TicketSubject = styled.div`
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const TicketMeta = styled.div`
  font-size: 0.8rem;
  color: ${p => p.theme.colors.text.muted};
  display: flex;
  gap: 12px;
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 40px;
  color: ${p => p.theme.colors.text.muted};
`;

// ==================== Helpers ====================

const statusConfig = {
  open: { icon: faClock, bg: '#fef3c7', color: '#d97706' },
  in_progress: { icon: faHeadset, bg: '#dbeafe', color: '#2563eb' },
  waiting_customer: { icon: faClock, bg: '#e2e8f0', color: '#64748b' },
  resolved: { icon: faCheckCircle, bg: '#d1fae5', color: '#059669' },
  closed: { icon: faTimesCircle, bg: '#f1f5f9', color: '#94a3b8' },
};

// ==================== Component ====================

export const SupportHub = ({ user, recentTickets }) => {
  const isStaff = user?.role === 'super_admin' || user?.role === 'accountant';

  const hubCards = [
    {
      icon: faTicketAlt,
      title: 'تیکت‌های پشتیبانی',
      desc: 'مشاهده، ایجاد و پیگیری تیکت‌های پشتیبانی',
      href: '/dashboard/tickets',
      bg: '#ede9fe',
      color: '#7c3aed',
    },
    {
      icon: faHeadset,
      title: 'چت آنلاین',
      desc: 'گفتگوی مستقیم با کارشناسان پشتیبانی',
      href: '/dashboard/chat',
      bg: '#dbeafe',
      color: '#2563eb',
      show: isStaff,
    },
    {
      icon: faQuestionCircle,
      title: 'سوالات متداول',
      desc: 'مدیریت و مشاهده FAQ',
      href: '/dashboard/faq',
      bg: '#d1fae5',
      color: '#059669',
      show: isStaff,
    },
    {
      icon: faShieldAlt,
      title: 'گارانتی و وارانتی',
      desc: 'استعلام و مدیریت گارانتی محصولات',
      href: '/dashboard/warranty',
      bg: '#fee2e2',
      color: '#dc2626',
      show: isStaff,
    },
  ];

  return (
    <div>
      <Grid>
        {hubCards
          .filter(card => card.show !== false)
          .map((card, idx) => (
            <HubCard key={idx} href={card.href}>
              <HubIcon $bg={card.bg} $color={card.color}>
                <Icon icon={card.icon} size="lg" />
              </HubIcon>
              <HubTitle>{card.title}</HubTitle>
              <HubDesc>{card.desc}</HubDesc>
            </HubCard>
          ))}
      </Grid>

      <RecentTickets>
        <SectionHeader>
          <SectionTitle>📋 تیکت‌های اخیر</SectionTitle>
          <Link href="/dashboard/tickets/new">
            <Button variant="primary" size="sm" icon={faPlus}>
              تیکت جدید
            </Button>
          </Link>
        </SectionHeader>

        {recentTickets.length === 0 ? (
          <EmptyState>
            <Icon icon={faTicketAlt} size="2xl" />
            <p>هیچ تیکتی ثبت نشده است.</p>
          </EmptyState>
        ) : (
          <TicketList>
            {recentTickets.map(ticket => {
              const status = statusConfig[ticket.status] || statusConfig.open;
              return (
                <Link
                  key={ticket.id}
                  href={`/dashboard/tickets/${ticket.id}`}
                  style={{ textDecoration: 'none', color: 'inherit' }}
                >
                  <TicketItem>
                    <TicketStatusIcon $bg={status.bg} $color={status.color}>
                      <Icon icon={status.icon} size="sm" />
                    </TicketStatusIcon>
                    <TicketInfo>
                      <TicketSubject>{ticket.subject}</TicketSubject>
                      <TicketMeta>
                        <span>#{ticket.ticket_number}</span>
                        <span>{ticket.created_at_jalali || ticket.created_at}</span>
                        <span>{ticket.messages_count || 0} پیام</span>
                      </TicketMeta>
                    </TicketInfo>
                    <Icon icon={faArrowLeft} size="sm" style={{ color: '#94a3b8' }} />
                  </TicketItem>
                </Link>
              );
            })}
          </TicketList>
        )}
      </RecentTickets>
    </div>
  );
};