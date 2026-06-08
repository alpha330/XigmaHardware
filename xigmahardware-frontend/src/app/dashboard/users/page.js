// src/app/dashboard/users/page.js
import { getUsersList } from '@/lib/api';
import { UsersTable } from '@/components/dashboard/UsersTable';

export default async function UsersPage() {
  const { data } = await getUsersList();
  const users = data?.results || data || [];

  return (
    <div className="animate-fade-in-up">
      <h1 style={{ fontSize: '1.8rem', fontWeight: 700, marginBottom: 24 }}>👥 مدیریت کاربران</h1>
      <UsersTable users={users} />
    </div>
  );
}