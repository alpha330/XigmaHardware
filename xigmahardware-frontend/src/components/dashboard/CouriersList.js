'use client';

import styled from '@emotion/styled';
import { Icon } from '@/components/ui/Icon';
import { Button } from '@/components/ui/Button';
import { useToast } from '@/components/ui/Toast';
import { updateCourierStatus } from '@/lib/api';
import { faMotorcycle, faCar, faTruck, faCheck, faTimes, faMapMarkerAlt, faPhone } from '@fortawesome/free-solid-svg-icons';

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
  background: ${p => p.theme.colors.surface.card};
  border: 1px solid ${p => p.theme.colors.border.light};
  border-radius: ${p => p.theme.borderRadius.lg};
  overflow: hidden;
`;

const Th = styled.th`
  text-align: right;
  padding: 14px 16px;
  background: ${p => p.theme.colors.bg.tertiary};
  font-size: 0.85rem;
  color: ${p => p.theme.colors.text.secondary};
  font-weight: 600;
  border-bottom: 1px solid ${p => p.theme.colors.border.light};
`;

const Td = styled.td`
  padding: 14px 16px;
  border-bottom: 1px solid ${p => p.theme.colors.border.light};
  font-size: 0.9rem;
`;

const StatusBadge = styled.span`
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 50px;
  font-size: 0.8rem;
  font-weight: 500;
  background: ${p => p.$bg};
  color: ${p => p.$color};
`;

const VehicleIcon = styled.span`
  font-size: 1.2rem;
  margin-left: 4px;
`;

const vehicleIcons = {
  motorcycle: faMotorcycle,
  car: faCar,
  pickup: faTruck,
  van: faTruck,
  truck: faTruck,
};

export const CouriersList = ({ couriers }) => {
  const toast = useToast();

  const handleToggleAvailable = async (id) => {
    const res = await updateCourierStatus(id);
    if (res.success) {
      toast.success('وضعیت پیک بروزرسانی شد');
      window.location.reload();
    } else {
      toast.error(res.error);
    }
  };

  if (couriers.length === 0) {
    return <p style={{ color: '#94a3b8' }}>هیچ پیکی ثبت نشده است.</p>;
  }

  return (
    <Table>
      <thead>
        <tr>
          <Th>نام</Th>
          <Th>نوع</Th>
          <Th>وسیله نقلیه</Th>
          <Th>وضعیت</Th>
          <Th>موفقیت</Th>
          <Th>موقعیت</Th>
          <Th>عملیات</Th>
        </tr>
      </thead>
      <tbody>
        {couriers.map(c => (
          <tr key={c.id}>
            <Td>
              <div style={{ fontWeight: 600 }}>{c.name}</div>
              <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                <Icon icon={faPhone} size="xs" /> {c.phone}
              </div>
            </Td>
            <Td>{c.courier_type_display?.label || c.courier_type}</Td>
            <Td>
              <VehicleIcon>
                <Icon icon={vehicleIcons[c.vehicle_type] || faMotorcycle} />
              </VehicleIcon>
              {c.vehicle_type_display?.label || c.vehicle_type}
            </Td>
            <Td>
              <StatusBadge
                $bg={c.is_available ? '#ecfdf5' : '#fef2f2'}
                $color={c.is_available ? '#059669' : '#dc2626'}
              >
                <Icon icon={c.is_available ? faCheck : faTimes} size="xs" />
                {c.is_available ? 'آماده' : 'مشغول'}
              </StatusBadge>
            </Td>
            <Td>
              <div style={{ fontWeight: 600, color: c.success_rate > 80 ? '#059669' : '#f59e0b' }}>
                {c.success_rate}%
              </div>
              <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                {c.successful_deliveries}/{c.total_deliveries}
              </div>
            </Td>
            <Td>
              {c.current_latitude ? (
                <a
                  href={`https://maps.google.com/?q=${c.current_latitude},${c.current_longitude}`}
                  target="_blank"
                  style={{ color: '#8b5cf6' }}
                >
                  <Icon icon={faMapMarkerAlt} /> مشاهده
                </a>
              ) : (
                <span style={{ color: '#94a3b8' }}>-</span>
              )}
            </Td>
            <Td>
              <Button
                variant={c.is_available ? 'outline' : 'primary'}
                size="sm"
                onClick={() => handleToggleAvailable(c.id)}
              >
                {c.is_available ? 'غیرفعال' : 'فعال'}
              </Button>
            </Td>
          </tr>
        ))}
      </tbody>
    </Table>
  );
};