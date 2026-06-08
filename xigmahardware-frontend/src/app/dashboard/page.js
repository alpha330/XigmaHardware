import { getMe } from '@/lib/api';

export default async function DashboardHome() {
  const { data: user } = await getMe();
  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>👋 خوش آمدید، {user?.full_name || user?.email}</h1>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16 }}>
        <StatCard title="سفارشات" value={user?.orders_count || 0} />
        <StatCard title="موجودی کیف پول" value={`${user?.wallet_balance?.balance?.toLocaleString() || 0} تومان`} />
        <StatCard title="آدرس‌ها" value={user?.addresses_count || 0} />
        <StatCard title="تیکت‌ها" value={user?.tickets_count || 0} />
      </div>
    </div>
  );
}

const StatCard = ({ title, value }) => (
  <div style={{ padding: 20, background: 'white', borderRadius: 12, border: '1px solid #e2e8f0' }}>
    <div style={{ color: '#64748b', fontSize: '0.85rem' }}>{title}</div>
    <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>{value}</div>
  </div>
);