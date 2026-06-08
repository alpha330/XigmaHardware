// src/app/dashboard/support/page.js
import { getMyTickets } from '@/lib/api';
import { SupportHub } from '@/components/dashboard/SupportHub';
import { getUserFromCookies } from '@/lib/auth-actions';

export default async function SupportPage() {
  const user = await getUserFromCookies();
  const { data: ticketsData } = await getMyTickets();
  const recentTickets = ticketsData?.results?.slice(0, 5) || [];

  return (
    <div className="animate-fade-in-up">
      <h1 style={{ fontSize: '1.8rem', fontWeight: 700, marginBottom: 24 }}>
        🎧 مرکز پشتیبانی
      </h1>
      <SupportHub user={user} recentTickets={recentTickets} />
    </div>
  );
}