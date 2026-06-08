'use client';

import { useState } from 'react';
import styled from '@emotion/styled';
import { Icon } from '@/components/ui/Icon';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { useToast } from '@/components/ui/Toast';
import { updateUserRole, toggleUserActive } from '@/lib/api';
import { faSearch, faUser, faCheck, faTimes, faEdit } from '@fortawesome/free-solid-svg-icons';

const FiltersBar = styled.div`
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
`;

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
  background: ${p => p.$active ? '#ecfdf5' : '#fef2f2'};
  color: ${p => p.$active ? '#059669' : '#dc2626'};
`;

const RoleSelect = styled.select`
  padding: 6px 10px;
  border-radius: 6px;
  border: 1px solid ${p => p.theme.colors.border.light};
  font-family: inherit;
  font-size: 0.85rem;
  background: white;
`;

const roleLabels = {
  client: 'مشتری',
  accountant: 'حسابدار',
  stock_keeper: 'انباردار',
  courier: 'پیک',
  super_admin: 'ادمین کل',
};

export const UsersTable = ({ users }) => {
  const toast = useToast();
  const [search, setSearch] = useState('');

  const handleRoleChange = async (userId, newRole) => {
    const res = await updateUserRole(userId, newRole);
    if (res.success) {
      toast.success('نقش کاربر تغییر کرد');
      window.location.reload();
    } else {
      toast.error(res.error);
    }
  };

  const handleToggleActive = async (userId) => {
    const res = await toggleUserActive(userId);
    if (res.success) {
      toast.success('وضعیت کاربر تغییر کرد');
      window.location.reload();
    } else {
      toast.error(res.error);
    }
  };

  return (
    <>
      <FiltersBar>
        <Input
          placeholder="جستجوی کاربر..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          icon={faSearch}
        />
      </FiltersBar>

      <Table>
        <thead>
          <tr>
            <Th>کاربر</Th>
            <Th>ایمیل / موبایل</Th>
            <Th>نقش</Th>
            <Th>وضعیت</Th>
            <Th>تاریخ عضویت</Th>
            <Th>عملیات</Th>
          </tr>
        </thead>
        <tbody>
          {users.filter(u =>
            !search || u.email?.includes(search) || u.mobile?.includes(search) || u.full_name?.includes(search)
          ).map(user => (
            <tr key={user.id}>
              <Td>
                <div style={{ fontWeight: 600 }}>{user.full_name || user.email || user.mobile}</div>
              </Td>
              <Td>
                <div>{user.email}</div>
                {user.mobile && <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>{user.mobile}</div>}
              </Td>
              <Td>
                <RoleSelect
                  value={user.role}
                  onChange={(e) => handleRoleChange(user.id, e.target.value)}
                >
                  {Object.entries(roleLabels).map(([key, label]) => (
                    <option key={key} value={key}>{label}</option>
                  ))}
                </RoleSelect>
              </Td>
              <Td>
                <StatusBadge $active={user.is_active}>
                  <Icon icon={user.is_active ? faCheck : faTimes} size="xs" />
                  {user.is_active ? 'فعال' : 'غیرفعال'}
                </StatusBadge>
              </Td>
              <Td>{user.date_joined ? new Date(user.date_joined).toLocaleDateString('fa-IR') : '-'}</Td>
              <Td>
                <Button
                  variant={user.is_active ? 'danger' : 'primary'}
                  size="sm"
                  onClick={() => handleToggleActive(user.id)}
                >
                  {user.is_active ? 'غیرفعال‌سازی' : 'فعال‌سازی'}
                </Button>
              </Td>
            </tr>
          ))}
        </tbody>
      </Table>
    </>
  );
};