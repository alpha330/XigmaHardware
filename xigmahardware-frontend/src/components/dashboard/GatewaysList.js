'use client';

import styled from '@emotion/styled';
import { Icon } from '@/components/ui/Icon';
import { Button } from '@/components/ui/Button';
import { useToast } from '@/components/ui/Toast';
import { toggleGatewayActive, setGatewayDefault } from '@/lib/api';
import { faCreditCard, faCheck, faTimes, faStar, faEdit } from '@fortawesome/free-solid-svg-icons';

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
`;

const GatewayCard = styled.div`
  padding: 24px;
  background: ${p => p.theme.colors.surface.card};
  border: 1px solid ${p => p.$default ? p.theme.colors.brand[400] : p.theme.colors.border.light};
  border-radius: ${p => p.theme.borderRadius.lg};
  transition: all 0.2s;
  position: relative;

  &:hover { box-shadow: ${p => p.theme.shadows.md}; }
`;

const GatewayIcon = styled.div`
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: ${p => p.theme.colors.brand[50]};
  color: ${p => p.theme.colors.brand[600]};
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  margin-bottom: 12px;
`;

const GatewayName = styled.h3`
  font-weight: 700;
  margin-bottom: 4px;
`;

const GatewayType = styled.div`
  font-size: 0.85rem;
  color: ${p => p.theme.colors.text.muted};
  margin-bottom: 12px;
`;

const StatusBadge = styled.span`
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 50px;
  font-size: 0.8rem;
  font-weight: 500;
  background: ${p => p.$active ? '#ecfdf5' : '#fef2f2'};
  color: ${p => p.$active ? '#059669' : '#dc2626'};
`;

const DefaultBadge = styled.span`
  position: absolute;
  top: 12px;
  left: 12px;
  background: ${p => p.theme.colors.brand[500]};
  color: white;
  padding: 2px 10px;
  border-radius: 50px;
  font-size: 0.7rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
`;

const Actions = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 16px;
`;

const gatewayIcons = {
  payping: faCreditCard,
  zarinpal: faCreditCard,
  crypto: faCreditCard,
  card_to_card: faCreditCard,
};

export const GatewaysList = ({ gateways }) => {
  const toast = useToast();

  const handleToggleActive = async (id) => {
    const res = await toggleGatewayActive(id);
    if (res.success) {
      toast.success('وضعیت درگاه تغییر کرد');
      window.location.reload();
    } else {
      toast.error(res.error);
    }
  };

  const handleSetDefault = async (id) => {
    const res = await setGatewayDefault(id);
    if (res.success) {
      toast.success('درگاه پیش‌فرض تنظیم شد');
      window.location.reload();
    } else {
      toast.error(res.error);
    }
  };

  if (gateways.length === 0) {
    return <p style={{ color: '#94a3b8' }}>هیچ درگاهی ثبت نشده است.</p>;
  }

  return (
    <Grid>
      {gateways.map(gw => (
        <GatewayCard key={gw.id} $default={gw.is_default}>
          {gw.is_default && (
            <DefaultBadge><Icon icon={faStar} size="xs" /> پیش‌فرض</DefaultBadge>
          )}
          <GatewayIcon>
            <Icon icon={gatewayIcons[gw.gateway_type] || faCreditCard} />
          </GatewayIcon>
          <GatewayName>{gw.name}</GatewayName>
          <GatewayType>{gw.type_display?.label || gw.gateway_type}</GatewayType>
          <StatusBadge $active={gw.is_active}>
            <Icon icon={gw.is_active ? faCheck : faTimes} size="xs" />
            {gw.is_active ? 'فعال' : 'غیرفعال'}
          </StatusBadge>
          <div style={{ marginTop: 8, fontSize: '0.85rem', color: '#94a3b8' }}>
            Mode: {gw.mode_display?.label || gw.mode}
          </div>
          <Actions>
            <Button variant="outline" size="sm" icon={faEdit}
              onClick={() => window.location.href = `/dashboard/gateways/${gw.id}/edit`}>
              ویرایش
            </Button>
            <Button
              variant={gw.is_active ? 'danger' : 'primary'}
              size="sm"
              onClick={() => handleToggleActive(gw.id)}
            >
              {gw.is_active ? 'غیرفعال' : 'فعال'}
            </Button>
            {!gw.is_default && (
              <Button variant="ghost" size="sm" icon={faStar} onClick={() => handleSetDefault(gw.id)}>
                پیش‌فرض
              </Button>
            )}
          </Actions>
        </GatewayCard>
      ))}
    </Grid>
  );
};