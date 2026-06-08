// src/app/dashboard/layout.js
import { getUserFromCookies } from '@/lib/auth-actions';
import { DashboardShell } from '@/components/dashboard/DashboardShell';
import { redirect } from 'next/navigation';

export const metadata = {
  title: 'داشبورد | XigmaHardware',
};

export default async function DashboardLayout({ children }) {
  const user = await getUserFromCookies();

  if (!user) {
    redirect('/auth/login');
  }

  return <DashboardShell user={user}>{children}</DashboardShell>;
}